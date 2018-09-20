# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '09/05 12:07'
__description__ = '''
## 使用 selenium + chrome 实现爬虫
'''

import os
import sys
import random
from copy import deepcopy

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (NoSuchAttributeException,
                                        WebDriverException, NoSuchElementException,
                                        NoSuchFrameException, TimeoutException)

from izen import helper, dec, crawler
from izen.helper import rand_pareto_float, rand_block
from logzero import logger as log

PIXELS_PER_DOWN_KEY = 81  # 9*9 => 1


def gen_find_method(ele_type, multiple=True, extra_maps=None):
    """
    将 ele_type 转换成对应的元素查找方法
    e.g::

        make_elt(ele_type=name, False) => find_element_by_name
        make_elt(ele_type=name, True) => find_elements_by_name

    :param ele_type:
    :type ele_type:
    :param multiple:
    :type multiple:
    :param extra_maps:
    :type extra_maps:
    :return:
    """
    _ = 'elements' if multiple else 'element'
    d = {
        'class': 'class_name'
    }
    if isinstance(extra_maps, dict):
        d = dict(d, **extra_maps)
    return 'find_{}_by_{}'.format(_, d.get(ele_type, ele_type))


class Robot(object):
    """
    create a web driven crawl robot
    """

    def __init__(self, driver=None, **kwargs):
        """
        if no ``driver`` supplied, set driver to ``Chrome``

        :param driver:
        """
        self.driver = driver if driver else webdriver.Chrome()
        self.log_who = {
            'click': False,
        }
        lw = kwargs.get('log_who')
        if isinstance(lw, dict):
            self.log_who = dict(self.log_who, **lw)

    def load_page(self, url):
        try:
            self.driver.get(url)
        except (TimeoutException, Exception) as e_:
            log.error('open {} failed with: {}'.format(url, e_))
            raise

    def get_elements(self, dat, multiple=False, retry=1, **kwargs):
        """
            映射 dat:dict => ``find_element_by_dat.key`` 来查找元素

        :param dat: a dict like {'name': <the ele name>}
        :type dat: dict
        :param multiple:
        :type multiple: bool
        :param retry:
        :type retry: int
        :return:
        :rtype:
        """
        if not isinstance(dat, dict):
            return dat

        while retry > 0:
            for k, v in dat.items():
                try:
                    # 获取成功, 直接返回
                    return getattr(self.driver, gen_find_method(k, multiple, kwargs.get('extra_maps')))(v)
                except WebDriverException as _:
                    if not kwargs.get('skip_log'):
                        log.warning('[{}]: {}'.format(dat, _))
                finally:
                    retry -= 1
            raise ValueError(dat)

    def has_element(self, dat, skip_log=False):
        """
        :param dat: dict like {'name': <the ele name>}
        :type dat: dict
        :param skip_log: skip log at your wish
        :type skip_log:
        :return:
        :rtype:
        """
        try:
            if self.get_elements(dat, skip_log=skip_log):
                return True
        except Exception as _:
            if not skip_log:
                log.error(_)
            return False

    def smooth_scroll(self, x_dist, y_dist, x_neg, y_neg, two_paned_scroll='window', element=True):
        try:
            if two_paned_scroll != 'window':
                if element:
                    src_str = ''.join(['document.getElementById(\'', two_paned_scroll, '\')'])
                else:
                    src_str = ''.join(['document.getElementsByClassName(\'', two_paned_scroll, '\')[0]'])
            else:
                src_str = 'window'
            x_scroll = '.scrollBy(8,0);'
            y_scroll = '.scrollBy(0,8);'
            if x_neg:
                x_scroll = '.scrollBy(-8,0);'
            if y_neg:
                y_scroll = '.scrollBy(0,-8);'
            for i in range(x_dist // 8):
                self.driver.execute_script(src_str + x_scroll)
                rand_block(0, 0.001)
            for i in range(y_dist // 8):
                self.driver.execute_script(src_str + y_scroll)
                rand_block(0, 0.001)
        except WebDriverException as e:
            log.warning(e.msg)
            raise

    def _mock_input(self, target, content):
        """
            mock human input

        :param target: the element to input to
        :param content: the content
        :return:
        """
        content = helper.to_str(content)
        for w in content:
            target.send_keys(w)
            rand_block(0.01, 0.01)

    def mock_click(self, target, ele_num=None):
        """
        将 ``target`` 转换为 web 元素, 并模拟点击
        ele_num 为指定点击哪个元素, 如果为 any, 则触发任意一个

        :param ele_num:
        :param target:
        :return:
        """
        # 如果是 multiple 将首先获取满足条件的所有元素, 并倒序获取最后一个元素.
        if ele_num:
            # 获取所有元素
            elements = self.get_elements(target, multiple=True)
            # ele_num == any , 则任意满足条件点击即可
            if ele_num == 'any':
                # 遍历, 直到任意一个元素点击成功
                for _ in reversed(elements):
                    if self.mock_click(_):
                        return True
                return False

            if isinstance(ele_num, int):
                # 如果指定 num, 则取 min(ele_num, len)
                try:
                    ele_num = min(ele_num, len(elements) - 1)
                    element = elements[ele_num]
                    element.click()
                    return True
                except WebDriverException as _:
                    log.error('({}){}'.format(target, _))
                    return False
            else:
                # 如果不是 ``any`` , 且不是 int 则为非法ele_num
                return False
        else:
            try:
                element = self.get_elements(target)
                element.click()
                return True
            except WebDriverException as _:
                if self.log_who['click']:
                    log.error('({}){}'.format(target, _))
                return False

    def mock_click_next_page(self, dat):
        btn = self.get_elements(dat)
        rand_block(0.1, 0.2)
        return self.mock_click(btn)

    def mock_key_down(self, target, key_press_times):
        """
            key_press_times => >= 0 则 DOWN, 否则 UP

        :param target:
        :type target:
        :param key_press_times:
        :type key_press_times: int
        :return:
        :rtype:
        """
        key = Keys.DOWN
        if key_press_times < 0:
            key = Keys.UP

        for i in range(abs(key_press_times)):
            rand_block(0.1, 0.01)
            target.send_keys(key)

    def switch_to_frame(self, dat):
        self.driver.switch_to.frame(self.get_elements(dat))

    def switch_to_default(self):
        self.driver.switch_to.default_content()

    def mock_input(self, dat, term='', clear=True, mock_input_change='', submit=False):
        """
            输入 term 到 input:ele(dat) 元素
            如果 ``mock_input_change`` 不为空, 则该 input 不能保留原始值, 可以输入一个值, 然后清空.

        - clear 清空input的元素
        - submit 提交

        :param dat:
        :type dat: dict
        :param term:
        :type term: str
        :param submit:
        :type submit: bool
        :param clear:
        :type clear: bool
        :param mock_input_change: 针对不能保留原来值的输入框
        :type mock_input_change: str
        :return:
        :rtype:
        """
        target = self.get_elements(dat)
        if clear:
            target.clear()
            self._mock_input(target, Keys.BACKSPACE * 50)

        if mock_input_change:
            self._mock_input(target, mock_input_change)
            rand_block(0.01, 0.01)
            self._mock_input(target, Keys.BACKSPACE * (len(mock_input_change) + 2))

        if term:
            self._mock_input(target, term)

        if submit:
            rand_block(0.01, 0.1)
            target.send_keys(Keys.ENTER)
            rand_block(0.01, 0.1)

    def scroll_by_key_down(self, dat, distance_togo):
        """ 模拟 page_up/down 方式来滚动

        :param dat:
        :type dat:
        :param distance_togo:
        :type distance_togo:
        :return:
        :rtype:
        """
        try:
            target = self.get_elements(dat)
            distance_done = 0
            while distance_done < distance_togo:
                chance = random.random()
                if chance < 0.05:
                    rand_block(0.5, 0.1)
                    continue
                distance = rand_pareto_float(100, 10)
                if chance >= 0.95:
                    distance = -distance
                key_press_times_ = distance // PIXELS_PER_DOWN_KEY
                self.mock_key_down(target, key_press_times_)
                distance_done += key_press_times_ * PIXELS_PER_DOWN_KEY
        except Exception as _:
            log.error(_)
            raise

    def scroll_smooth(self, x_dist, y_dist, x_neg, y_neg, two_paned_scroll='window', element=True):
        try:
            src_str = 'window'
            if two_paned_scroll != src_str:
                if element:
                    src_str = ''.join(['document.getElementById(\'', two_paned_scroll, '\')'])
                else:
                    src_str = ''.join(['document.getElementsByClassName(\'', two_paned_scroll, '\')[0]'])

            scroll_x = '.scrollBy(-8,0);' if x_neg else '.scrollBy(8,0);'
            scroll_y = '.scrollBy(0,-8);' if y_neg else '.scrollBy(0,8);'

            for i in range(x_dist // 8):
                self.driver.execute_script(src_str + scroll_x)
                rand_block(0, 0.001)

            for i in range(y_dist // 8):
                self.driver.execute_script(src_str + scroll_y)
                rand_block(0, 0.001)

        except WebDriverException as e:
            log.warning(e)
            raise

    @dec.catch(True, WebDriverException, do_raise=Exception)
    def scroll_to_element(self, dat, tow_paned_scroll='window', element=True, close_in=0):
        # scroll down to element
        target = self.get_elements(dat)
        # 已完成距离
        distance_done = 0
        # 待完成距离

        w_size = self.driver.get_window_size()
        # log.debug('y total need to go: {}'.format(target.location['y']))
        # from center to element y
        distance_togo = target.location['y'] - w_size['height'] // 2
        # y // 3 防止滚动过多
        if not close_in:
            close_in = w_size['height'] // 3

        while distance_done < distance_togo:
            chance = random.random()
            if chance < 0.1:
                # 在0.1 的概率下等待一定时间
                mini_ = min(0.01 / chance, 0.5)
                rand_block(mini_, 0.1)
            else:
                # 多数情况下向下 scroll
                y_neg, distance = False, rand_pareto_float(100, 10)
                # 以很小的概率向上 scroll
                if chance > 0.96:
                    y_neg, distance = True, -rand_pareto_float(100, 10)

                # log.debug('Each time: {}/{}/{}'.format(distance_togo, distance_done, distance))
                distance = min(distance_togo - distance_done + close_in, distance)
                distance_done += distance
                self.scroll_smooth(0, int(abs(distance)), False, y_neg, tow_paned_scroll, element)


class ChromeRobot(Robot):
    def __init__(self, driver=None, **kwargs):
        if not driver:
            driver = self.chrome_driver(**kwargs)
        super().__init__(driver, **kwargs)

    def chrome_driver(self, **kwargs):
        """
        supported:
            to = timeout, 30
            images = load images, 0
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')

        prefs = {"profile.managed_default_content_settings.images": kwargs.get('images', 0)}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options=options)
        driver.set_window_size(1366, 768)
        driver.set_window_position(32, 0)
        driver.set_page_load_timeout(kwargs.get('to', 30))
        return driver

    def chrome_driver_old(self, **kwargs):
        options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": kwargs.get('images', 0)}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options=options)
        return driver


class ASite(object):
    """ The base of a site crawler """

    def __init__(self, driver, **kwargs):
        # self.driver = driver
        self.robot = ChromeRobot(driver, **kwargs)
        self.base = {}

    def has_next_page(self, current_page_num=0):
        np = len(self.robot.get_elements(self.base.get('next_page'), multiple=True))
        return np >= 1

    # @dec.catch(True, IndexError)
    def goto_next(self):
        next_page = self.robot.get_elements(self.base['next_page'], multiple=True)[-1]
        self.robot.scroll_to_element(next_page)
        self.robot.mock_click_next_page(next_page)

    def mock_popovers(self):
        for d in self.base['popovers']:
            if self.robot.has_element(d, skip_log=True):
                rand_block(1, 1, slow_mode=(2, 5))
                self.robot.mock_click(d)
                break

    def _check_params(self, *args, **kwargs):
        """ 检查参数信息是否匹配 """
        terms = kwargs.get('terms')
        if not terms:
            raise crawler.CrawlerParamsError('Terms needed!')

        if not isinstance(terms, list):
            terms = [terms]
        if len(terms) != len(self.base['terms']):
            raise crawler.CrawlerParamsError('args length must match base[terms]')

    def mock_input_submit(self, *args, **kwargs):
        """ 模拟输入参数, 然后提交 """
        if not kwargs.get('skip_load'):
            self.robot.load_page(self.base['homepage'])

        terms = kwargs.get('terms')
        for i, q in enumerate(self.base['terms']):
            if i < len(self.base['terms']) - 1:
                self.robot.mock_input(q, terms[i], clear=True)
            else:
                self.robot.mock_input(q, terms[i], clear=True, submit=True)

    def mock_human_crawl(self, *args, **kwargs):
        """ 模拟 human 操作方式爬取站点 """
        self._check_params(*args, **kwargs)
        self.mock_input_submit(*args, **kwargs)
        return self.response_result(**kwargs)

    def response_result(self, **kwargs):
        # yield self.driver.page_source, self.driver.current_url, 1
        # after mock submit, the first page is crawled.
        # so start@ index of 1, and yield first
        # when running over, use else to yield the last page.
        page_togo = kwargs.get('page_togo', 20)
        for page_done in range(1, page_togo):
            yield self.robot.driver.page_source, self.robot.driver.current_url, page_done
            # click any popups
            self.mock_popovers()

            if self.has_next_page(page_done):
                self.goto_next()
            else:
                # 如果无下一页, 直接退出
                log.debug('page {} is the last result page!'.format(page_done))
                break
        else:
            log.debug('all done {}'.format(page_done))
            yield self.robot.driver.page_source, self.robot.driver.current_url, page_togo
