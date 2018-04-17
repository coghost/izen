izen 库
=====

> izen, 封装一些常用功能

## 功能列表

- [x] 配置文件
- [x] 加密解密
- [x] 常用装饰器
- [x] 常用辅助功能
- [x] mqtt通信
- [x] redis通信
- [x] 定期任务

### `icfg.py`

使用样例

```python
>>> import logzero
>>> from logzero import logger as log
>>> from izen.icfg import Conf, LFormatter

>>> pth_cfg = '/tmp/.code.cnf'
>>> cfg = Conf(
...     pth=pth_cfg,
...     dat={
...         'mg.host': '127.0.0.1',
...         'mg.port': 27027,
...         'mg.db': 'test_db',
...         'rds.host': '127.0.0.1',
...         'rds.port': 6379,
...         'rds.db': {
...             'val': 0,
...             'proto': str
...         },
...     }
... ).cfg

>>> if cfg.get('log.enabled', False):
...     logzero.logfile(
...         cfg.get('log.file_pth', '/tmp/.code.log'),
...         maxBytes=cfg.get('log.file_size', 5) * 1000000,
...         backupCount=cfg.get('log.file_backups', 3),
...         loglevel=cfg.get('log.level', 10),
...     )
...
>>> bagua = '🍺🍻♨️️😈☠'
>>> formatter = LFormatter(bagua)
>>> logzero.formatter(formatter)
>>>
>>> log.debug('hi')
 🍺 D 180417 16:36:05 <stdin>:1 | hi
>>> log.info('hi')
 🍻 I 180417 16:37:21 <stdin>:1 | hi
>>> log.warning('hi')
 ♨ W 180417 16:37:35 <stdin>:1 | hi
>>> log.error('hi')
 ️ E 180417 16:37:41 <stdin>:1 | hi
```

### 装饰器

i.e. `dec.catch`, 自动捕获函数内程序错误, 并保证其他函数可以正常运行

```python
>>> from izen import dec
>>>
>>>
>>> @dec.catch(True, ZeroDivisionError)
... def terr():
...     print('divide by 0')
...     print(1 / 0)
...     print('i can not go here.')
...
>>>
>>> def t():
...     terr()
...     print('but i can go here.')
...
>>> t()
divide by 0
[E 180417 16:25:41 dec:457] <stdin>(1)>terr: has err(division by zero)
Traceback (most recent call last):
  File "/Users/lihe/pan.weiyun/tinyc/smartwear/izen/izen/dec.py", line 452, in wrapper_
    return fn(*args, **kwargs)
  File "<stdin>", line 4, in terr
ZeroDivisionError: division by zero
but i can go here.
```

