from core.node.manager import NodeManager

# result = NodeManager.available_nodes()
# print("Available Nodes: ", result)

ex_inst = NodeManager.create_node_instance('exchange', 'KuCoin')
# ex_inst = NodeManager.create_node_instance('exchange', 'KuCoin')

# print(ex_inst)
# print(type(ex_inst))
# print(ex_inst.name)

# from core.session import SessionManager


# ssm = SessionManager()

# ssm.start_new_project("SandBox Project")

# project = ssm.project

# # print(project)

# editor = project._exec

# # print(editor)

# editor.attach_node(ex_inst)


# input, output = ex_inst.get_io()
# print(output.all)

dp = ex_inst.get_dynamic_params()
sp = ex_inst.get_static_params()
print("Static Params: ", sp.limit.value)

print("TImeframe value: ", dp.timeframe.value)

dp.timeframe.value = "1h"

# print("Timeframe value after mod: ", dp.timeframe.value)
