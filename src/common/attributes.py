import base64

import boto3
from pynamodb.attributes import Attribute
from pynamodb.constants import STRING


class EncryptedAttribute(Attribute):
    """
    A custom model attribute
    """

    # This tells PynamoDB that the attribute is stored in DynamoDB as a string
    # attribute
    attr_type = STRING

    def __init__(self,
                 region=None,
                 kms_key=None):
        super(EncryptedAttribute, self).__init__()
        if region is None and kms_key is None:
            self.region = None
            self.kms_key = None
        else:
            self.kms_key = kms_key
            self.region = region

    def serialize(self, value):
        """
        encrypt the value from string to encrypted blob
        :param value:
        :return: encrypted value only if region and kms key wasn't None
        """
        #
        if self.kms_key is not None and self.region is not None:
            kms = boto3.client('kms', self.region)
            stuff = kms.encrypt(KeyId=self.kms_key, Plaintext=value)
            binary_encrypted = stuff.get('CiphertextBlob')
            encrypted_value = base64.b64encode(binary_encrypted)
            return encrypted_value.decode()
        return value

    def deserialize(self, value):
        """
        decrypt the value
        :param value: attribute value
        :return: decrypted value only if region and kms key wasn't None
        """
        if self.kms_key is not None and self.region is not None:
            kms = boto3.client('kms', self.region)
            binary_data = base64.b64decode(value)
            meta = kms.decrypt(CiphertextBlob=binary_data)
            plaintext = meta.get('Plaintext')
            return plaintext.decode()
        return value
