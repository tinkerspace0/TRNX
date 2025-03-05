# trenex.py


from trenex.core.components import ExchangeComponent, DataProcessor, Oracle, Agent

class Trenex:
    """
    Main bot class that holds and executes components in a predefined order.
    """
    def __init__(self):
        self.components = {
            "Exchange": ExchangeComponent(),
            "DataProcessor": DataProcessor(),
            "Oracle": Oracle(),
            "Agent": Agent()
        }
        self.execution_order = ["Exchange", "DataProcessor", "Oracle", "Agent"]

    def build(self):
        """
        Build the bot by initializing components and their plugins.
        """
        for comp_name in self.execution_order:
            self.components[comp_name].build()
        print("Trenex build complete.")

    def run(self):
        """
        Run components in the specified execution order.
        """
        for comp_name in self.execution_order:
            self.components[comp_name].execute()
