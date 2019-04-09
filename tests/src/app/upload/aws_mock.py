from unittest.mock import MagicMock

import boto3
from moto import mock_s3

# `create_key` response
create_resp = {...}

# `generate_data_key` response
generate_resp = {...}

# `decrypt` response
decrypt_resp = {...}

# `generate_presigned_url` response
generate_presigned_url_resp = "random url"


def client(*args, **kwargs):
    if args[0] == 's3':
        s3_mock = mock_s3()
        s3_mock.start()
        mock_client = boto3.client(*args, **kwargs)
        mock_client.generate_presigned_url = MagicMock(return_value=generate_presigned_url_resp)

    else:
        mock_client = boto3.client(*args, **kwargs)

        if args[0] == 'kms':
            mock_client.create_key = MagicMock(return_value=create_resp)
            mock_client.generate_data_key = MagicMock(return_value=generate_resp)
            mock_client.decrypt = MagicMock(return_value=decrypt_resp)

    return mock_client
