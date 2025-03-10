from abc import ABC, abstractmethod
from core.plugin.plugin_base import Plugin

class SignalPlugin(Plugin):
    """
    Base class for signal plugins.
    Provides an interface for generating a trading signal.
    """

class Strategy(SignalPlugin):
    """
    Base class for trading strategies.
    Extends SignalPlugin with methods for executing trades.
    """
    
    def process(self):
        return self.execute()
    
    @abstractmethod
    def execute(self, market_data: dict) -> str:
        """
        Execute the trading strategy based on the generated signal and market data.
        
        Args:
            market_data (dict): Current market data.
        
        Returns:
            str: A trade decision (e.g., "BUY", "SELL", "HOLD").
        """
        pass

class Model(SignalPlugin):
    """
    Base class for models that generate signals based on learned or computed patterns.
    Models can be machine learning-based, statistical, or rule-based.
    """
    @abstractmethod
    def train(self, training_data: list) -> None:
        """
        Train the model using historical or simulated data.
        
        Args:
            training_data (list): Training dataset.
        """
        pass

    @abstractmethod
    def predict(self, input_data: list) -> float:
        """
        Generate a prediction (signal) based on input data.
        
        Args:
            input_data (list): Input features for prediction.
        
        Returns:
            float: The predicted signal value.
        """
        pass
