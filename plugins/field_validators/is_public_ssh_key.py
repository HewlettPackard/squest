import base64
import binascii
import struct

# For testing
try:
    from django.core.exceptions import ValidationError as UIValidationError
    from rest_framework.serializers import ValidationError as APIValidationError
except ImportError:
    pass

ERROR_MESSAGE = "Is not a valid public ssh key"

def is_public_ssh_key(ssh_key):
    array = ssh_key.split()
    # Each rsa-ssh key has 3 different strings in it, first one being
    # type_of_key second one being keystring third one being username.
    if len(array) not in [2, 3]:
        return False
    type_of_key = array[0]
    ssh_key_str = array[1]

    # must have only valid rsa-ssh key characters ie binascii characters
    try:
        data = base64.decodebytes(bytes(ssh_key_str, 'utf-8'))
    except binascii.Error:
        return False
    a = 4
    # unpack the contents of ssh_key, from ssh_key[:4] , it must be equal to 7 , property of ssh key .
    try:
        str_len = struct.unpack('>I', data[:a])[0]
    except struct.error:
        return False
    # ssh_key[4:11] must have string which matches with the type_of_key , another ssh key property.
    print(str_len)
    if data[a:a + str_len].decode(encoding='utf-8') == type_of_key:
        return True
    else:
        return False


def validate_api(value):
    if not is_public_ssh_key(value):
        raise APIValidationError(ERROR_MESSAGE)


def validate_ui(value):
    if not is_public_ssh_key(value):
        raise UIValidationError(ERROR_MESSAGE)
