from v2.nacos.common.nacos_exception import NacosException, INVALID_PARAM
from v2.nacos.config.encryption.abstract_encryption_plugin_service import AbstractEncryptionPluginService
from v2.nacos.config.model.config_param import HandlerParam
from v2.nacos.utils import aes_util, encode_util


class EncryptionPluginService(AbstractEncryptionPluginService):
    def __init__(self):
        self.ALGORITHM = 'cipher-aes'
        self.content_key = self.generate_key()
        self.the_key_of_content_key = self.generate_key()

    def param_check(self, handler_param: HandlerParam):
        if len(handler_param.plain_data_key) == 0:
            raise NacosException(INVALID_PARAM, "empty plain_data_key error")
        if len(handler_param.content) == 0:
            raise NacosException(INVALID_PARAM, "encrypt empty content error")

    def generate_key(self, length: int = 16):
        return encode_util.urlsafe_b64encode(
            aes_util.get_random_bytes_from_crypto(length))

    def encrypt(self, handler_param: HandlerParam):
        self.param_check(handler_param)
        encrypted_bytes = aes_util.encrypt_to_bytes(
            encode_util.decode_string_to_utf8_bytes(handler_param.plain_data_key),
            encode_util.decode_string_to_utf8_bytes(handler_param.content))
        handler_param.content = encode_util.encode_base64(encrypted_bytes)

    def decrypt(self, handler_param: HandlerParam):
        self.param_check(handler_param)
        decrypted_bytes = aes_util.decrypt_to_bytes(
            encode_util.decode_string_to_utf8_bytes(handler_param.plain_data_key),
            encode_util.decode_base64(handler_param.content))
        handler_param.content = encode_util.encode_utf8_bytes_to_string(decrypted_bytes)

    def generate_secret_key(self, handler_param: HandlerParam):
        handler_param.plain_data_key = self.content_key

    def algorithm_name(self):
        return self.ALGORITHM

    def encrypt_secret_key(self, handler_param: HandlerParam):
        if len(handler_param.plain_data_key) == 0:
            raise NacosException(INVALID_PARAM, "empty plain_data_key error")
        encrypted_bytes = aes_util.encrypt_to_bytes(
            encode_util.decode_string_to_utf8_bytes(self.the_key_of_content_key),
            encode_util.decode_string_to_utf8_bytes(handler_param.plain_data_key))
        encrypted_data_key = encode_util.encode_base64(encrypted_bytes)
        handler_param.encrypted_data_key = encrypted_data_key

    def decrypt_secret_key(self, handler_param: HandlerParam):
        if len(handler_param.encrypted_data_key) == 0:
            raise NacosException(INVALID_PARAM, "empty encrypted data key error")
        decrypted_bytes = aes_util.decrypt_to_bytes(
            encode_util.decode_string_to_utf8_bytes(self.the_key_of_content_key),
            encode_util.decode_base64(handler_param.encrypted_data_key))
        decrypted_data_key = encode_util.encode_utf8_bytes_to_string(decrypted_bytes)
        handler_param.plain_data_key = decrypted_data_key
