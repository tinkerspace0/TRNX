from core.node.manager import NodeManager

result = NodeManager.available_nodes()
print("Available Nodes: ", result)

ex_inst = NodeManager.create_node_instance('exchange', 'KuCoin')
rsi_inst = NodeManager.create_node_instance('dataprocessor', 'RSI')

# print(ex_inst)
# print(type(ex_inst))
# print(ex_inst.name)

# print(rsi_inst)
# print(type(rsi_inst))
# print(rsi_inst.name)

from core.session import SessionManager


ssm = SessionManager()

ssm.start_new_project("SandBox Project")

project = ssm.project

# print(project)

editor = project._exec

# print(editor)

editor.attach_node(ex_inst)
editor.attach_node(rsi_inst)

# input, output = ex_inst.get_io()
# print(output.all)

dp = ex_inst.get_dynamic_params()
sp = ex_inst.get_static_params()
print("Exchange Limit: ", sp.limit.value)
print("Exchange Timeframe: ", dp.timeframe.value)

dp = rsi_inst.get_dynamic_params()
sp = rsi_inst.get_static_params()
print("RSI Limit: ", sp.limit.value)
print("RSI Period: ", dp.period.value)


editor.connect_node_io(output_node_name=ex_inst.name, output_port="ohlcv", input_node_name=rsi_inst.name, input_port="ohlcv")

editor.build_trnx()

bot = editor.get_trnx()

bot.run()