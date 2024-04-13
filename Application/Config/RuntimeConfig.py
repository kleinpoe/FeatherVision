import fcntl
import json
from logging import Logger
import socket
import os
import struct
from subprocess import check_output

class Environment:

    def GetIp(self) -> str:
        try:
            ip = check_output(['hostname', '-I']).decode('utf-8').split(' ')[0]
            return ip
        except Exception as e:
            print(f'Failed to retrieve local ip adress of device: {e}')
            raise e
            
    def GetApplicationDirectory(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RuntimeConfig:
    def __init__(self, environment: Environment):
        self.ApplicationDirectory = environment.GetApplicationDirectory()
        self.Ip = environment.GetIp()