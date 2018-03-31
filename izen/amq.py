# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '13/11/2017 3:14 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import socket
import time
import uuid
import random

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt_client
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
from logzero import logger as log

"""topic 通信"""

'''topic encapsulation'''


class Topic(object):
    """
        初始化 ``topic`` 连接的配置

    .. code:: python

        # 配置文件需要包含如下字段
        conf = {
            "hostname": "127.0.0.1",
            "port": 1883,
            "username": "",
            "password": ""
        }

    """

    def __init__(self, conf=None):
        conf = conf if conf else {}
        self.conf = {
            'hostname': conf.get('hostname', 'localhost'),
            'port': conf.get('port', 1883),
            'auth': {
                'username': conf.get('username', 'admin'),
                'password': conf.get('password', 'admin'),
            }
        }

    def run(self, handler=None):
        pass


class Publisher(Topic):
    """
        简单的, ``单次发布消息`` 到云端队列, 不需要保持连接

    """

    def run(self, dat=None):
        """
            发布消息

        - 样例:

        .. code:: python

            t = {
                'hostname': '192.168.1.2',
                'port': 1883,
                'username': 'admin',
                'password': 'admin',
            }
            Publisher(t).run({'payload': json.dumps(t)}) if pub else TopicConsumer(t).run()

        :param dat:
        :type dat:
        :return:
        :rtype:
        """
        conf = self.conf
        dat = dat if dat else {}
        publish.single(topic=dat.get('topic', 'test_topic'),
                       payload=dat.get('payload', 'just a test topic payload'),
                       qos=dat.get('qos', 0),
                       retain=dat.get('retain', False),
                       hostname=conf['hostname'],
                       port=conf['port'],
                       auth=conf['auth'])


class TopicConsumer(Topic):
    """
        ``topic`` 消费

    .. code:: python

        def topic_test(pub=True):
            t = {
                'hostname': '192.168.1.2',
                'port': 1883,
                'username': 'admin',
                'password': 'admin',
            }
            Publisher(t).run({'payload': json.dumps(t)}) if pub else TopicConsumer(t).run()

    """

    def run(self, handler=None):
        while True:
            try:
                conf = self.conf
                handler = handler if handler else {}
                client_ = mqtt_client.Client(client_id=getattr(handler, 'cid', hex(uuid.getnode())),
                                             clean_session=getattr(handler, 'clean_session', True))
                client_.username_pw_set(conf['auth']['username'], conf['auth']['password'])
                rs = client_.connect(conf['hostname'], conf['port'])
                client_.on_log = getattr(handler, 'on_log', _on_log)
                client_.on_connect = getattr(handler, 'on_connect', _on_connect)
                client_.on_message = getattr(handler, 'on_message', _on_message)
                client_.on_disconnect = getattr(handler, 'on_disconnect', _on_disconnect)
                client_.loop_forever(timeout=1.0)
            except socket.error as err:
                # 如果无法正常连接到指定服务器, 则以2s周期, 进行尝试
                log.error('socket error: {}'.format(err))
                time.sleep(2)
                # 增加一个随机数
                time.sleep(random.random())
                continue
            except Exception as ee:
                log.error('topic error: {}'.format(ee))
            break


def push_to_topic(dst, dat, qos=0, retain=False, cfgs=None):
    """
    - 发送数据 dat 到目的地 dst

    :param cfgs:
    :type cfgs:
    :param dst:
    :type dst:
    :param dat:
    :type dat:
    :param qos:
    :type qos:
    :param retain:
    :type retain:
    """
    cfg_amqt = {
        'hostname': cfgs['hostname'],
        'port': cfgs['port'],
        'username': cfgs['username'],
        'password': cfgs['password'],
    }

    msg = {
        'topic': dst,
        'payload': dat,
        'qos': qos,
        'retain': retain,
    }
    try:
        Publisher(cfg_amqt).run(msg)
        return True
    except Exception as err:
        log.error('push to amqt: {}'.format(err))
        return False


''' topic default functions '''


def _on_log(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        head = 'INFO'
    elif level == MQTT_LOG_NOTICE:
        head = 'NOTICE'
    elif level == MQTT_LOG_WARNING:
        head = 'WARN'
    elif level == MQTT_LOG_ERR:
        head = 'ERR'
    elif level == MQTT_LOG_DEBUG:
        head = 'DEBUG'
    else:
        head = level
    log.info('%s: %s' % (head, buf))


def _on_connect(client, userdata, flags, rc):
    """默认 topic 连接处理方法"""
    log.debug('[MQTT] Connected with result code ' + str(rc))
    client.subscribe('test_topic', qos=2)


def _on_message(client, userdata, msg):
    """默认消费队列"""
    log.debug(msg.payload)


def _on_disconnect(client, userdata, rc):
    if rc != 0:
        log.debug('Unexpected disconnection %s' % rc)
