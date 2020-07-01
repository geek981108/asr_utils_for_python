# asr_urils for Python

# 作用
使用它思ASR引擎转写wav为文字

# 使用方法
1. 安装 whl
2. 在代码中使用即可

# 使用示例
```python
from asr_utils.asr_utils import SendAudio
send_audio = SendAudio(filename='test.wav', asr_uri='ws://47.93.120.246:18080/client/ws/speech')
# 设置并发数量，不设置默认为1
send_audio.set_concurrent(1)
# 设置log文件输出路径，默认不输出log文件
send_audio.set_log_file_dir('log', 'log.txt')
send_audio.send()
```

# TODO
1. 命令行集成