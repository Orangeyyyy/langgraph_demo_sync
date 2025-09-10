from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="myenv.env")

# 定义工具
@tool
def search(query: str, config: RunnableConfig) -> str:
    """模拟从网络上搜获相关的数据进行汇总"""
    return f"搜索结果: {query} 的信息"

# 定义状态
class State(TypedDict):
    input: str
    output: str
    needs_search: bool
    search_count: int

# 定义节点
def decide_action(state: State, config: RunnableConfig) -> State:
    # model = ChatOpenAI(
    # model_name="qwen3-max-preview", 
    # temperature=0, 
    # api_key=os.getenv("DASHSCOPE_API_KEY"),
    # base_url=os.getenv("DEEPSEEK_API_BASE")
    # ).bind_tools(tools)
    llm = ChatOpenAI(
        model_name="qwen3-max-preview", 
        temperature=0, 
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE")
        )
    prompt = f"用户问题: {state['input']}\n回答 'yes' 如果需要搜索，'no' 如果可以直接回答。"
    response = llm.invoke(prompt, config=config).content
    state["needs_search"] = response.lower() == "yes"
    return state

def search_node(state: State, config: RunnableConfig) -> State:
    state["search_count"] += 1
    result = search.invoke({"query": state["input"]}, config=config)
    state["output"] = result
    return state

def answer_node(state: State, config: RunnableConfig) -> State:
    llm = ChatOpenAI(
        model_name="qwen3-max-preview", 
        temperature=0, 
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE")
        )
    prompt = f"直接回答用户问题: {state['input']}"
    response = llm.invoke(prompt, config=config).content
    state["output"] = response
    return state

# 条件函数
def route(state: State) -> str:
    if state["needs_search"] and state["search_count"] < 2:
        return "search_node"
    return "answer_node"

# 创建图
workflow = StateGraph(State)
workflow.add_node("decide_action", decide_action)
workflow.add_node("search_node", search_node)
workflow.add_node("answer_node", answer_node)
workflow.add_edge(START, "decide_action")
workflow.add_conditional_edges("decide_action", route, {
    "search_node": "search_node",
    "answer_node": "answer_node"
})
workflow.add_conditional_edges("search_node", route, {
    "search_node": "search_node",
    "answer_node": "answer_node"
})
workflow.add_edge("answer_node", END)

# 编译和运行
graph = workflow.compile()
result = graph.invoke(
    {"input": "什么是 LangGraph?", "output": "", "needs_search": False, "search_count": 0},
    config={"configurable": {"user_id": "user123"}}
)
print(result)
