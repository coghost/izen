# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '15/09/2017 2:01 PM'
__description__ = '''
参考: https://wiki.python.org/moin/PythonDecoratorLibrary
'''
import math
import functools
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import wraps
import ctypes
import datetime
import inspect
import os
import sys
import threading
import time
import traceback

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log


def singleton(cls):
    """

    -  单例模式之 ``装饰器方式`` 实现, 保证程序同一次运行生命周期,
       只有一个实例

    .. code:: python

            @singleton
            class T(object):
                pass

    :param cls:
    :type cls:
    :return:
    :rtype:
    """
    instances = dict()

    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


class Singleton(type):
    """
    单例模式之 ``__metaclass__`` 方式实现

    -  保证程序同一次运行生命周期, 只有一个实例
    -  使用方法: 在需要保证单例运行的class 里面添加
       ``__metaclass__ = Singleton``

    .. code:: python

            class A(object):
                __metaclass__ = Singleton

    """
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._instance:
            Singleton._instance[cls] = type.__call__(cls, *args, **kwargs)
        return Singleton._instance[cls]


def retry(tries, delay=3, backoff=2):
    '''Retries a function or method until it returns True.

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.'''

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay  # make mutable

            rv = f(*args, **kwargs)  # first attempt
            while mtries > 0:
                if rv is True:  # Done on success
                    return True

                mtries -= 1  # consume an attempt
                time.sleep(mdelay)  # wait...
                mdelay *= backoff  # make future wait longer

                rv = f(*args, **kwargs)  # Try again

            return False  # Ran out of tries :-(

        return f_retry  # true decorator -> decorated function

    return deco_retry  # @retry(arg[, ...]) -> true decorator


