# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/09/2017 5:15 PM'
__description__ = '''
'''

import binascii
import datetime
import json
import os
import requests
import socket
import struct
import subprocess
import sys
import time
import platform
import base64
import getpass
import pickle
import random

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import psutil
from wcwidth import wcwidth
from clint import textui
import click
from logzero import logger as log

""" 交互选择功能 """


def gen_separator(separator=''):
    _header, _footer = '', ''
    if not separator:
        separator = []
    if not isinstance(separator, list):
        separator = [separator]
    if len(separator) == 1:
        _header = _footer = separator[0]
    elif len(separator) == 2:
        _header, _footer = separator
    return _header, _footer


def num_choice(choices, default='1', valid_keys='', depth=1, icons='', sn_info=None,
               indent=4, fg_color='green', separator='',
               with_img=6, img_list=None, img_cache_dir='/tmp', use_cache=False,
               ):
    """
        传入数组, 生成待选择列表, 如果启用图片支持, 需要额外传入与数组排序一致的图片列表,
        - 图片在 iterms 中显示速度较慢, 不推荐使用

        .. note: 图片在 iterms 中显示速度较慢, 如果数组长度大于10, 不推荐使用

        .. code:: python

            sn_info = {
                'align': '-', # 左右对齐
                'length': 2, # 显示长度
            }

    :param use_cache:
    :type use_cache:
    :param default:
    :type default:
    :param indent: ``左侧空白``
    :type indent:
    :param fg_color: ``前景色``
    :type fg_color:
    :param choices: 备选选项
    :type choices: list
    :param depth: ``如果是嵌套数组, 显示当前层级``
    :type depth: int
    :param icons: ``默认展示的icons:  '🍺🍻◆☊✩♪♩♪``
    :type icons: str
    :param sn_info: ``需要展示的序号的信息长度对齐方式, 默认2个字符/右对齐``
    :type sn_info: dict
    :param valid_keys: ``可以输入的有效 key, 使用 ',' 分隔``
    :type valid_keys: str
    :param separator: 分隔符 header/footer, 默认无, 如果不为空, 则显示
    :type separator:
    :param img_cache_dir:  ``图片缓存目录``
    :type img_cache_dir: str
    :param with_img: ``是否使用图片, 如果值大于0, 则以实际值大小来作为终端显示行数``
    :type with_img: int
    :param img_list: ``图片原始 url ``
    :type img_list: list
    :return:
    :rtype:
    """
    icons = '🍺🍻◆☊✩♪♩♪' if not icons else icons
    if not choices:
        return None

    # warn: 这里需要使用 None, 不能 not default 来判断!!!
    if default != None:
        default = '{}'.format(default)

    sn_info = sn_info or {}
    _header, _footer = gen_separator(separator=separator)

    with textui.indent(indent, quote=' {}'.format(icons[depth - 1])):
        if _header:
            textui.puts(getattr(textui.colored, fg_color)(_header))

        for i, choice in enumerate(choices, start=1):
            if with_img > 0 and img_list:
                cat_net_img(img_list[i - 1],
                            indent=indent,
                            img_height=with_img,
                            img_cache_dir=img_cache_dir,
                            use_cache=use_cache)

            _align = '{}{}'.format(sn_info.get('align', ''), sn_info.get('length', 2))
            # _hint = '%{}s. %s'.format(_align) % (i, choice)
            _hint_num = '%{}s.'.format(_align) % i
            _hint = '[{}]'.format(_hint_num)
            _hint = textui.colored.magenta(_hint)
            _hint += getattr(textui.colored, fg_color)(' %s' % choice)
            textui.puts(_hint)

        if _footer:
            textui.puts(getattr(textui.colored, fg_color)(_footer))

    _valid = [str(x + 1) for x in range(0, len(choices))]
    c = click.prompt(
        # click.style('[Depth: ({})]Your Choice(q-quit/b-back)?', fg='cyan').format(depth),
        click.style('Your Choice(q-quit/b-back)?', fg='cyan'),
        type=str,
        default=default
    )

    if str(c) in 'qQ':
        os._exit(-1)
    if valid_keys == 'all':
        return c
    elif str(c) in 'bB':
        return str(c)
    elif valid_keys and str(c) in valid_keys.split(','):
        return str(c)
    elif c not in _valid:
        textui.puts(textui.colored.red('  😭 ✘ Invalid input[{}]'.format(c)))
        return num_choice(choices)
    else:
        return int(c) - 1


