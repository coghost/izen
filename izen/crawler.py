# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/8/21 10:15'
__description__ = '''
### multiple UA
- [user-agents](https://github.com/selwin/python-user-agents)
- [async-requests](https://blog.csdn.net/dashoumeixi/article/details/81085141)

'''

from dataclasses import dataclass
import os
import sys
import random
import time
import json
from http import cookiejar
from urllib import parse

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import tqdm
import asyncio
import requests
from bs4 import BeautifulSoup as BS
from izen import helper, dec
import logzero
from logzero import logger as zlog


class CrawlerError(Exception):
    pass


class CrawlerParamsError(CrawlerError):
    pass


@dataclass
class UA:
    """
    tons of user agents
        UA.mac_chrome__
        UA.mac_safari__
    """
    android_firefox_aurora__: str = 'Mozilla/5.0 (Android; Mobile; rv:27.0) Gecko/27.0 Firefox/27.0'
    blackberry_bold_touch__: str = 'Mozilla/5.0 (BlackBerry; U; BlackBerry 9930; en-US) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.0.0.241 Mobile Safari/534.11+'
    blackberry_bold__: str = 'BlackBerry9700/5.0.0.862 Profile/MIDP-2.1 Configuration/CLDC-1.1 VendorID/331 UNTRUSTED/1.0 3gpp-gba'
    blackberry_torch__: str = 'Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; zh-TW) AppleWebKit/534.8+ (KHTML, like Gecko) Version/6.0.0.448 Mobile Safari/534.8+'
    chromebook__: str = 'Mozilla/5.0 (X11; CrOS i686 0.12.433) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.77 Safari/534.30'
    galaxy_s3__: str = 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
    galaxy_tab__: str = 'Mozilla/5.0 (Linux; U; Android 2.2; en-us; SCH-I800 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
    google_bot__: str = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    ie_touch__: str = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)'
    ie__: str = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'
    ipad__: str = 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'
    iphone__: str = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
    j2me_opera__: str = 'Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (J2ME/22.478; U; en) Presto/2.5.25 Version/10.54'
    kindle_fire__: str = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.1.0-80) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true'
    mac_safari__: str = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2'
    mac_chrome__: str = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    nexus_7__: str = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'
    nokia_n97__: str = 'Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/12.0.024; Profile/MIDP-2.1 Configuration/CLDC-1.1; en-us) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.12344'
    outlook_usa_string: str = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/6.0; Microsoft Outlook 15.0.4420)'
    playbook__: str = 'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.0.1; en-US) AppleWebKit/535.8+ (KHTML, like Gecko) Version/7.2.0.1 Safari/535.8+'
    thunderbird__: str = 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Thunderbird/38.2.0 Lightning/4.0.2'
    ubuntu_firefox__: str = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1'
    windows_ie__: str = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'
    windows_phone__: str = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; SAMSUNG; SGH-i917)'
    windows_rt__: str = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)'


class ParseHeaderFromFile(object):
    def __init__(self, fpth='headers.txt', raw='', use_cookies=True):
        self.fpth = fpth
        self.url = ''
        self.cookies = {}
        self.headers = {}
        self.parse_headers(use_cookies, raw)

    def parse_headers(self, use_cookies, raw):
        """
        analyze headers from file or raw messages

        :return: (url, dat)
        :rtype:
        """
        if not raw:
            packet = helper.to_str(helper.read_file(self.fpth))
        else:
            packet = raw
        dat = {}

        pks = [x for x in packet.split('\n') if x.replace(' ', '')]
        url = pks[0].split(' ')[1]

        for i, cnt in enumerate(pks[1:]):
            arr = cnt.split(':')
            if len(arr) < 2:
                continue
            arr = [x.replace(' ', '') for x in arr]
            _k, v = arr[0], ':'.join(arr[1:])
            dat[_k] = v

        if use_cookies:
            try:
                self.fmt_cookies(dat.pop('Cookie'))
            except:
                pass
        self.headers = dat
        self.url = 'https://{}{}'.format(self.headers.get('Host'), url)
        return url, dat

    def fmt_cookies(self, ck):
        """
        :param ck:
        :type ck:
        :return:
        :rtype:
        """
        cks = {}
        for c in ck.split(';'):
            a = c.split('=')
            if len(a) != 2:
                continue
            cks[a[0].replace(' ', '')] = a[1].replace(' ', '')
        self.cookies = cks


