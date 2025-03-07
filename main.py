from core.plugin import Plugin
from trenex import trenex


todo = 1

if todo == 1:
    trenex.start_new_trnx("trnx1")
    trenex.load_plugin("plugins/Binance.zip")
    trenex.load_plugin("plugins/RSI.zip")

    trenex.connect_plugin_output_to_input("Binance", "OHLCV", "Rsi", "ohlcv")

    trenex.build_trnx()
    trenex.get_trnx().run()


else:
# from core.plugin import create_template 

# create_template("RSI", "dataprocessor", "plugins")



    from core.plugin import package_plugin

    package_plugin("plugins/Binance")
    package_plugin("plugins/RSI")