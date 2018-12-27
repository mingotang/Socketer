# -*- encoding: UTF-8 -*-
import logging


class SocketConstants:
    CLIENT_EXIT_MSG = 'ClientSocketExit'


__log_leval_map__ = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


def get_logger(module_name: str, log_path: str = None, log_level=logging.DEBUG):
    if isinstance(log_level, int):
        log_level = log_level
    elif isinstance(log_level, str):
        try:
            log_level = __log_leval_map__[log_level]
        except KeyError:
            raise ValueError('param log_level should be in range {} but got {}.'.format(
                str(list(__log_leval_map__.keys())), str(log_level),
            ))
    else:
        raise ValueError('param log_level should be in int/str but got {} with value {}.'.format(
            type(log_level), str(log_level)
        ))

    logger = logging.Logger(module_name, log_level)

    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logging.Formatter('%(asctime)s %(module)s %(levelname)s: %(message)s'))
    screen_handler.setLevel(log_level)
    logger.addHandler(screen_handler)

    if log_path is not None:
        import os
        if not isinstance(log_path, str):
            raise ValueError('param log_path should be in type str but got {}'.format(type(log_path)))
        folder_path = os.path.split(log_path)[0]

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(filename)s %(funcName)s %(lineno)d:  %(levelname)s, %(message)s'
        ))
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    return logger