class Crawler(object):
    def __init__(self, site_init_url, base_dir='/tmp/crawler', overwrite=False, timeout=5, cache=None,
                 force_spawn=False, **kwargs):
        """ init the crawler with cache supported

        :param cache: use cache
        :type cache: dict
        :param site_init_url: any url of the site
        :type site_init_url: str
        """
        logzero.loglevel(kwargs.get('log_level', 10))
        # this header is used for fetch the dst url headers and cookies, but may enough for some site.
        self.__header__ = {
            'User-Agent': UA.mac_chrome__
        }
        # headers for crawl purpose
        self.headers = {
            'get': {},
            'post': {},
            'json': {},
        }
        self.timeout = timeout

        self.result = {
            'start_tm': helper.unixtime(),
            'end_tm': helper.unixtime(),
            'ok': 0,
            'fail': 0,
            'skip': 0,
        }
        self.overwrite = overwrite
        self.sess = requests.session()

        # domain for now only used for setup the base dir
        self.homepage = ''
        self.domain = ''

        # if cache.enabled each time crawled a page, save it to cache dir
        self.cache = cache if cache else {
            'base': base_dir,
            'site_dir': '',
            'site_raw': '',
            'site_media': '',
            'enabled': True,
        }

        self.spawn(site_init_url, force_spawn)

    def spawn(self, url, force_spawn=False):
        """use the url for creation of domain and fetch cookies

        - init cache dir by the url domain as ``<base>/domain``
        - save the cookies to file ``<base>/domain/cookie.txt``
        - init ``headers.get/post/json`` with response info
        - init ``site_dir/site_raw/site_media``

        :param url:
        :type url:
        :param force_spawn:
        :type force_spawn:
        :return:
        :rtype:
        """
        _url, domain = self.get_domain_home_from_url(url)
        if not _url:
            return False

        self.cache['site_dir'] = os.path.join(self.cache['base'], self.domain)
        for k in ['raw', 'media']:
            self.cache['site_' + k] = os.path.join(self.cache['site_dir'], k)
            helper.mkdir_p(self.cache['site_' + k], True)

        ck_pth = os.path.join(self.cache['site_dir'], 'cookie.txt')
        helper.mkdir_p(ck_pth)

        name = os.path.join(self.cache['site_raw'], 'homepage')
        # not force spawn and file ok
        if not force_spawn and helper.is_file_ok(name):
            # zlog.debug('{} exist!'.format(name))
            self.sess.cookies = self.load_cookies(ck_pth)
            return True
        else:
            zlog.debug('{} not exist!'.format(name))

        res = self.sess.get(url, headers=self.__header__)
        if res.status_code != 200:
            return False
        if res:
            helper.write_file(res.content, name)
        # self.load(url)

        for k, v in self.headers.items():
            self.headers[k] = res.request.headers

        self.dump_cookies(cookies=self.sess.cookies, save_to=ck_pth)

        return True

    def get_domain_home_from_url(self, url):
        """ parse url for domain and homepage

        :param url: the req url
        :type url: str
        :return: (homepage, domain)
        :rtype:
        """
        p = parse.urlparse(url)
        if p.netloc:
            self.domain = p.netloc
            self.homepage = '{}://{}'.format(p.scheme, p.netloc)
            return self.homepage, p.netloc
        else:
            return '', ''

    @staticmethod
    def dump_cookies(cookies, save_to):
        _cookie_jar = cookiejar.LWPCookieJar(save_to)
        requests.utils.cookiejar_from_dict({
            c.name: c.value
            for c in cookies
        }, _cookie_jar)
        _cookie_jar.save(save_to, ignore_discard=True, ignore_expires=True)

    @staticmethod
    def load_cookies(ck_pth):
        if not helper.is_file_ok(ck_pth):
            return
        _cookie_jar = cookiejar.LWPCookieJar(ck_pth)
        _cookie_jar.load(ck_pth, ignore_expires=True, ignore_discard=True)
        _cookies = requests.utils.dict_from_cookiejar(_cookie_jar)
        cookies = requests.utils.cookiejar_from_dict(_cookies)
        return cookies

    def map_url_to_cache_id(self, url):
        """use of the url resource location as cached id

        e.g.: ``<domain>/foo/bar/a.html => <base>/domain/foo/bar/a.html``

        - map the url to local file

        :param url:
        :type url:
        :return:
        :rtype:
        """
        base, _ = self.get_domain_home_from_url(url)

        if base == '':
            # invalid url
            _sub_page = ''
        elif base == url or base + '/' == url:
            # homepage
            _sub_page = 'homepage'
        else:
            # sub page
            _sub_page = url.replace(base, '').split('/')
            _sub_page = '/'.join([x for x in _sub_page if x])

        if _sub_page:
            full_name = os.path.join(self.cache['site_raw'], _sub_page)
            return full_name
        else:
            return _sub_page

    @staticmethod
    def load_from_cache(name):
        if not helper.is_file_ok(name):
            return ''
        return helper.read_file(name)

    def gen_tasks(self, urls):
        """ according the urls gen {name:'', url:''} dict.
        :param urls:
        :type urls:
        :return:
        :rtype:
        """
        tasks = []
        if isinstance(urls, list):
            for url in urls:
                dat = {
                    'url': url,
                    'name': url.split('/')[-1]
                }
                if not self.overwrite and helper.is_file_ok(dat['name']):
                    self.result['skip'] += 1
                else:
                    tasks.append(dat)
        elif isinstance(urls, dict):
            # {k: v} => k is name, v is url value
            for k, v in urls.items():
                dat = {
                    'url': v,
                    'name': k,
                }
                if not self.overwrite and helper.is_file_ok(dat['name']):
                    self.result['skip'] += 1
                else:
                    tasks.append(dat)
        else:
            raise CrawlerParamsError('urls should be list/dict')
        return tasks


