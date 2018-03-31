#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

__author__ = 'lfp <imanux@sina.com>'
__date__ = '2/19/16'
__modified__ = '2/19/16'
__version__ = '0.0.1'
__description__ = '''
'''

import json
import os
import sys
import unittest

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)

if sys.version_info[0] < 3:
    import imp

    imp.reload(sys)
    sys.setdefaultencoding('utf-8')
else:
    from importlib import reload

    reload(sys)

from izen import chaos
from izen.chaos import Chaos, RsaPub, RsaPriv

pub_key = os.path.join(app_root, 'tests/pub_test.key')
priv_key = os.path.join(app_root, 'tests/priv_test.key')

# 签名的长度
LEN_B64RSA_SIGN = 172
skip_enc = False


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.ca = Chaos()
        self.pub = RsaPub(pub_key)
        self.priv = RsaPriv(priv_key)

    def tearDown(self):
        self.ca = None
        self.pub = None
        self.priv = None

    @unittest.skipIf(skip_enc, 'enc test is: {}'.format(skip_enc))
    def test_encrypt(self):
        txt = 'hello world'
        sec = '5eb63bbbe01eeed093cb22bb8f5acdc3'
        ca = chaos.Chaos()
        self.assertEqual(ca.encrypt(txt), sec)

    @unittest.skipIf(skip_enc, 'enc test is: {}'.format(skip_enc))
    def test_aes_enc_dec(self):
        dat = 'just a try'
        key_ = 'whoami'

        cip = self.ca.aes_encrypt(dat, key_)
        pln = self.ca.aes_decrypt(cip, key_)
        self.assertEqual(pln, dat)

    @unittest.skipIf(skip_enc, 'enc test is: {}'.format(skip_enc))
    def test_rsa_enc_dec(self):
        """rsa_base64_encrypt 加密的字符, 应该被rsa_base64_decrypt 解密"""
        dat = 'just a try'
        r = self.pub.rsa_base64_encrypt(dat)
        r = self.priv.rsa_base64_decrypt(r)
        self.assertEqual(r, dat)

    @unittest.skipIf(skip_enc, 'enc test is: {}'.format(skip_enc))
    def test_rsa_sign(self):
        # 待加密字符
        msg = 'this is a test'
        # 简单使用 md5 加密
        msg = self.ca.encrypt(msg)
        # 将签名附加在加密数据后
        msg += self.priv.rsa_base64_sign_str(msg)

        # 对加密数据验证签名
        _p = self.pub.rsa_check_base64_sign_str(msg[:-LEN_B64RSA_SIGN], msg[-LEN_B64RSA_SIGN:])
        self.assertTrue(_p)

    @unittest.skipIf(skip_enc, 'enc test is: {}'.format(skip_enc))
    def test_aes_rsa(self):
        """ aes 加密数据, rsa 对 aes 密钥签名, 并附加在数据之后 """
        key_ = 'whoami'
        dat = 'just a try'
        cip = self.ca.aes_encrypt(dat, key_)
        cip += self.priv.rsa_base64_sign_str(cip)

        sg = self.pub.rsa_check_base64_sign_str(cip[:-LEN_B64RSA_SIGN], cip[-LEN_B64RSA_SIGN:])
        self.assertTrue(sg)

        rs = self.ca.aes_decrypt(cip[:-LEN_B64RSA_SIGN], key_)
        self.assertEqual(dat, rs)


if __name__ == '__main__':
    unittest.main()
