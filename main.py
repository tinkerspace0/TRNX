from core.plugin import Plugin
from trenex import trenex

# trenex.start_new_trnx("trnx1")
# trenex.load_plugin("plugins/Binance")

# trenex.connect_plugin_output_to_input("Binance", "OHLCV", "RSI", "ohlcv")

# trenex.build_trnx()
# trenex.get_trnx("trnx1").run()



from core.plugin import create_template 

create_template("Binance", "exchangeinterface", "plugins")