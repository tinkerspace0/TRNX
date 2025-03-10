# core/plugin/data_plugin.py
from abc import abstractmethod
from typing import Dict, List
from core.plugin.plugin_base import Plugin
from core.debug.profiler import Profiler

profile = Profiler.profile


class DataPlugin(Plugin):
    """
    Abstract Data Processing Plugin for extracting meaningful informations out of raw market data.
    """

class Indicator(DataPlugin):
    """
    Abstract Indicator Plugin for generating technical indicators from raw market data.
    """
    @profile
    @abstractmethod
    def compute(self, data: List[List[float]]) -> List[float]:
        pass

class Feature(DataPlugin):
    """
    Abstract Feature Plugin for generating features from raw market data.
    """
    @profile
    @abstractmethod
    def compute(self, data: List[List[float]]) -> List[float]:
        pass