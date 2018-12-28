# -*- encoding: UTF-8 -*-
import socket
import time

from queue import Queue, Empty
from threading import Thread, Lock

from Socketer.utils import get_logger, SocketConstants


class SocketClient(SocketConstants):

    def __init__(self, host: str, port: int = 33331, bufsize: int = 1024,
                 time_out: float = 1.0, msg_encoding: str = 'utf-8'):
        self.log = get_logger(self.__class__.__name__)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(time_out)
        self.msg_in = Queue()
        self.msg_out = Queue()
        self.msg_lock = Lock()

        self.__host__ = host
        self.__port__ = port
        self.__msg_encoding__ = msg_encoding
        self.__bufsize__ = bufsize

        self.__send_thread__ = None
        self.__send_tag__ = False

        self.__receive_thread__ = None
        self.__receive_tag__ = False

    def __send_msg__(self):
        while self.__send_tag__ is True:
            try:
                msg_obj = self.msg_out.get(timeout=1)
                self.socket.sendall(msg_obj.encode(self.__msg_encoding__))
                self.log.debug('message to {}: {}'.format(self.__host__, msg_obj))
            except Empty:
                continue

    def __receive_msg__(self):
        while self.__receive_tag__ is True:
            try:
                msg = self.socket.recv(self.__bufsize__).decode(self.__msg_encoding__)
                if len(msg) == 0:
                    continue
                self.log.debug('message from {}: {}'.format(self.__host__, msg))
                if msg == 'SocketExit':
                    break
                else:
                    self.msg_in.put(msg)
            except ConnectionResetError:
                self.socket.connect((self.__host__, self.__port__))
                self.log.info('redo connect to server {}'.format(self.__host__))
            except socket.timeout:
                continue

    def start(self):
        self.log.info('connect to server {}'.format(self.__host__))
        self.socket.connect((self.__host__, self.__port__))

        self.__send_tag__ = True
        self.__send_thread__ = Thread(target=self.__send_msg__, name='send socket message')
        self.__send_thread__.start()
        self.log.debug('message sending started.')

        self.__receive_tag__ = True
        self.__receive_thread__ = Thread(target=self.__receive_msg__, name='receive socket message')
        self.__receive_thread__.start()
        self.log.debug('message receiving started.')

        self.log.info('{} started.'.format(self.__class__.__name__))

    def stop(self):
        self.msg_out.put(self.CLIENT_EXIT_MSG)

        while self.msg_out.empty() is False:
            time.sleep(0.1)
        self.log.debug('all task processed send.')

        self.__send_tag__ = False
        self.__send_thread__.join(5)
        self.log.debug('message sending stopped.')

        self.msg_lock.acquire()
        while self.msg_in.empty() is False:
            time.sleep(0.1)
        self.log.debug('all message received processed.')

        self.__receive_tag__ = False
        self.__receive_thread__.join(10)
        self.log.debug('message receiving stopped.')

        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.log.info('{} stopped.'.format(self.__class__.__name__))


if __name__ == '__main__':
    from Socketer.Server import SocketServer, SocketMessage
    port = 14112
    new_server = SocketServer(port=port)
    new_server.start()
    new_client = SocketClient(socket.gethostname(), port=port)
    new_client.start()
    time.sleep(2)
    try:
        new_client.msg_out.put('test client send')
        s = new_server.msg_in.get()
        new_server.msg_out.put(SocketMessage(s.addr, 'test server response % client receive'))
        s = new_client.msg_in.get()
        new_client.stop()
    except KeyboardInterrupt as e:
        new_server.stop()
        new_client.stop()
        raise e
    finally:
        new_server.stop()
        new_client.stop()
