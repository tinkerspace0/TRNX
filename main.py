

todo = 2

if todo == 1:
    from core.plugin import Plugin
    from trenex import Trenex

    from core.plugin import package_plugin

    package_plugin("plugins/Binance")
    package_plugin("plugins/RSI")
    package_plugin("plugins/Agent")


    trenex = Trenex()
    trenex.start_new_trnx("trnx1")
    trenex.load_plugin("plugins/Binance.zip")
    trenex.load_plugin("plugins/RSI.zip")
    trenex.load_plugin("plugins/Agent.zip")

    trenex.define_plugin_output_to_input("Binance", "ohlcv", "Rsi", "ohlcv")
    trenex.define_plugin_output_to_input("Rsi", "rsi", "Agent", "rsi")

    trenex.build_trnx()
    trenex.get_trnx().run()


elif todo == 2:


    from core.plugin import create_template, get_available_plugin_types
    print(get_available_plugin_types())
    create_template("RSI", "DataPlugin", "temp_templates")


# else:
#     from core.plugin import create_template 

#     create_template("Agent", "dataprocessor", "plugins")

