from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 定义状态
class State(TypedDict):
    input: str
    output: str
    needs_processing: bool

# 定义节点
def check_input(state: State) -> State:
    state["needs_processing"] = len(state["input"]) > 5
    return state

def process_input(state: State) -> State:
    state["output"] = f"处理输入: {state['input']}"
    return state

def skip_processing(state: State) -> State:
    state["output"] = "输入太短，无需处理"
    return state

# 条件函数
def route(state: State) -> str:
    return "process_input" if state["needs_processing"] else "skip_processing"

# 创建图
workflow = StateGraph(State)
workflow.add_node("check_input", check_input)
workflow.add_node("process_input", process_input)
workflow.add_node("skip_processing", skip_processing)
workflow.add_edge(START, "check_input")
workflow.add_conditional_edges("check_input", route, {
    "process_input": "process_input",
    "skip_processing": "skip_processing"
})
workflow.add_edge("process_input", END)
workflow.add_edge("skip_processing", END)

# 编译和运行
graph = workflow.compile()
result = graph.invoke({"input": "Hi", "output": "", "needs_processing": True})
print(result)
