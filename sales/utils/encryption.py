import hashlib

def encrypt(value):
    """
    MD5加密
    :param value: 需要被加密的数据
    :return: 加密后的值
    """
    salt = 'username'.encode('utf-8')
    md5_value = hashlib.md5(salt)
    md5_value.update(value.encode('utf-8'))
    return md5_value.hexdigest()