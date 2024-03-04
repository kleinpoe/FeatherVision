

from Application.Config.Config import Config
from Application.Infrastructure.LoggerFactory import LoggerFactory
from Application.Infrastructure.NetworkChecker import NetworkChecker
from Application.Infrastructure.PerformanceMonitor import PerformanceMonitor


config = Config()
logger = LoggerFactory(config).CreateLogger()
networkChecker = NetworkChecker(logger)
performanceMonitor = PerformanceMonitor(config,networkChecker,logger)

logger.info(performanceMonitor.GetPerformanceInfo())