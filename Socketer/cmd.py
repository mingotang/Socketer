# -*- encoding: UTF-8 -*-
"""
Socketer:
    Proudly presented by JM.

Usage:
    sockter -v | --version
    sockter -h | --help

Tips:
    Please hit Ctrl-C to exit.

Options:
    -h --help        Show this help message and exit.
    -v --version     Show version.
"""
from docopt import docopt

class sockter():

    def __init__(self, **kwargs):
        self.__args__ = kwargs

    def get_command(self):
        """ 处理命令行参数 """
        pass


def cli():
    """ 入口方法 """
    from Socketer import __version__
    args = docopt(__doc__, version='Socketer {}'.format(__version__))
    sockter(**args).get_command()

if __name__ == '__main__':
    cli()
