import socket
import os

class Environment:
    
    @classmethod
    def GetIp(cls) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        ServerIp = s.getsockname()[0]
        return ServerIp
    
    @classmethod
    def GetApplicationDirectory(cls) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RuntimeConfig:
    def __init__(self):
        self.ApplicationDirectory = Environment.GetApplicationDirectory()
        self.Ip = Environment.GetIp()