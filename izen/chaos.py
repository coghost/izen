# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '12/09/2017 5:36 PM'
__description__ = '''
'''
import base64
import hashlib
import os
import sys
import platform

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as pkcs

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from izen import helper
from izen import dec

"""
base64
md5
sha1
aes : {
'aes128': 16,
}
rsa
"""


class Chaos(object):
    """
    加密混淆
    """

    def __init__(self):
        self.aes_mode = AES.MODE_CBC
        self.bs = AES.block_size

    @dec.catch(True, TypeError)
    def encrypt(self, plain, algorithm='md5'):
        """ 简单封装系统加密

        :param plain: 待加密内容
        :type plain:  ``str/bytes``
        :param algorithm: 加密算法
        :type algorithm: str
        :return:
        :rtype:
        """
        plain = helper.to_bytes(plain)
        return getattr(hashlib, algorithm)(plain).hexdigest()

    def aes_obj(self, sec_key, encrypt_sec_key=True):
        """
            生成aes加密所需要的 ``key, iv``

        .. warning:: 每个AES.new对象, 只能使用一次

        :param sec_key:
        :type sec_key: str
        :param encrypt_sec_key: ``如果为true, 则md5加密 sec_key, 生成 key,iv, 否则直接使用 sec_key, 来作为key,iv``
        :type encrypt_sec_key:  bool
        :return:
        :rtype:
        """
        # 使用 md5加密 key, 获取32个长度, 拆分为两个16长度作为 AES的 key, iv
        p = self.encrypt(sec_key) if encrypt_sec_key else sec_key
        key, iv = p[:self.bs], p[16:]

        return AES.new(key, self.aes_mode, iv)

    def aes_encrypt(self, plain, sec_key, enable_b64=True):
        """
            使用 ``aes`` 加密数据, 并由 ``base64编码`` 加密后的数据

        - ``sec_key`` 加密 ``msg``, 最后选择 ``是否由base64编码数据``
        - msg长度为16位数, 不足则补 'ascii \\0'

        .. warning::
             msg长度为16位数, 不足则补 'ascii \\0'

        :param plain:
        :type plain: str
        :param sec_key:
        :type sec_key:  str
        :param enable_b64:
        :type enable_b64: bool
        :return:
        :rtype:
        """
        plain = helper.to_str(plain)
        sec_key = helper.to_str(sec_key)
        # 如果msg长度不为16倍数, 需要补位 '\0'
        plain += '\0' * (self.bs - len(plain) % self.bs)
        # 使用生成的 key, iv 加密
        plain = helper.to_bytes(plain)
        cipher = self.aes_obj(sec_key).encrypt(plain)
        # 是否返回 base64 编码数据
        cip = base64.b64encode(cipher) if enable_b64 else cipher
        return helper.to_str(cip)

    def aes_decrypt(self, cipher, sec_key, enable_b64=True):
        """
            由 ``base64解码数据``, 然后再使用 ``aes`` 解密数据

        - 使用 ``sec_key`` 解密由 ``base64解码后的cipher`` 数据
        - 先base64 decode, 再解密, 最后移除补位值 'ascii \\0'

        :param cipher:
        :type cipher: str
        :param sec_key:
        :type sec_key: str
        :param enable_b64:
        :type enable_b64: bool
        :return:
        :rtype:
        """
        cipher = base64.b64decode(cipher) if enable_b64 else cipher

        plain_ = self.aes_obj(sec_key).decrypt(cipher)
        return helper.to_str(plain_).rstrip('\0')


class RsaPub(Chaos):
    """
        公钥:用于客户端加密上传数据, 与验证服务器签名

    """

    def __init__(self, key_file):
        Chaos.__init__(self)
        # super(RsaPub, self).__init__()
        self.key_file = key_file

    def rsa_base64_encrypt(self, plain, b64=True):
        """
            使用公钥加密 ``可见数据``

        - 由于rsa公钥加密相对耗时, 多用来 ``加密数据量小`` 的数据

        .. note::
            1. 使用aes加密数据
            2. 然后rsa用来加密aes加密数据时使用的key

        :param plain:
        :type plain:
        :param b64:
        :type b64:
        :return:
        :rtype:
        """
        with open(self.key_file) as fp:
            key_ = RSA.importKey(fp.read())
            plain = helper.to_bytes(plain)
            cipher = PKCS1_v1_5.new(key_).encrypt(plain)
            cip = base64.b64encode(cipher) if b64 else cipher
            return helper.to_str(cip)

    def rsa_check_base64_sign_str(self, cipher, sign, b64=True):
        """
            验证服务端数据 ``rsa`` 签名

        """
        with open(self.key_file) as fp:
            key_ = RSA.importKey(fp.read())
            v = pkcs.new(key_)
            sign = base64.b64decode(sign) if b64 else sign
            cipher = helper.to_bytes(cipher)
            # if hasattr(cipher, 'encode'):
            #     cipher = cipher.encode('utf-8')
            return v.verify(SHA.new(cipher), sign)


class RsaPriv(Chaos):
    """
        私钥:用于服务器端签名数据, 与解密客户端数据

    """

    def __init__(self, key_file):
        Chaos.__init__(self)
        # super(RsaPriv, self).__init__()
        self.key_file = key_file

    def rsa_base64_decrypt(self, cipher, b64=True):
        """
            先base64 解码 再rsa 解密数据
        """
        with open(self.key_file) as fp:
            key_ = RSA.importKey(fp.read())
            _cip = PKCS1_v1_5.new(key_)
            cipher = base64.b64decode(cipher) if b64 else cipher
            plain = _cip.decrypt(cipher, Random.new().read(15 + SHA.digest_size))
            return helper.to_str(plain)

    def rsa_base64_sign_str(self, plain, b64=True):
        """
            对 msg rsa 签名, 然后使用 base64 encode 编码数据

        """
        with open(self.key_file) as fp:
            key_ = RSA.importKey(fp.read())
            # h = SHA.new(plain if sys.version_info < (3, 0) else plain.encode('utf-8'))
            plain = helper.to_bytes(plain)
            # if hasattr(plain, 'encode'):
            #     plain = plain.encode()
            h = SHA.new(plain)
            cipher = pkcs.new(key_).sign(h)
            cip = base64.b64encode(cipher) if b64 else cipher
            return helper.to_str(cip)


if __name__ == '__main__':
    ca = Chaos()
    # test of catch
    print(ca.encrypt('hello world', 'md6'))
    print('hi')