class Deprecated(object):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    - It accepts a single paramter ``msg`` which is shown with the warning.
    - It should contain information which function or method to use instead.

    """

    def __init__(self, msg):
        self.msg = msg

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn("Call to deprecated method ({}({}):{}).{}".format
                          (fn.__code__.co_filename.split('/')[-1],
                           fn.__code__.co_firstlineno,
                           fn.__name__, self.msg),
                          category=DeprecationWarning,
                          stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            return fn(*args, **kwargs)

        return wrapper


class Curried(object):
    '''
    Decorator that returns a function that keeps returning functions
    until all arguments are supplied; then the original function is
    evaluated.
    '''

    def __init__(self, func, *a):
        self.func = func
        self.args = a

    def __call__(self, *a):
        args = self.args + a
        if len(args) < self.func.__code__.co_argcount:
            return Curried(self.func, *args)
        else:
            return self.func(*args)


class Tomorrow:
    """
        参考原文件: https://github.com/madisonmay/Tomorrow

    - ``tomorrow/async/threads``

    """

    def __init__(self, future, timeout):
        try:
            self._future = future
            self._timeout = timeout
        except KeyboardInterrupt as err:
            raise SystemExit(111)

    def __getattr__(self, name):
        result = self._wait()
        return result.__getattribute__(name)

    def _wait(self):
        print('timeout is: ', self._timeout)
        return self._future.result(timeout=self._timeout)


def async_(n, base_type, timeout=None):
    def decorator(fn):
        if isinstance(n, int):
            pool = base_type(n)
        elif isinstance(n, base_type):
            pool = n
        else:
            raise TypeError("Invalid type: %s" % type(base_type))

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return Tomorrow(pool.submit(fn, *args, **kwargs), timeout=timeout)

        return wrapper

    return decorator


def async_threads(n, timeout=None):
    """
    https://docs.python.org/3.6/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
    - ``n`` 为同时运行被修饰函数的 ``总线程数`` (如果有多个地方调用被修改函数),
    - ``timeout超时时间`` 防止线程阻塞

    -  `async`_
    -  `Tomorrow`_

    .. code:: python

        @threads(1, timeout=1.1)
        def _to_01():
            time.sleep(1)
            print 'to_01'

    .. _async: #izen.assist.dec.async
    .. _Tomorrow: #izen.assist.dec.Tomorrow


    :param n: ``总线程数``
    :type n: int
    :param timeout: ``timeout超时时间``
    :type timeout: int
    """
    return async_(n, ThreadPoolExecutor, timeout)


def threads(bg=False, my_exception=TypeError):
    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if bg:
                try:
                    t = threading.Thread(target=fn, args=args, kwargs=kwargs)
                    t.daemon = True
                    t.start()
                    return t
                except my_exception as e:
                    print(e)
            else:
                return fn(*args, **kwargs)

        return wrapper

    return dec


def later(periods=10.0, precision=2.0, offset=0.0, check_interval=0.1, only_run_once=True):
    """
    **注意:会阻塞程序运行, 如果后台运行, 请放置于线程中**

    这个会阻塞程序运行, 如果不是这个目的, 请确保待装饰程序以线程方式运行

    * periods 是正常提供的参数, 如 10s, 则函数每10s 运行一次
    * precision 精度,
        * 如3s, 则 0~3s 内都可以触发运行
        * 如果是0s, 则函数可在  ```sleep check_interval``` 后, 一直运行
    * offset 偏移
        * 如果需要在 3s~6s 内运行, 则可设置 offset 为3, 这样到检测时间后, 会延迟 3s 运行

    example:
    ::

        @dec.threads(1)
        @later(...)
        def fn():
            print('test later')

    定期运行指定函数的装饰器, 如果precision 为0,则函数可一直运行

    :param periods: 函数运行周期 s
    :type periods: ``float``
    :param precision: 函数到运行周期, 可触发运行的容忍范围 s
    :type precision: ``float``
    :param offset: 从运行周期开始, 触发运行向后偏移时间 s
    :type offset: ``float``
    :param check_interval: 检测是否触发的间隔, 用来释放 cpu 资源
    :type check_interval: ``float``
    :param only_run_once: 周期内是否只运行一次
    :type only_run_once: ``bool``
    :return: 返回函数装饰器
    :rtype:
    """

    def dec_fn(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                while True:
                    # 检测时间
                    _st = time.time()

                    # 如果 precision 不为 0, 则触发检查容忍周期
                    _ready = not precision
                    if not _ready:
                        # 当前时间 - 偏移 对周期取余 满足小于精度, 则运行
                        _ready = (_st - offset) % periods <= precision

                    if _ready:
                        # 条件符合, 则运行处理函数
                        fn(*args, **kwargs)
                        # 计算函数运行时间
                        _es = time.time() - _st
                        # 如果要保证只运行一次, 且函数处理时间 小于 精度缓冲时间,
                        # 为了保证只运行一次, 需要额外等待 (精度 - 处理时间)
                        # 如果周期小于精度, 则取两者最小值
                        _extra_max_wait = min(periods, precision)
                        if only_run_once and _es < _extra_max_wait:
                            time.sleep(_extra_max_wait - _es)
                    time.sleep(check_interval)
            except KeyboardInterrupt as ____:
                raise SystemExit(1)
                # except Exception as err:
                #     print('error of later: {}'.format(err))

        return wrapper

    return dec_fn


def _async_raise(tid, exctype):
    """
    raises the exception, performs cleanup if needed
    参考: https://www.oschina.net/question/172446_2159505
    """
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    print('force close: {} {}'.format(tid, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


class TimeoutException(Exception):
    pass


def block_until_expired(timeout):
    """ 阻塞当前程序运行, 直到超时

    .. note: 会阻塞当前程序运行

    - 如果 ``timeout大于0``, 则当作 ``计时阻塞器`` 来使用

    .. code:: python

            @run_until(0.1)
            def s2():
                m = 5
                while m:
                    print('s2: ', m, now())
                    time.sleep(1)
                    m -= 1
                return 'good'

    :param timeout: int
    :type timeout:
    :return:
    :rtype:
    """
    if not callable(timeout):
        def dec(fn):
            @wraps(fn)
            def wrapper_(*args, **kwargs):
                class TimeLimited(threading.Thread):
                    def __init__(self, _error=None, ):
                        threading.Thread.__init__(self)
                        self.error_ = _error
                        self.result = None
                        self.stopped = False

                    def run(self):
                        self.result = fn(*args, **kwargs)

                try:
                    float(timeout)
                except ValueError as err:
                    print('err: ', err)
                    return None, None

                t = TimeLimited()
                t.start()

                if timeout > 0:
                    t.join(timeout)

                    if t.isAlive():
                        print('[timeout running out for {}]'.format(fn.__name__))
                        _async_raise(t.ident, SystemExit)
                        return None, None

                    return t.error_, t.result

            return wrapper_

        return dec


def catch(do, my_exception=TypeError, hints=''):
    """
    防止程序出现 exception后异常退出,
    但是这里的异常捕获机制仅仅是为了防止程序退出, 无法做相应处理
    可以支持有参数或者无参数模式

    -  ``do == True`` , 则启用捕获异常
    -  无参数也启用 try-catch

    .. code:: python

            @catch
            def fnc():
                pass

    -  在有可能出错的函数前添加, 不要在最外层添加,
    -  这个catch 会捕获从该函数开始的所有异常, 会隐藏下一级函数调用的错误.
    -  但是如果在内层的函数也有捕获方法, 则都会catch到异常.

    :param do:
    :type do:
    :param my_exception:
    :type my_exception:
    :param hints:
    :type hints:
    :return:
    :rtype:
    """
    if not hasattr(do, '__call__'):
        def dec(fn):
            @wraps(fn)
            def wrapper_(*args, **kwargs):
                if not do:
                    return fn(*args, **kwargs)

                try:
                    return fn(*args, **kwargs)
                except my_exception as e:
                    log.error("{}({})>{}: has err({})".format(
                        fn.__code__.co_filename.split('/')[-1],
                        fn.__code__.co_firstlineno,
                        fn.__name__, e))
                    traceback.print_exc()
                    if hints:
                        print(hints)

            return wrapper_

        return dec

    @wraps(do)
    def wrapper(*args, **kwargs):
        try:
            return do(*args, **kwargs)
        except my_exception as e:
            log.error("{}({})>{}: has err({})".format(
                do.__code__.co_filename.split('/')[-1],
                do.__code__.co_firstlineno,
                do.__name__, e
            ))
            traceback.print_exc()
            if hints:
                print(hints)

    return wrapper


def prt(show=False):
    """
    通过 ``装饰器`` 打印函数 ``参数, 运行时间, 返回值`` 等信息

    -  如果 ``prt(show==True)`` 打印函数信息,
    -  否则, 不做任何处理

    .. code:: python

        @prt(True)
        def say():
            print 'say'

        '''
        hello, world
        ----------------------------------------------------------------
        function(say) :
            arguments        = (),{}
            return           = None
            cost             = 0.000015 sec
        ----------------------------------------------------------------
        '''


        @prt(False)
        def say():
            print 'say'

        # 输出 hello, world

    -  定义一个全局变量 ``bl`` (调试模式设置为 ``True``, 在生产模式为
       ``False``)

    .. note: 调试模式, 设置为 True, 在生产模式时, 设置为False

    :param show: ``True/False``
    :type show: bool
    """

    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = None
            ts = time.time()
            if show:
                try:
                    result = fn(*args, **kwargs)
                except Exception as e:
                    print(e)
                finally:
                    te = time.time()
                    print("-" * 64)
                    print("function({}) :".format(fn.__name__))
                    print("\t{:<16} = {},{}".format('arguments', args, kwargs))
                    print("\t{:<16} = {}".format('return', result))
                    print("\t{:<16} = {:.6f} sec".format('cost', te - ts))
                    print("-" * 64)
                    return result
            else:
                return fn(*args, **kwargs)

        return wrapper

    return dec


if __name__ == '__main__':
    pass
    # print(add10(31))
    # print(callable(add))
    # print(hasattr(add, '__call__'))
