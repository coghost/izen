# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '28/03/2018 10:39 AM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import logging

import profig
import logzero

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)


class Conf(object):
    """配置文件模块基础类

    pth: 文件存储位置
    dat: 配置文件内容的字典结构

    样例:
        # 定义 pth, dat
        pth = '/tmp/t.cfg'
        dat = {
            'mqtt.host': '127.0.0.1',
            'mqtt.port': 1883,
            'mqtt.quit_if_same_cid': True,
        }
        cfg = Conf(pth=pth, dat=dat).cfg
    """

    def __init__(self, pth, dat=None, enable_default_log=True):
        """初始化配置文件
        - 文件不存在: 将字典dat初始化到文件中
        - 文件存在: 以字典数据类型来初始化配置文件

        :param dat: ``字典类型``
        :type dat: dict
        :param pth: ``文件存储路径``
        :type pth: str
        :param enable_default_log: ``是否启用默认log配置参数``
        :type enable_default_log: bool
        """
        self.cfg = profig.Config(pth, encoding='utf-8')

        # 读取配置
        self.cfg.read()

        # 初始化默认log字段类型
        if enable_default_log:
            self.__spawn()

        # 初始化自定义字典
        if dat:
            self.__do_init(dat)

        # 在配置不存在时, 需要首先在初始化在内存中, 然后再同步到本地并退出执行程序
        if not os.path.exists(os.path.expanduser(pth)):
            self.cfg.sync()
            raise SystemExit('[init-cfg-file]: {}'.format(os.path.expanduser(pth)))

    def __spawn(self):
        """通过手动方式, 指定字段类型与默认值,
            - 如果配置文件有变动, 需要手动在这里添加
            - 如果配置字段未在这里指出, 则默认为 string, 使用时需要手动转换
        """
        dat = {
            'log.enabled': False,
            'log.file_pth': '/tmp/izen.log',
            'log.file_backups': 3,
            'log.file_size': 5,
            'log.level': 10,
            'log.symbol': '☰☷☳☴☵☲☶☱',
        }
        self.__do_init(dat)

    def __do_init(self, dat_dict):
        """
            使用字典方式来更新到存储文件中
        :param dat_dict:
        :type dat_dict:
        :return:
        :rtype:
        """
        for k, v in dat_dict.items():
            if isinstance(v, dict):
                self.cfg.init(k, v['val'], v['proto'])
            else:
                self.cfg.init(k, v)
        self.cfg.sync()


class LFormatter(logzero.LogFormatter):
    """ 改写 logzero 的 LogFormatter

    - 移除 ``[]``, 支持自定义前导字符(任意长度, 但只取前5个字符),
    - 增加 ``critical`` 的颜色实现

    """
    DEFAULT_FORMAT = '%(color)s {}%(levelname)1.1s %(asctime)s ' \
                     '%(module)s:%(lineno)d {}%(end_color)s %(' \
                     'message)s'
    DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: logzero.ForegroundColors.CYAN,
        logging.INFO: logzero.ForegroundColors.GREEN,
        logging.WARNING: logzero.ForegroundColors.YELLOW,
        logging.ERROR: logzero.ForegroundColors.RED,
        logging.CRITICAL: logzero.ForegroundColors.MAGENTA,
    }

    def __init__(self, log_pre='♨✔⊙✘◈'):
        logzero.LogFormatter.__init__(self,
                                      datefmt=self.DEFAULT_DATE_FORMAT,
                                      colors=self.DEFAULT_COLORS
                                      )
        blank__ = '➵' * 5
        log_pre += blank__[len(log_pre):]  # 如果无, 或者长度小于5, 则使用 blank_ 自动补全5个字符
        self.CHAR_PRE = dict(zip(range(5), log_pre))

    def format(self, record):
        _char_pre = self.CHAR_PRE[record.levelno / 10 - 1] + ' '
        __fmt = self.DEFAULT_FORMAT
        __fmt = __fmt.format(_char_pre, '|')
        self._fmt = __fmt
        return logzero.LogFormatter.format(self, record)