def yn_choice(msg, indent=4, fg_color='cyan', separator=''):
    """
        传入 msg , 返回 True/False

    :param separator:
    :type separator:
    :param fg_color:
    :type fg_color:
    :param indent:
    :type indent:
    :param msg:
    :type msg:
    :return:
    :rtype:
    """
    _header, _footer = gen_separator(separator=separator)
    if _header:
        textui.puts(getattr(textui.colored, fg_color)(_header))
    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(textui.colored.green(msg))
    if _footer:
        textui.puts(getattr(textui.colored, fg_color)(_footer))

    c = click.confirm(
        click.style('Your Choice?[yn] (q-quit/b-back)?', fg='cyan'),
        default=True,
    )
    return c


def pause_choice(msg, indent=4, fg_color='green', separator=''):
    _header, _footer = gen_separator(separator=separator)

    if _header:
        textui.puts(getattr(textui.colored, fg_color)(_header))
    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(getattr(textui.colored, fg_color)(msg))

    if _footer:
        textui.puts(getattr(textui.colored, fg_color)(_footer))

    c = click.prompt(click.style('Press Any Key to Continue...(q-quit)', fg='cyan'), default='.')
    if str(c) in 'qQ':
        os._exit(-1)
    return c


def copy_to_clipboard(dat):
    """
        复制 ``dat`` 内容到 剪切板中

    :return: None
    """
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(to_bytes(dat))
    p.stdin.close()
    p.communicate()


def cat_net_img(url='', indent=4, img_height=0, img_cache_dir='/tmp', use_cache=False):
    """
        - 优先 从微博缓存目录读取图片
        - 如果失败, 再从相应的url读取照片

    :param use_cache: ``使用缓存``
    :type use_cache:
    :param img_cache_dir:
    :type img_cache_dir:
    :param url:
    :type url:
    :param indent:
    :type indent:
    :param img_height:
    :type img_height:
    :return:
    :rtype:
    """
    name = url.split('/')[-1]
    pth = os.path.join(img_cache_dir, name)

    # 如果不使用缓存 或者 文件不存在, 则先下载到本地, 然后再读取
    if not use_cache or not is_file_ok(pth):
        raw = requests.get(url)
        write_file(raw.content, pth)

    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(cat_img_by_path(pth, img_height))


def cat_img_by_path(pth, img_height=0):
    mar = to_str(base64.b64encode(read_file(pth)))
    return cat_img_cnt(mar, img_height)


def cat_img_cnt(cnt_in='', img_height=0):
    """
       展示图片内容

    :param cnt_in:
    :type cnt_in:
    :param img_height:  照片占用的终端行数
    :type img_height: int
    :return:
    :rtype:
    """
    if not img_height:
        img_height = 6
    _head = '\x1b]1337;'
    _file = 'File=name={}'.format(to_str(base64.b64encode(to_bytes(now()))))
    _attr = ';inline=1;height={}:'.format(img_height)
    _tail = '\x07'
    cnt = '{}{}{}{}{}'.format(
        _head, _file, _attr, cnt_in, _tail
    )
    return cnt


def color_print(msg, indent=4, color='green'):
    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(getattr(textui.colored, color)(msg))


""" 时间处理 """


def now(fmt='%Y-%m-%d %H:%M:%S'):
    """
        获取当前时间的字符串表示

    :param fmt: ``默认(%Y-%m-%d %H:%M:%S)``
    :type fmt: str
    :return:
    :rtype: str
    """
    return datetime.datetime.now().strftime(fmt)


def str2unixtime(ts, fmt='%Y-%m-%d %H:%M:%S'):
    """
        将固定格式的字符串转换成对应的时间戳到秒级别

    - 使用:

    >>> str2unixtime('2016-01-01 01:01:01')
    1451581261

    :param ts:
    :type ts:
    :param fmt:
    :type fmt:
    :return:
    :rtype:
    """
    t = time.strptime(ts, fmt)
    return int(time.mktime(t))


