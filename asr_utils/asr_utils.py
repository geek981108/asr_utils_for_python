import asyncio
import json
import threading
import websockets
from .logger import logger_settings


class SendAudio:

    def __init__(self, filename, asr_uri):
        """
        :param filename: 音频文件名
        :param asr_uri: ASR 地址
        """
        self.filename = filename
        self.asr_uri = asr_uri
        self.log_file_dir = None
        self.log_file_name = None
        self.concurrent = None

    def set_log_file_dir(self, log_file_dir, log_file_name):
        """
        设置log文件路径和文件名
        :param log_file_dir: log文件路径
        :param log_file_name: log文件名
        :return:
        """
        self.log_file_dir = log_file_dir
        self.log_file_name = log_file_name

    def set_concurrent(self, concurrent):
        """
        设置并发数量
        :param concurrent: 并发数量
        :return:
        """
        self.concurrent = concurrent

    def is_need_log_file(self):
        """
        判断是否需要本地存储log
        :return:
        """
        if self.log_file_dir is not None:
            return logger_settings(self.log_file_dir, self.log_file_name)
        else:
            return logger_settings()

    async def send_audio(self):

        """
        发送音频到ASR
        :return: 语音转文字
        """
        logger = self.is_need_log_file()
        async with websockets.connect(self.asr_uri) as ws:
            user_input = ''
            with open(self.filename, 'rb') as f:
                await ws.send(f)
                await ws.send('EOS')
                while True:
                    try:
                        recv = await ws.recv()
                        recv = recv.encode('utf-8').decode('unicode_escape')
                        recv = json.loads(recv)
                        logger.info(recv)
                        try:
                            user_input = recv['result']['hypotheses'][0]['transcript']
                            logger.info('用户输入：' + user_input)
                        except KeyError:
                            pass
                    except:
                        await ws.close()
                        break
            return user_input

    def create_loop(self):
        """
        并发时，每一个thread需要跑在一个loop中
        :return:
        """
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return asyncio.get_event_loop().run_until_complete(self.send_audio())

    def send(self):
        threads = []
        if self.concurrent is None:
            return self.create_loop()
        else:
            for i in range(self.concurrent):
                threads.append(threading.Thread(target=self.create_loop))
            for item in threads:
                item.start()
