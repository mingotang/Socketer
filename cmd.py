# -*- encoding: UTF-8 -*-
"""
Socketer:
    Proudly presented by JM.

Usage:
    sockter -w | --wind
    sockter -h | --help
    sockter -v | --version

Tips:
    Please hit Ctrl-C to exit.

Options:
    -w --wind        Start Wind Server
    -h --help        Show this help message and exit.
    -v --version     Show version.
"""
from docopt import docopt

class sockter():

    def __init__(self, **kwargs):
        self.__args__ = kwargs

    def get_command(self):
        """ 处理命令行参数 """
        if '-w' in self.__args__ or '--wind' in self.__args__:
            from Socketer.ApplyWind import WindServer
            wind_server = WindServer()
            try:
                wind_server.start()
            except KeyboardInterrupt:
                wind_server.stop()
            finally:
                wind_server.stop()
        else:
            pass


def cli():
    """ 入口方法 """
    from Socketer import __version__
    args = docopt(__doc__, version='Socketer {}'.format(__version__))
    sockter(**args).get_command()

if __name__ == '__main__':
    cli()