def unixtime2str(timestamp, fmt='%Y-%m-%d %H:%M:%S'):
    """
    将 ``秒级别的时间戳`` 转换成字符串

    .. warning:
        时间戳是以 ``秒`` 为单位的

    :param timestamp: unix timestamp
    :type timestamp: int
    :param fmt: show format
    :type fmt: str
    :return:
    :rtype: str
    """
    dt = None
    try:
        timestamp = time.localtime(timestamp)
        dt = time.strftime(fmt, timestamp)
    except Exception as err:
        print(err)
    return dt


def unixtime(mm=False):
    """
        返回当前时间的 ``unix时间戳``, 默认返回级别 ``second``

    - 可设置 ``mm=True`` 来获取毫秒, 毫秒使用 ``(秒+随机数)*1000`` 来实现, 尽量防止出现相同

    - 使用时间范围限制:(2001/9/9 9:46:40 ~ 2286/11/21 1:46:3)
    - 样例

    .. code:: python

        # 标准情况直接使用秒
        len(str(unixtime()))
        # 输出 10

        # 如果需要唯一标识, 可以尝试使用
        len(str(unixtime(True)))
        # 输出 13

    """
    if mm:
        return int((time.mktime(datetime.datetime.now().timetuple()) + random.random()) * 1000)
    else:
        return int(time.mktime(datetime.datetime.now().timetuple()))


"""文件处理"""


def mkdir_p(pathin, is_dir=False):
    """
        分隔pathin, 并以此创建层级目录

    - ``is_dir == True``: 则将所有 ``/ 分隔`` 的pathin 当前文件夹
    - 否则, 将分隔的最后一个元素当做是文件处理

    >>> # 创建一个目录 /tmp/a/b/c
    >>> mkdir_p('/tmp/a/b/c/001.log')

    :param is_dir: ``是否目录``
    :type is_dir: bool
    :param pathin: ``待创建的目录或者文件路径``
    :type pathin: str
    """
    h, _ = os.path.split(pathin)
    if is_dir:
        h = pathin
    try:
        if not os.path.exists(h):
            os.makedirs(h)
    except FileExistsError as _:
        pass
    except Exception as err:
        raise err


def walk_dir_with_filter(pth, prefix=None, suffix=None):
    """
        默认情况下,会遍历目录下所有文件,写入数组返回.

    - ``prefix`` 会过滤以 其开头的所有文件
    - ``suffix`` 结尾

    :param pth:
    :type pth:
    :param prefix:
    :type prefix:
    :param suffix:
    :type suffix:
    :return:
    :rtype:
    """
    if suffix is None or type(suffix) != list:
        suffix = []
    if prefix is None or type(prefix) != list:
        prefix = []

    r = []
    for root_, dirs, files in os.walk(pth):
        for file_ in files:
            full_pth = os.path.join(root_, file_)

            # 排除 \.开头文件, 及 .pyc .md 结尾文件
            c = False
            for x in prefix:
                if file_.startswith(x):
                    c = True
                    break
            if c:
                continue
            # if runs here , c is False
            for x in suffix:
                if file_.endswith(x):
                    c = True
                    break
            if c:
                continue

            r.append(full_pth)
    return r


def write_file(dat, pth, append=False):
    """
        将 dat 内容写入 pth 中, 如果写入成功, 返回为空, 否则返回失败信息

    :type append: ``bool``
    :param append: 写入模式
    :type append: ``bool``
    :param dat: 待写入内容
    :type dat: ``str``
    :param pth:
    :type pth: ``str``
    :return:
    :rtype:
    """
    err = None

    _d, _nm = os.path.split(pth)
    if _d and not os.path.exists(_d):
        os.makedirs(_d)

    try:
        mode = 'ab' if append else 'wb'

        with open(pth, mode) as _fp:
            dat = to_bytes(dat)
            _fp.write(dat)
    except Exception as _err:
        err = _err
    return err


def read_file(pth):
    """
        读取文件, 并返回内容,
        如果读取失败,返回None

    :param pth:
    :type pth:
    :return:
    :rtype:
    """
    cont = None
    try:
        with open(u'' + pth, 'rb') as fp:
            cont = fp.read()
    except Exception as err:
        print(err)
    return cont


