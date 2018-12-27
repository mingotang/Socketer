# -*- encoding: UTF-8 -*-
import socket
import time

from queue import Queue, Empty
from threading import Thread

from Socketer.utils import get_logger, SocketConstants


class SocketMessage(object):
    def __init__(self, addr: str, msg: str):
        self.addr = addr
        self.msg = msg


class SocketServer(SocketConstants):

    def __init__(self, port: int = 33331, bufsize: int = 1024,
                 time_out: float = 1.0, msg_encoding: str = 'utf-8', **kwargs):
        self.log = get_logger(
            self.__class__.__name__,
            log_path=kwargs.get('log_path', None),
            log_level=kwargs.get('log_level', 'debug'),
        )

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((socket.gethostname(), port))
        self.socket.settimeout(time_out)

        self.msg_in = Queue()
        self.msg_out = Queue()
        self.server_task = Queue()

        self.__bufsize__ = bufsize
        self.__msg_encoding__ = msg_encoding
        self.__client_dict__ = dict()
        self.__thread_dict__ = dict()

        self.__receive_tag__ = False
        self.__receive_thread__ = None

        self.__server_tag__ = False
        self.__server_thread__ = None

        self.__send_tag__ = False
        self.__send_thread__ = None

        self.__process_tag__ = False
        self.__process_thread__ = None

    def on_new_client(self, sock_addr: str):
        pass

    def __receive_msg__(self, sock_client: socket.socket, sock_addr):
        self.__client_dict__[sock_addr] = sock_client
        self.log.info('connected from: {}.'.format(sock_addr))
        self.on_new_client(sock_addr)

        while self.__receive_tag__ is True:
            msg = sock_client.recv(self.__bufsize__).decode(self.__msg_encoding__)

            if len(msg) == 0:
                continue

            self.log.debug('message from {}: {}'.format(sock_addr, msg))
            if msg == self.CLIENT_EXIT_MSG:
                self.server_task.put(SocketMessage(sock_addr, self.CLIENT_EXIT_MSG))
                sock_client.shutdown(socket.SHUT_RD)
                break
            else:
                self.msg_in.put(SocketMessage(sock_addr, msg))

    def __send_msg__(self):
        while self.__send_tag__ is True:
            try:
                msg_obj = self.msg_out.get(timeout=1)

                if isinstance(msg_obj, SocketMessage):
                    msg_client = self.__client_dict__[msg_obj.addr]
                    assert isinstance(msg_client, socket.socket)
                    msg_client.sendall(msg_obj.msg.encode(self.__msg_encoding__))
                    self.log.debug('message to {}: {}'.format(msg_obj.addr, msg_obj.msg))
                else:
                    raise NotImplementedError
            except Empty:
                continue

    def __server_process__(self):
        while self.__server_tag__ is True:
            try:
                obj = self.server_task.get(timeout=10)
                assert isinstance(obj, SocketMessage)
                if obj.msg == self.CLIENT_EXIT_MSG:
                    sock_client = self.__client_dict__[obj.addr]
                    sock_client.shutdown()
                    self.__client_dict__.pop(obj.addr)
                    if obj.addr in self.__thread_dict__:
                        self.__thread_dict__.pop(obj.addr)
                else:
                    raise NotImplementedError('Unknown SocketServer task {} from {}'.format(obj.msg, obj.addr))
            except Empty:
                continue

    def __msg_process__(self):
        while self.__process_tag__ is True:
            time.sleep(1)

    def start(self):
        self.__send_tag__ = True
        self.__send_thread__ = Thread(target=self.__send_msg__, name='socket message sending service')
        self.__send_thread__.start()
        self.log.debug('message sending started.')

        self.__process_tag__ = True
        self.__process_thread__ = Thread(target=self.__msg_process__, name='socket message process')
        self.__process_thread__.start()
        self.log.debug('message processing started.')

        self.log.debug('start waiting for socket connection.')
        self.socket.listen(10)

        self.__server_tag__ = True
        self.__server_thread__ = Thread(target=self.__server_process__, name='socket server process')
        self.__server_thread__.start()

        self.__receive_tag__ = True
        while self.__receive_tag__ is True:
            try:
                client_sock, client_addr = self.socket.accept()
                receive_thread = Thread(target=self.__receive_msg__, args=(client_sock, client_addr), name=client_addr)
                receive_thread.start()
                self.__thread_dict__[client_addr] = receive_thread
                self.log.debug('message receiving from {} started.'.format(client_addr))
            except socket.timeout:
                continue

        self.log.info('{} started.'.format(self.__class__.__name__))

    def stop(self):
        self.__receive_tag__ = False
        for t_key, t_value in self.__thread_dict__.items():
            t_value.join(10)
            self.log.debug('message receiving from {} stopped.'.format(t_key))

        while self.msg_in.empty() is False:
            time.sleep(0.1)
        self.log.debug('all message received processed.')

        self.__server_tag__ = False
        self.__server_thread__.join()

        while self.msg_out.empty() is False:
            time.sleep(0.1)
        self.log.debug('all task processed send.')

        self.__process_tag__ = False
        self.__process_thread__.join(10)
        self.log.debug('message processing thread stopped.')

        self.__send_tag__ = False
        self.__send_thread__.join()
        self.log.debug('message sending stopped.')

        # close socket client
        for s_key, s_value in self.__client_dict__.items():
            s_value.shutdown(socket.SHUT_RDWR)
            s_value.close()
            self.log.debug('connection from {} closed.'.format(s_key))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

        self.log.info('{} stopped.'.format(self.__class__.__name__))


if __name__ == '__main__':
    new_server = SocketServer()
    try:
        new_server.start()
        s = new_server.msg_in.get()
        print(s)
        new_server.msg_out.put(SocketMessage(s.addr, 'response'))
    except KeyboardInterrupt as e:
        new_server.stop()
        raise e
    finally:
        new_server.stop()