class CommonCrawler(Crawler):
    def __init__(self, bs=None, **kwargs):
        super().__init__(**kwargs)
        # set bs4 parse options
        self.bs = {
            'parser': 'lxml',
            'encoding': 'utf-8'
        }
        if isinstance(bs, dict):
            for k, _ in self.bs.items():
                self.bs[k] = bs.get(k)

    def do_sess_get(self, url):
        """get url by requests synchronized

        :param url:
        :type url:
        :return:
        :rtype:
        """
        try:
            res = self.sess.get(url, headers=self.headers['get'], timeout=self.timeout)
            if res.status_code == 200:
                return res.content
        except (requests.ReadTimeout, requests.ConnectTimeout, requests.ConnectionError) as _:
            zlog.error('failed of: {} with error: {}'.format(url, _))

    def load(self, url, use_cache=True, show_log=False):
        """fetch the url ``raw info``, use cache first, if no cache hit, try get from Internet

        :param url:
        :type url:
        :param use_cache:
        :type use_cache:
        :param show_log:
        :type show_log:
        :return: the ``raw info`` of the url
        :rtype: ``str``
        """
        _name = self.map_url_to_cache_id(url)
        raw = ''
        hit = False

        if use_cache:
            hit = True
            raw = self.load_from_cache(_name)

        if not raw:
            if show_log:
                zlog.debug('from cache got nothing {}'.format(_name))
            raw = self.do_sess_get(url)
            if raw:
                helper.write_file(raw, _name)

        # if not raw:
        #     hit = True
        #     raw = self.load_from_cache(_name)
        if show_log:
            zlog.debug('[{}:{:>8}] get {}'.format('Cache' if hit else 'Net', len(raw), url))
        return raw

    def bs4get(self, url, use_cache=True, show_log=False, is_json=False):
        raw = self.load(url, use_cache, show_log)
        if not raw:
            return
        if is_json:
            return json.loads(helper.to_str(raw))
        return BS(raw, self.bs['parser'], from_encoding=self.bs['encoding'])

    def do_sess_post(self, url, data, headers=None, ret='json'):
        res = self.sess.post(url, data=data, headers=headers or self.headers['post'], timeout=self.timeout)
        if res.status_code == 200:
            if ret == 'json':
                return res.json()
            return res.content

    def load_post(self, url, data, headers=None, ret='json', use_cache=True, show_log=False):
        name = self.map_url_to_cache_id(url)
        if data:
            keys = sorted(data.keys())
            for k in keys:
                name += '{}{}'.format(k, data[k])

        raw = ''
        hit = False

        if use_cache:
            hit = True
            raw = self.load_from_cache(name)

        if not raw:
            if show_log:
                zlog.debug('cache miss: ({})'.format(name))
            raw = self.do_sess_post(url, data, headers, ret)
            if raw:
                if ret == 'json':
                    raw = json.dumps(raw)
                zlog.debug('write ({}) to {}'.format(len(raw), name))
                helper.write_file(raw, name)

        if show_log:
            zlog.debug('[cache {}:{:>8}] post {}'.format('hit' if hit else 'miss', len(raw), name))
        return raw

    def bs4post(self, url, data, headers=None, ret='json', use_cache=True, show_log=False):
        raw = self.load_post(url, data=data, ret=ret,
                             use_cache=use_cache, headers=headers,
                             show_log=show_log)
        if ret == 'json':
            return json.loads(raw)
        else:
            return raw

    def sync_save(self, res, overwrite=False):
        """ save ``res`` to local synchronized

        :param res: {'url': '', 'name': ''}
        :type res: dict
        :param overwrite:
        :type overwrite:
        :return:
        :rtype: BeautifulSoup
        """
        if not isinstance(res, dict):
            raise CrawlerParamsError('res must be dict')

        url_, file_name = res.get('url', ''), res.get('name', '')
        if not url_ or not file_name:
            raise CrawlerParamsError('url&name is needed!')

        # log.debug('Sync {}'.format(res.get('name')))
        # not overwrite and file exists
        if not overwrite and helper.is_file_ok(file_name):
            return True

        cnt = self.do_sess_get(url_)
        # get res failed
        if not cnt:
            return False

        with open(file_name, 'wb') as f:
            f.write(cnt)
        zlog.debug('Sync Done {}'.format(res.get('name')))
        return True