def clear_empty_file(pathin, extensions=None, do_clear=False):
    if not os.path.exists(pathin):
        log.debug('{} not exist'.format(pathin))
        return

    for root, dirs, files in os.walk(pathin):
        for f in files:
            ext = f.split('.')[-1]
            if extensions and ext not in extensions:
                continue
            _fpth = os.path.join(root, f)
            if not is_file_ok(_fpth):
                log.debug('_delete_ file: {}/{}'.format(root, f.split('-')[1]))
                if do_clear:
                    os.remove(_fpth)


def is_file_ok(fpth):
    """
        判断文件是否为空, 如果不存在, 或者大小为0, 则返回0, 否则返回文件大小.

    :param fpth:
    :type fpth:
    :return:
    :rtype:
    """
    try:
        return os.path.getsize(fpth)
    except FileNotFoundError as _:
        return 0


def b64_file(src_file):
    """
    打包当前程序目录中的所有程序文件 生成 tgz 文件, 读取 base64编码后, 使用aes加密数据,并附加rsa签名
    :return:
    :rtype:
    """
    z = None
    i = 0
    while not z and i < 3:
        z = read_file(src_file)
        time.sleep(0.1)
        i += 1

    if not z:
        log.warning('cannot open {} '.format(src_file))
        return z

    c = base64.b64encode(z)
    return c


def pickle_m2f(dat, pth):
    """
        将 dat 内容同步到文件存储中

    :param dat:
    :type dat:
    :param pth:
    :type pth:
    :return:
    :rtype:
    """
    mkdir_p(pth)
    # 为了2与3兼容, 设置 dump 的协议为 2
    with open(pth, 'wb') as f:
        pickle.dump(dat, f, 2)


def pickle_f2m(pth, rt=None):
    """
        获取文件内容并返回, 如果文件不存在, 则返回 rt

    :param pth:
    :type pth:
    :param rt: ``如果需要指定返回值, 请设置该值``
    :type rt:
    :return:
    :rtype:
    """
    r = rt
    try:
        with open(pth, 'rb') as f:
            r = pickle.load(f)
    except Exception as err:
        sys.stderr.write('pickle_f2m(pth={}) with error: {}\n'.format(pth, err))
    return r


""" 数据校验 """


def l_endian(v):
    """ 小端序 """
    w = struct.pack('<H', v)
    return str(binascii.hexlify(w), encoding='gbk')


def b_endian(v):
    """ 大端序 """
    w = struct.pack('>H', v)
    return str(binascii.hexlify(w), encoding='gbk')


def xorsum(t):
    """
    异或校验
    :param t:
    :type t:
    :return:
    :rtype:
    """
    _b = t[0]
    for i in t[1:]:
        _b = _b ^ i
        _b &= 0xff
    return _b


def xorsum_counter(t):
    """
    异或取反
    :param t:
    :type t:
    :return:
    :rtype:
    """
    return ~xorsum(t) & 0xff


def check_sum(buf, csum):
    """
    检查数据的校验和
    :param buf:
    :type buf:
    :param csum:
    :type csum:
    :return:
    :rtype:
    """
    csum = csum.encode('utf-8')
    _csum = ord(buf[0])
    for x in buf[1:]:
        _csum ^= ord(x)

    _csum = binascii.b2a_hex(chr(_csum).encode('utf-8')).upper()
    if _csum != csum:
        sys.stderr.write('csum not matched: ({} {})\n'.format(_csum, csum))
    return _csum == csum


def crc16(cmd, use_byte=False):
    """
        CRC16 检验
        - 启用``use_byte`` 则返回 bytes 类型.

    :param cmd: 无crc检验的指令
    :type cmd:
    :param use_byte: 是否返回byte类型
    :type use_byte:
    :return: 返回crc值
    :rtype:
    """
    crc = 0xFFFF

    # crc16 计算方法, 需要使用 byte
    if hasattr(cmd, 'encode'):
        cmd = bytes.fromhex(cmd)

    for _ in cmd:
        c = _ & 0x00FF
        crc ^= c
        for i in range(8):
            if crc & 0x0001 > 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1

    # modbus crc16计算时,需要高/低位倒置
    t = [(crc & 0x00FF), (crc >> 8 & 0xFF)]
    crc = '%02X%02X' % (t[0], t[1])
    if use_byte:
        crc = bytes.fromhex(crc)
    return crc


