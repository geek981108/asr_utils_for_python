import logging
import os


def logger_settings(logger_file_dir=None, logger_file_name=None):
    """
    日志设置，同时输出到文件和屏幕
    :return: logger
    """

    logger = logging.getLogger()
    logging_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    logger.setLevel(logging.DEBUG)

    if logger_file_dir is not None and logger_file_name is not None:
        LOGGING_DIR = os.path.join(logger_file_dir, logger_file_name)
        if not os.path.exists(LOGGING_DIR):
            os.mkdir(LOGGING_DIR)
        f = open(os.path.join(logger_file_dir, logger_file_name), 'w')
        f.close()
        # 输出到文件
        file_handler = logging.FileHandler(f'{LOGGING_DIR}')
        file_handler.setFormatter(logging_formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    # 输出到屏幕
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging_formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(stream_handler)
    return logger
