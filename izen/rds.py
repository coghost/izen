#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '6/12/16 1:41 PM'
__description__ = '''
使用 host-redis(ORM) 来操作redis数据库
1. 建立连接
2. redis crud操作
'''

''' 
official
third-party
self-def
'''
import os
import sys

import hot_redis as hr

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_root = os.path.dirname(app_root)
sys.path.append(app_root)

if sys.version_info[0] < 3:
    import imp

    imp.reload(sys)
    sys.setdefaultencoding('utf-8')
else:
    from importlib import reload

    reload(sys)

''' file-global vars '''
List = hr.List
Set = hr.Set
Dict = hr.Dict
String = hr.String
ImmutableString = hr.ImmutableString
Int = hr.Int
Float = hr.Float
Queue = hr.Queue
LifoQueue = hr.LifoQueue
SetQueue = hr.SetQueue
LifoSetQueue = hr.LifoSetQueue
DefaultDict = hr.DefaultDict
MultiSet = hr.MultiSet

''' classes '''


class Rds(object):
    def __init__(self, conf=None):
        conf = conf if conf else {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 3,
            'socket_connect_timeout': 3,
        }
        hr.configure(conf)


class RdsClient(Rds):
    """
        封装hot-redis, 导出可能用到的所有属性

    .. warning:
        导出数据类型是为了隔绝hot-redis对程序的干扰

    """
    # _warn_ 下列导出数据类型是为了隔绝hot-redis对程序的干扰
    List = hr.List
    Set = hr.Set
    Dict = hr.Dict
    String = hr.String
    ImmutableString = hr.ImmutableString
    Int = hr.Int
    Float = hr.Float
    Queue = hr.Queue
    LifoQueue = hr.LifoQueue
    SetQueue = hr.SetQueue
    LifoSetQueue = hr.LifoSetQueue
    DefaultDict = hr.DefaultDict
    MultiSet = hr.MultiSet

    def __init__(self, conf):
        super(RdsClient, self).__init__(conf)

    def ok(self):
        l = self.List(key='foo')

    @classmethod
    def transaction(cls):
        """
        """
        return hr.transaction()


def transaction():
    """
    """
    return hr.transaction()


def client(*args, **kwargs):
    return hr.HotClient(*args, **kwargs)


def config(*args, **kwargs):
    return hr.configure(*args, **kwargs)


''' attributes private '''