"""系统命令"""


def debug(users=None):
    """
        是一种方便的测试模式, 用于 ``全局开启`` 或者关闭测试功能

    - 如果当前用户存在在users列表中, 则设定程序运行于debug模式

    """
    if not users:
        return False
    users = users if isinstance(users, list) else [users]
    return True if getpass.getuser() in users else False


def get_addr(iface='lo0'):
    """
        获取网络接口 ``iface`` 的 ``mac``

    - 如果系统类型为 ``mac``, 使用 ``psutil``
    - 其他使用 ``socket``

    :param iface: ``网络接口``
    :type iface: str
    :return: ``mac地址/空``
    :rtype: str/None
    """
    if platform.system() in ['Darwin', 'Linux']:
        _AF_FAMILY = psutil.AF_LINK
    else:
        raise SystemExit('Unsupported System. Only Mac/Linux Supported')

    addrs = psutil.net_if_addrs()
    for n in addrs[iface]:
        if n.family == _AF_FAMILY:
            return n.address


def uniqid(iface='wlan0', is_hex=True):
    """
        使用网卡的物理地址 ``默认wlan0`` 来作为标识

    - 置位 ``is_hex``, 来确定返回 ``16进制/10进制格式``

    :param iface: ``网络接口(默认wlan0)``
    :type iface: str
    :param is_hex: ``True(返回16进制)/False(10进制)``
    :type is_hex: bool
    :return: ``mac地址/空``
    :rtype: str
    """
    # return str(appid.getnode()) if not is_hex else str(hex(appid.getnode()))[2:-1]
    m_ = get_addr(iface)
    m_ = ''.join(m_.split(':')) if m_ else m_
    if m_ and not is_hex:
        m_ = str(int(m_.upper(), 16))
    return m_


def app_id(iface=''):
    """ 依据指定的 ``iface`` 名, 来获取程序运行需要的唯一ID

    - iface 为空, 则自动从系统选择第一个可用的网络接口 mac
    - 顺序,自动获取编号最小的网络接口:
        + macosx: en0~n
        + linux: eth/wlan(0~n)

    :param iface: ``系统中的网络接口名``
    :type iface: str
    :return:
    :rtype:
    """
    if iface:
        return uniqid(iface)

    if platform.system() == 'Darwin':
        _ava_start = ['en']
    elif platform.system() == 'Linux':
        _ava_start = ['eth', 'wla']
    else:
        return None

    nics = psutil.net_if_addrs()
    _ifces = list(nics.keys())
    _ifces.sort()

    for _ in _ifces:
        if _[:len(_ava_start[0])] in _ava_start:
            return uniqid(_)


def get_sys_cmd_output(cmd):
    """
        通过 ``subprocess`` 运行 ``cmd`` 获取系统输出

    - ``cmd`` 为数组形式
    - 需要符合 ``subprocess`` 调用标准
    -  返回

       -  err信息,
       -  使用 ``换行符\\n`` 分隔的数组

    :param cmd:
    :type cmd: list, str
    :return:
    :rtype:
    """
    _e, op = None, ''
    if not isinstance(cmd, list):
        cmd = cmd.split(' ')

    try:
        op = subprocess.check_output(cmd)
        if sys.version_info[0] >= 3:
            op = to_str(op)
        op = op.split('\n')
    except Exception as err:
        _e = err

    return _e, op


def os_cmd(cmd):
    rs = os.popen(cmd).read()
    return rs


def reboot():
    """
        ``重启系统``

    - 需要权限支持

    """
    sys.stdout.write('{}\n'.format(subprocess.call('/sbin/reboot')))


"""程序控制 线程/定期运行"""


def block_here(duration=0):
    """
    如果 duration 为0, 则一直阻塞程序运行
    :param duration:
    :type duration:
    :return:
    :rtype:
    """
    try:
        while not duration:
            time.sleep(0.001)

        while duration:
            time.sleep(0.001)
            duration -= 1
    except KeyboardInterrupt as err:
        raise SystemExit(1)


""" http get/post """


