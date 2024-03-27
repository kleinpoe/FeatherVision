
import asyncio

from Config.RuntimeConfig import RuntimeConfig
from Config.Config import Config
from Infrastructure.LoggerFactory import LoggerFactory
from Infrastructure.NetworkChecker import NetworkChecker
from Infrastructure.PerformanceMonitor import PerformanceMonitor


config = Config(RuntimeConfig())
logger = LoggerFactory(config).CreateLogger()
networkChecker = NetworkChecker(logger)
performanceMonitor = PerformanceMonitor(config,networkChecker,logger)

logger.info(performanceMonitor.GetPerformanceInfo())