class AsyncCrawler(CommonCrawler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def async_get(self, res):
        loop_ = asyncio.get_event_loop()
        cnt = await loop_.run_in_executor(None, self.do_sess_get, res.get('url'))
        return cnt

    def write_hd(self, file_name, cnt):
        with open(file_name, 'wb') as f:
            f.write(cnt)

    async def crawl_raw(self, res):
        """ crawl the raw doc, and save it asynchronous.

        :param res: {'url','', 'name': ''}
        :type res: ``dict``
        :return:
        :rtype:
        """
        cnt = await self.async_get(res)
        if cnt:
            loop_ = asyncio.get_event_loop()
            await loop_.run_in_executor(None, self.write_hd, res.get('name'), cnt)
            return True
        else:
            return False

    async def _sem_crawl(self, sem, res):
        """ use semaphore ``encapsulate`` the crawl_media \n
        with async crawl, should avoid crawl too fast to become DDos attack to the crawled server
        should set the ``semaphore size``, and take ``a little gap`` between each crawl behavior.

        :param sem: the size of semaphore
        :type sem:
        :param res:
        :type res: dict
        :return:
        :rtype:
        """
        async with sem:
            st_ = await self.crawl_raw(res)
            if st_:
                self.result['ok'] += 1
            else:
                self.result['fail'] += 1

            # take a little gap
            await asyncio.sleep(random.randint(0, 1))

    async def crawl(self, urls, sem):
        """
        :param urls:
        :type urls: list/dict
        :param sem:
        :type sem:
        :return:
        :rtype:
        """
        tasks = [
            self._sem_crawl(sem, x)
            for x in urls
        ]

        tasks_iter = asyncio.as_completed(tasks)

        fk_task_iter = tqdm.tqdm(
            tasks_iter,
            total=len(tasks),
            desc=' ✈',
            # desc='✈ {}/{}'.format(self.result['ok'], self.result['fail'])
        )
        for co_ in fk_task_iter:
            await co_

    def run(self, urls, max_num, preset_pth=''):
        self.result['start_tm'] = helper.unixtime()
        _cwd = os.getcwd()
        try:
            os.chdir(preset_pth or self.cache['site_media'])
            tasks = self.gen_tasks(urls)
        except CrawlerParamsError as _:
            zlog.error(_)
            os.chdir(_cwd)
            return

        sem = asyncio.Semaphore(max_num)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl(tasks, sem))
        loop.close()
        self.result['end_tm'] = helper.unixtime()
        os.chdir(_cwd)