def do_get(url, params, to=3):
    """
    使用 ``request.get`` 从指定 url 获取数据

    :param params: ``输入参数, 可为空``
    :type params: dict
    :param url: ``接口地址``
    :type url:
    :param to: ``响应超时返回时间``
    :type to:
    :return: ``接口返回的数据``
    :rtype: dict
    """
    try:
        rs = requests.get(url, params=params, timeout=to)
        if rs.status_code == 200:
            try:
                return rs.json()
            except Exception as __e:
                # log.error(__e)
                return rs.text
    except Exception as er:
        log.error('get {} ({}) with err: {}'.format(url, params, er))
        time.sleep(0.5)
    return {}


def do_post(url, payload, to=3, use_json=True):
    """
    使用 ``request.get`` 从指定 url 获取数据

    :param use_json: 是否使用 ``json`` 格式, 如果是, 则可以直接使用字典, 否则需要先转换成字符串
    :type use_json: bool
    :param payload: 实际数据内容
    :type payload: dict
    :param url: ``接口地址``
    :type url:
    :param to: ``响应超时返回时间``
    :type to:
    :return: ``接口返回的数据``
    :rtype: dict
    """
    try:
        if use_json:
            rs = requests.post(url, json=payload, timeout=to)
        else:
            rs = requests.post(url, data=payload, timeout=to)
        if rs.status_code == 200:
            log.warn(rs.text)
            return rs.json()
    except Exception as er:
        log.error('post to {} ({}) with err: {}'.format(url, payload, er))
        time.sleep(0.5)
    return {}


""" 进制, str/bytes 转换 """


def b2h(bins):
    return ''.join(["%02X" % x for x in bins]).strip()


def to_str(str_or_bytes, charset='utf-8'):
    """
        转换 str_or_bytes 为 str

        - if hasattr(str_or_bytes, 'decode'), 转换

    :param str_or_bytes:
    :type str_or_bytes:
    :param charset:
    :type charset:
    :return:
    :rtype:
    """
    return str_or_bytes.decode(charset) if hasattr(str_or_bytes, 'decode') else str_or_bytes


def to_bytes(str_or_bytes):
    """
        转换 str_or_bytes 为 bytes

        - if hasattr(str_or_bytes, 'encode'), 转换

    :param str_or_bytes:
    :return:
    """
    return str_or_bytes.encode() if hasattr(str_or_bytes, 'encode') else str_or_bytes


""" 实用功能 """


class Colorful(object):
    """
        colorful output

        debug: green
        info: cyan
        error: red
    """

    def __init__(self, indent=0, quote=' '):
        self.indent = indent
        self.quote = quote

    def _p(self, color, msg):
        if not self.indent:
            textui.puts(getattr(textui.colored, color)(msg))
            return

        with textui.indent(indent=self.indent, quote=self.quote):
            textui.puts(getattr(textui.colored, color)(msg))

    def debug(self, msg):
        self._p('green', msg)

    def info(self, msg):
        self._p('cyan', msg)

    def error(self, msg):
        self._p('red', msg)


def multi_replace(original, pattens, delim='|,'):
    """
        使用 ``multi_delim`` 中的所有规则来替换 ``original`` 字符串内容

    >>> orig = '今天是一个好天气'
    >>> multi_replace(orig, '今天|是|好天气')
    '一个'
    >>> multi_replace(orig, '今天,today |是,is |好天气,good weather')
    'today is 一个good weather'

    :param delim: 分隔符, 外层 `|` 内层 `,`
    :type delim:
    :param original: 原始字符串
    :type original: str
    :param pattens: 替换规则
    :type pattens: str
    :return:
    :rtype:
    """
    if not original:
        return ''

    if not delim or len(delim) != 2:
        delim = '|,'

    # 最外层分隔符, 第二层分隔符
    level0, level1 = delim[0], delim[1]

    for re_pair in pattens.split(level0):
        _f, _to = re_pair, ''

        re_pair = re_pair.split(level1)
        if len(re_pair) == 2:
            _f, _to = re_pair
        original = original.replace(_f, _to)
    return original


def randint(start=0, end=100):
    return random.randint(start, end)


