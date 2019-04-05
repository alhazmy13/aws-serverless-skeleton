import base64
import datetime
import json
import sys
import time

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import get_credentials
from botocore.endpoint import BotocoreHTTPSession
from botocore.session import Session
from src.common.encoder import StreamTypeDeserializer
from src.common.exceptions import ESException
from src.common.log import get_logger


if sys.version_info < (3, 0):
    import urllib
    import urlparse
else:
    import urllib.request as urllib
    import urllib.parse as urlparse


class DynamoToEsService(object):
    def __init__(self, event, es_endpoint, region):

        # The following parameters are required to configure the ES cluster
        self.es_endpoint = es_endpoint
        # The following parameters can be optionally customized
        self.event = event
        # Python formatter to generate index name from the DynamoDB table name
        self.doc_table_format = '{}'
        # Python formatter to generate type name from the DynamoDB table name
        self.doc_type_format = '{}_type'
        # If not set, use the runtime lambda region
        self.es_region = region
        # Max number of retries for exponential backoff
        self.es_max_retries = 3

    def post_to_es(self, payload):
        """
        High-level POST data to Amazon Elasticsearch Service with exponential backoff
        according to suggested algorithm:
        http://docs.aws.amazon.com/general/latest/gr/api-retries.html
        :param payload:
        :return:
        """

        # Get aws_region and credentials to post signed URL to ES
        es_region = self.es_region
        session = Session({'region': es_region})
        creds = get_credentials(session)
        es_url = urlparse.urlparse(self.es_endpoint)
        es_endpoint = es_url.netloc or es_url.path  # Extract the domain name in ES_ENDPOINT

        # Post data with exponential backoff
        retries = 0
        while retries < self.es_max_retries:
            if retries > 0:
                seconds = (2 ** retries) * .1
                time.sleep(seconds)

            try:
                es_ret_str = self.post_data_to_es(payload, es_region, creds, es_endpoint, '/_bulk')
                es_ret = json.loads(es_ret_str)

                if es_ret['errors']:
                    get_logger().error('ES post unsuccessful, errors present, took=%sms',
                                       es_ret['took'])
                    # Filter errors
                    es_errors = [item for item in es_ret['items'] if item.get('index').get('error')]
                    get_logger().error('List of items with errors: %s', json.dumps(es_errors))
                else:
                    get_logger().info('ES post successful, took=%sms', es_ret['took'])
                break  # Sending to ES was ok, break retry loop
            except ESException as e:
                if (e.status_code >= 500) and (e.status_code <= 599):
                    retries += 1  # Candidate for retry
                else:
                    raise  # Stop retrying, re-raise exception

    @staticmethod
    def get_table_name_from_arn(arn):
        """
        Extracts the DynamoDB table from an ARN
        ex: arn:aws:dynamodb:REGION:USER:table/table-name/stream/2015-11-13T09:23:17.104
        should return 'table-name'
        :param arn:
        :return:
        """
        return arn.split(':')[5].split('/')[1]

    @staticmethod
    def compute_doc_index(keys_raw, deserializer):
        """
        Compute a compound doc index from the key(s) of the object in
        lexicographic order: "k1=key_val1|k2=key_val2"
        :param deserializer:
        :param keys_raw:
        :return:
        """
        index = []
        for key in sorted(keys_raw):
            index.append('{}={}'.format(key, deserializer.deserialize(keys_raw[key])))
        return '|'.join(index)

    def execute(self):
        records = self.event['Records']
        now = datetime.datetime.utcnow()

        ddb_deserializer = StreamTypeDeserializer()
        es_actions = []  # Items to be added/updated/removed from ES - for bulk API
        cnt_insert = cnt_modify = cnt_remove = 0
        for record in records:
            # Handle both native DynamoDB Streams or Streams data from Kinesis (for manual replay)
            if record.get('eventSource') == 'aws:dynamodb':
                ddb = record['dynamodb']
                ddb_table_name = self.get_table_name_from_arn(record['eventSourceARN'])
                doc_seq = ddb['SequenceNumber']
            elif record.get('eventSource') == 'aws:kinesis':
                ddb = json.loads(base64.b64decode(record['kinesis']['data']))
                ddb_table_name = ddb['SourceTable']
                doc_seq = record['kinesis']['sequenceNumber']
            else:
                get_logger().error('Ignoring non-DynamoDB event sources: %s',
                                   record.get('eventSource'))
                continue

            # Compute DynamoDB table, type and index for item
            doc_table = self.doc_type_format.format(ddb_table_name.lower())  # Use formatter
            doc_type = self.doc_type_format.format(ddb_table_name.lower())  # Use formatter
            doc_index = self.compute_doc_index(ddb['Keys'], ddb_deserializer)

            # Dispatch according to event TYPE
            event_name = record['eventName'].upper()  # INSERT, MODIFY, REMOVE

            # Treat events from a Kinesis stream as INSERTs
            if event_name == 'AWS:KINESIS:RECORD':
                event_name = 'INSERT'

            # Update counters
            if event_name == 'INSERT':
                cnt_insert += 1
            elif event_name == 'MODIFY':
                cnt_modify += 1
            elif event_name == 'REMOVE':
                cnt_remove += 1
            else:
                get_logger().warning('Unsupported event_name: %s', event_name)

            # If DynamoDB INSERT or MODIFY, send 'index' to ES
            if (event_name == 'INSERT') or (event_name == 'MODIFY'):
                if 'NewImage' not in ddb:
                    get_logger().warning('Cannot process stream if it does not contain NewImage')
                    continue
                # Deserialize DynamoDB type to Python types
                doc_fields = ddb_deserializer.deserialize({'M': ddb['NewImage']})
                # Add metadata
                doc_fields['@timestamp'] = now.isoformat()
                doc_fields['@SequenceNumber'] = doc_seq

                # Generate JSON payload
                doc_json = json.dumps(doc_fields)

                # Generate ES payload for item
                action = {'index': {'_index': doc_table, '_type': doc_type, '_id': doc_index}}
                es_actions.append(json.dumps(action))  # Action line with 'index' directive
                es_actions.append(doc_json)  # Payload line

            # If DynamoDB REMOVE, send 'delete' to ES
            elif event_name == 'REMOVE':
                action = {'delete': {'_index': doc_table, '_type': doc_type, '_id': doc_index}}
                es_actions.append(json.dumps(action))

        # Prepare bulk payload
        es_actions.append('')  # Add one empty line to force final \n
        es_payload = '\n'.join(es_actions)

        self.post_to_es(es_payload)  # Post to ES with exponential backoff

    @staticmethod
    def post_data_to_es(payload, region, creds, host, path, method='POST', proto='https://'):
        '''Post data to ES endpoint with SigV4 signed http headers'''
        """
        Low-level POST data to Amazon Elasticsearch Service generating a Sigv4 signed request

        :param payload:
        :param region:
        :param creds:
        :param host:
        :param path:
        :param method:
        :param proto:
        :return:
        """
        req = AWSRequest(method=method,
                         url=proto + host + urllib.quote(path),
                         data=payload,
                         headers={'Host': host})
        SigV4Auth(creds, 'es', region).add_auth(req)
        http_session = BotocoreHTTPSession()
        res = http_session.send(req.prepare())
        if 200 <= res.status_code <= 299:
            return res._content
        else:
            raise ESException(res.status_code, res._content)
