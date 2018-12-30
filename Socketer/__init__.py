# -*- encoding: UTF-8 -*-

# The version as used in the setup.py and the docs conf.py
__version__ = '0.0.1'


# include Package methods
from Socketer.Client import SocketClient
from Socketer.Server import SocketServer, SocketMessage

from Socketer.ApplyWind import WindClient, WindServer, WSDRes
