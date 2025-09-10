from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 定义状态
class State(TypedDict):
    input: str
    output: str

# 定义节点
def process_input(state: State) -> State:
    state["output"] = f"处理输入: {state['input']}"
    return state

def finalize_output(state: State) -> State:
    state["output"] += " -> 已完成"
    return state

# 创建图
workflow = StateGraph(State)
workflow.add_node("process_input", process_input)
workflow.add_node("finalize_output", finalize_output)
workflow.add_edge(START, "process_input")
workflow.add_edge("process_input", "finalize_output")
workflow.add_edge("finalize_output", END)

# 编译和运行
graph = workflow.compile()
result = graph.invoke({"input": "Hello, LangGraph!", "output": ""})
print(result)
