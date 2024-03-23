import netifaces
import os

class Environment:
    
    @classmethod
    def GetIp(cls) -> str:
        gw = netifaces.gateways()
        return gw['default'][netifaces.AF_INET][0]
    
    @classmethod
    def GetApplicationDirectory(cls) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RuntimeConfig:
    def __init__(self):
        self.ApplicationDirectory = Environment.GetApplicationDirectory()
        self.Ip = Environment.GetIp()