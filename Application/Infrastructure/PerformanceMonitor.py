
from dataclasses import dataclass
from logging import Logger
import threading
import time
import psutil
import asyncio
from asyncio import Task
from Config.Config import Config
from Infrastructure.NetworkChecker import NetworkChecker


@dataclass
class PerformanceInfo:
    CpuUsage: float
    MemoryUsage: float
    HddUsage: float
    CpuTemperature: float


class CancellationToken:
    CancellationRequested: bool = False


class PerformanceMonitor:

    def __init__(self, config: Config, networkChecker: NetworkChecker, logger: Logger):
        self.myConfig = config
        self.myNetworkChecker = networkChecker
        self.myLogger = logger

    def Start(self):

        self.myThread = threading.Thread(target=self.MonitorPerformance, daemon=True)
        self.myThread.start()

    def Stop(self):
        self.myCancellationToken.CancellationRequested = True

    def MonitorPerformance(self):
        self.myCancellationToken = CancellationToken()
        self.myLogger.info("Starting Performance Monitoring")
        try:
            while True:
                info = PerformanceMonitor.GetPerformanceInfo()
                internetAvailableText = "Connected to internet" if self.myNetworkChecker.InternetAvailable() else "Disconnected to internet"
                log = f'CPU={info.CpuUsage:3.1f}%,{info.CpuTemperature:3.1f}°C RAM={info.MemoryUsage:3.1f}% HDD={info.HddUsage:3.1f}%'
                self.myLogger.info(f'{log} {internetAvailableText}')
                if PerformanceMonitor.HardwareSituationIsCritical(info):
                    raise RuntimeError(f"Hardware situation is critical {PerformanceMonitor.GetPerformanceInfo()}")
                time.sleep(self.myConfig.LoggingConfig.PerformanceMonitorLoggingInterval.total_seconds())
                if self.myCancellationToken.CancellationRequested:
                    break
        except asyncio.CancelledError as e:
            self.myLogger.info('PerformanceMonitor was stopped')

    @classmethod
    def GetCpuTemperature(cl):
        f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        raw = f.read().rstrip()
        result = float(raw[:-3] + "." + raw[-3:])
        f.close()
        return result

    @classmethod
    def GetCpuLoad(cl):
        return psutil.cpu_percent()
    
    @classmethod
    def GetPerformanceInfo(cl):
        CpuUsage = psutil.cpu_percent()
        MemUsage = psutil.virtual_memory().percent
        HddUsage = psutil.disk_usage('/').percent
        CpuTemp = cl.GetCpuTemperature()
        return PerformanceInfo(CpuUsage, MemUsage, HddUsage, CpuTemp)

    @classmethod
    def HardwareSituationIsCritical(cl, performanceInfo: PerformanceInfo) -> bool:
        return performanceInfo.CpuUsage < 1 or performanceInfo.MemoryUsage > 95
