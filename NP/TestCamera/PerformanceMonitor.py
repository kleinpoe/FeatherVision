
from dataclasses import dataclass
from logging import Logger
import threading
import time
import psutil
import asyncio
from asyncio import Task


@dataclass
class PerformanceInfo:
    CpuUsage: list[float]
    MemoryUsage: float
    HddUsage: float
    CpuTemperature: float
    MegaBytesReceived: float
    MegaBytesSent: float


class CancellationToken:
    CancellationRequested: bool = False


class PerformanceMonitor:

    def __init__(self, loggingIntervalInSeconds):
        self.LoggingIntervalInSeconds = loggingIntervalInSeconds

    def Start(self):
        self.myThread = threading.Thread(target=self.MonitorPerformance, daemon=True)
        self.myThread.start()

    def Stop(self):
        self.myCancellationToken.CancellationRequested = True

    def MonitorPerformance(self):
        self.myCancellationToken = CancellationToken()
        print("Starting Performance Monitoring")
        try:
            while True:
                info = PerformanceMonitor.GetPerformanceInfo()
                log = f'CPU={info.CpuUsage}%,{info.CpuTemperature:3.1f}°C RAM={info.MemoryUsage:3.1f}% HDD={info.HddUsage:3.1f}% Network=[sent:{info.MegaBytesSent:.1f}MB,received={info.MegaBytesReceived:.1f}MB]'
                print(log)
                time.sleep(self.LoggingIntervalInSeconds)
                if self.myCancellationToken.CancellationRequested:
                    break
        except asyncio.CancelledError as e:
            print('PerformanceMonitor was stopped')

    @classmethod
    def GetCpuTemperature(cl):
        f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        raw = f.read().rstrip()
        result = float(raw[:-3] + "." + raw[-3:])
        f.close()
        return result

    @classmethod
    def GetCpuLoad(cl):
        return psutil.cpu_percent(percpu=True)
    
    @classmethod
    def GetPerformanceInfo(cl):
        CpuUsage = psutil.cpu_percent(percpu=True)
        MemUsage = psutil.virtual_memory().percent
        HddUsage = psutil.disk_usage('/').percent
        CpuTemp = cl.GetCpuTemperature()
        MegaBytesReceived = psutil.net_io_counters().bytes_recv / 1E6
        MegaBytesSent = psutil.net_io_counters().bytes_sent / 1E6
        return PerformanceInfo(CpuUsage, MemUsage, HddUsage, CpuTemp, MegaBytesReceived, MegaBytesSent)
