# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/24 11:07'
__description__ = '''
'''
import os
import sys
from collections import OrderedDict
from functools import wraps
import time

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from logzero import logger as log
from izen import helper
from izen.helper import R, G, B, C, Y, F, W


class Prettify(object):
    """
    color_log
    init_color_symbols
    log_random_sleep
    crt
    """

    def __init__(self, cfg, is_prod=False):
        self.is_prod = is_prod
        self.symbols = OrderedDict({})
        self.symbols_list = []
        self.cfg = cfg
        self.spawn()

    def spawn(self):
        self.init_color_symbols()
        self.symbols_list = list(self.symbols.values())

    def color_log(self, num, precision=2):
        if self.is_prod:
            return num
        if isinstance(num, str):
            return C.format(num)

        if isinstance(num, float):
            num = round(num, precision)

        try:
            cfg_rgb = self.cfg.get('pretty.rgb', '5,20,30')
            rgb = [int(x) for x in cfg_rgb.split(',')]
        except Exception:
            rgb = [5, 20, 30]
        if num <= rgb[0]:
            return G.format(num)
        elif num <= rgb[1]:
            return Y.format(num)
        elif num <= rgb[2]:
            return R.format(num)
        else:
            return F.format(num)

    def init_color_symbols(self):
        """
            'home', 'popover', 'get', 'scroll', 'paginate',
            'sleep', 'git', 'browser', 'bug',
            'end', 'right', 'wrong', 'save', 'main', 'raw'

        - font support: https://github.com/ryanoasis/nerd-fonts
        """
        # symbols = OrderedDict({})
        if self.is_prod:
            return
        keys = [
            'home', 'popover', 'get', 'scroll', 'paginate',
            'sleep', 'git', 'browser', 'bug', 'end',
            'right', 'wrong', 'save', 'main', 'raw',
            'keyboard', 'store', 'upload', 'send', 'music',
        ]

        _symbols = ['' for _ in keys]
        # symbols only available in my computer
        txt = self.cfg.get('pretty.symbols', '')
        if txt:
            sym = txt.split('\n')[0].split(',')
            _symbols = sym + _symbols[len(sym):]

        for i, k in enumerate(keys):
            if k in ['wrong', 'end']:
                self.symbols[k] = R.format(_symbols[i])
            else:
                self.symbols[k] = G.format(_symbols[i])

    def log_random_sleep(self, minimum=3.0, scale=1.0, hints=None):
        """wrap random sleep.

        - log it for debug purpose only
        """
        hints = '{} slept'.format(hints) if hints else 'slept'
        st = time.time()
        helper.random_sleep(minimum, scale)
        log.debug('{} {} {}s'.format(
            self.symbols.get('sleep', ''), hints, self.color_log(time.time() - st)))

    def crt(self, symbol='', hints='cost'):
        if isinstance(symbol, int):
            try:
                symbol = self.symbols_list[min(abs(symbol), len(self.symbols_list) - 1)]
            except IndexError as _:
                symbol = ''
        elif isinstance(symbol, str):
            symbol = self.symbols.get(symbol, G.format(symbol))

        def dec(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                st = time.time()
                result = fn(*args, **kwargs)
                cost_time = time.time() - st
                if cost_time > 0.009:
                    log.debug('{} {}({}) {} {} {}s'.format(
                        symbol,
                        C.format(fn.__code__.co_filename.split('/')[-1].split('.')[0]),
                        C.format(fn.__code__.co_firstlineno),
                        Y.format(fn.__name__),
                        hints,
                        self.color_log(cost_time)
                    ))
                return result

            return wrapper

        return dec


def term(*args, color='B', sep=' ', end='\n', file=None):
    args = [getattr(helper, color).format(x) for x in args]
    print(*args, sep=sep, end=end, file=file)


class ColorPrint(object):
    """
    if ``silent is true`` will print nothing.

    - R: Red
    - G: Green
    - B: Blue
    - C: Cyan
    - Y: Yellow
    - F: fuchsia
    - W: White
    """

    def __init__(self, silent=False):
        self.silent = silent

    def R(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)

    def G(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)

    def B(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)

    def C(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)

    def Y(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)

    def F(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)

    def W(self, *args, sep=' ', end='\n', file=None):
        if not self.silent:
            co_name = sys._getframe().f_code.co_name
            term(*args, color=co_name, sep=sep, end=end, file=file)


if __name__ == '__main__':
    cp = ColorPrint()
    cp12 = ColorPrint(silent=True)

    print('-' * 32)
    for m in 'RGBCYFW':
        for i in range(5):
            getattr(cp12, m)('{} {}'.format(m.lower(), i), end='; ')
    print('-' * 32)

    a = 0
    if 0 is not None:
        print('ok')
    if a:
        print('ok')
