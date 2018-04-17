izen change log
===============

v1.0.20180402
-------------
- `setup.py`
    + 版本直接放置于 `setup.py` 中实现
    + 修改 `license=GPL`
    + 增加详细描述`README.md`
- `icfg.py` 增加覆盖logger的`Formatter`样式

v1.0.20180301
-------------
- `dec.catch` 增加 `traceback.print_exc()` 打印详细错误日志
- `helper` 增加了 `crc16` 校验
- `dec` 增加了另一种单例实现`@dec.singleton`

v1.0.20180220
-------------
- `izen.py` 添加版本号, 可以 `izen.VERSION` 查看
- 移除 `Crypto` 依赖, 只需要 `pycrypto` 即可
- `helper.py`
    + num_choice/yn_choice 美化输出
    + 实现图片在 `iterm2终端` 输出
    + 实现 timestamp
    + os.popen() 系统命令运行
    + ColorFull 打印输出
    + 多字符替换
    + 表格打印
- `dec.py`
    + 修改了线程实现方式, 并可捕获错误输出
    + catch 增加了指定捕获的错误及提示信息
- `amq.py`
    + 增加了 on_log/on_disconnect 处理

v1.0.20171113
-------------

- `目录结构`
```sh
.
├── CHANGELOG.md
├── README.md
├── izen
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-36.pyc
│   ├── chaos.py
│   ├── dec.py
│   ├── helper.py
│   ├── rds.py
│   └── schedule.py
├── requirements.txt
└── setup.py
```

- `初次创建 izen 库`