def words(fpth):
    """
    ww = words(os.path.join(app_root, 'ig/helper.py'))
    for k, v in (ww.most_common(3)):
        print(k, v)

    :param fpth:
    :type fpth:
    :return:
    :rtype:
    """
    from collections import Counter
    words__ = Counter()
    with open(fpth) as fp:
        for line in fp:
            words__.update(line.strip().split(' '))
    return words__


class TermTable(object):
    def __init__(self, attributes):
        """Creates a new PylsyTable object with the given attrs (cols)."""
        self.StrTable = ""
        self.Table = []
        self.AttributesLength = []
        self.Lines_num = 0
        if type(attributes) != list:
            attributes = [attributes]
        self.Attributes = [u"{0}".format(attr) for attr in attributes]
        self.Cols_num = len(self.Attributes)
        for attribute in self.Attributes:
            col = dict()
            col[attribute] = []
            self.Table.append(col)

    def _print_divide(self):
        """Prints all those table line dividers."""
        for space in self.AttributesLength:
            self.StrTable += "+ " + "- " * space
        self.StrTable += "+" + "\n"

    def append_data(self, attribute, values):
        """Appends the given value(s) to the attribute (column)."""
        found = False
        if type(values) != list:
            values = [values]
        for col in self.Table:
            if attribute in col:
                dict_values = [u"{0}".format(value) for value in values]
                col[attribute] += dict_values
                found = True
        if not found:
            raise KeyError(attribute)

    def add_data(self, attribute, values):
        """Sets the given values for the attribute (column)."""
        found = False
        if type(values) != list:
            values = [values]
        for col in self.Table:
            if attribute in col:
                dict_values = [u"{0}".format(value) for value in values]
                col[attribute] = dict_values
                found = True
        if not found:
            raise KeyError(attribute)

    def _create_table(self):
        """
        Creates a pretty-printed string representation of the table as
        ``self.StrTable``.
        """
        self.StrTable = ""
        self.AttributesLength = []
        self.Lines_num = 0
        # Prepare some values..
        for col in self.Table:
            # Updates the table line count if necessary
            values = list(col.values())[0]
            self.Lines_num = max(self.Lines_num, len(values))
            # find the length of longest value in current column
            key_length = max([self._disp_width(v) for v in values] or [0])
            # and also the table header
            key_length = max(key_length, self._disp_width(list(col.keys())[0]))
            self.AttributesLength.append(key_length)
        # Do the real thing.
        self._print_head()
        self._print_value()

    def _print_head(self):
        """Generates the table header."""
        self._print_divide()
        self.StrTable += "| "
        for colwidth, attr in zip(self.AttributesLength, self.Attributes):
            self.StrTable += self._pad_string(attr, colwidth * 2)
            self.StrTable += "| "
        self.StrTable += '\n'
        self._print_divide()

    def _print_value(self):
        """Generates the table values."""
        for line in range(self.Lines_num):
            for col, length in zip(self.Table, self.AttributesLength):
                vals = list(col.values())[0]
                val = vals[line] if len(vals) != 0 and line < len(vals) else ''
                self.StrTable += "| "
                self.StrTable += self._pad_string(val, length * 2)
            self.StrTable += "|" + '\n'
            self._print_divide()

    def _disp_width(self, pwcs, n=None):
        """
        A wcswidth that never gives -1. Copying existing code is evil, but..
        github.com/jquast/wcwidth/blob/07cea7f/wcwidth/wcwidth.py#L182-L204
        """
        # pylint: disable=C0103
        #         Invalid argument name "n"
        # TODO: Shall we consider things like ANSI escape seqs here?
        #       We can implement some ignore-me segment like those wrapped by
        #       \1 and \2 in readline too.
        end = len(pwcs) if n is None else n
        idx = slice(0, end)
        width = 0
        for char in pwcs[idx]:
            width += max(0, wcwidth(char))
        return width

    def _pad_string(self, str, colwidth):
        """Center-pads a string to the given column width using spaces."""
        width = self._disp_width(str)
        prefix = (colwidth - 1 - width) // 2
        suffix = colwidth - prefix - width
        return ' ' * prefix + str + ' ' * suffix

    def __str__(self):
        """Returns a pretty-printed string representation of the table."""
        self._create_table()
        return self.StrTable
