import asyncio
import json
import threading
import websockets
from logger import logger_settings


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
        self.concurrent = 1
        self.need_all = None

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

    def set_return_all(self, need_all):
        """
        设置返回全部信息，默认为返回经过处理后的文字信息
        """
        self.need_all = need_all

    def is_need_log_file(self):
        """
        判断是否需要本地存储log
        :return:
        """
        if self.log_file_dir is not None:
            return logger_settings(self.log_file_dir, self.log_file_name)
        else:
            return logger_settings()

    async def send_audio(self, file):

        """
        发送音频到ASR
        :return: 语音转文字
        """
        logger = self.is_need_log_file()
        async with websockets.connect(self.asr_uri) as ws:
            user_input = None
            with open(file, 'rb') as f:
                await ws.send(f)
                await ws.send('EOS')
                while True:
                    try:
                        recv = await ws.recv()
                        recv = recv.encode('utf-8').decode('unicode_escape')
                        recv = json.loads(recv)
                        logger.info(recv)
                        try:
                            is_complete_translate = recv['result']['hypotheses'][0]['transcript']
                            if self.need_all is None:
                                user_input = []
                                for item in recv['result']['hypotheses']:
                                    user_input.append(item['transcript'])
                            else:
                                user_input = recv['result']['hypotheses']
                        except KeyError:
                            pass
                    except websockets.ConnectionClosedError:
                        if ws.close_code == 1005:
                            await ws.close()
                            break
                        else:
                            raise websockets.ConnectionClosedError
            logger.info('用户输入：' + str(user_input))
            return user_input

    def create_loop(self, file_name):
        """
        并发时，每一个thread需要跑在一个loop中
        :return:
        """
        new_loop = asyncio.new_event_loop()
        new_loop.create_task(self.send_audio())
        # asyncio.set_event_loop(new_loop)
        asyncio.get_event_loop().run_until_complete(self.send_audio(file_name))
        return tuple()

    def send(self):
        # threads = []
        # if self.concurrent is None:
        #     return self.create_loop()
        # else:
        #     for i in range(self.concurrent):
        #         threads.append(threading.Thread(target=self.create_loop))
        #     for item in threads:
        #         item.start()

        if type(self.filename) is str:
            self.send_audio(self.filename)
        elif type(self.filename) is list:
            concurrent_list = \
                [self.filename[i:i + self.concurrent] for i in range(0, len(self.filename), self.concurrent)]
            for item in concurrent_list:
                threads = []
                for file in item:
                    threads.append(threading.Thread(target=self.create_loop, args={file}))
                for thread in threads:
                    thread.start()



send_audio = SendAudio(filename='test.wav', asr_uri='ws://47.93.120.246:18080/client/ws/speech')
# 设置并发数量，不设置默认为1
send_audio.set_concurrent(1)
# 设置log文件输出路径，默认不输出log文件
send_audio.set_log_file_dir('./log', 'log.txt')
send_audio.set_return_all(True)
a = send_audio.send()
# print('aaaa' + a)
