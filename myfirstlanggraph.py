from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="./gitignore/myenv.env")

# DEEPSEEK_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# print(os.environ.get("DEEPSEEK_API_KEY"))

model = init_chat_model(
    "qwen3-max-preview", 
    temperature=0, 
    # streaming=True,
    model_provider="deepseek"
    # model_kwargs={
    #     "api_key": DEEPSEEK_API_KEY,
    #     "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    # }
    )
# print(model.__dict__)
# # from langchain_openai import ChatOpenAI

# # model = ChatOpenAI(model="deepseek-v3.1",api_key=DEEPSEEK_API_KEY ,base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# result = model.invoke("你好，请你介绍一下你自己。")
# # print(result.content)
# print(result.additional_kwargs)

from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests
import json
from langchain_tavily import TavilySearch

search_tool = TavilySearch(max_results=5, topic="general")

class WeatherQuery(BaseModel):
    loc: str = Field(description="The location name of the city")

@tool(args_schema= WeatherQuery)
def get_weather(loc):
    """
    查询即时天气函数
    loc: 必要参数，字符串类型，用于表示查询天气的具体城市名称,\
    注意，中国的城市需要用对应城市的英文名称代替，例如如果需要查询北京市天气，则loc参数需要输入'BeiJing'\
    :return: OpenWeather API查询即时天气的结果，具体URL请求地址为：https://api.openweathermap.org/data/2.5/weather\
    返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了全部重要的天气信息
    """

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": loc,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "metric",
        "lang": "zh_cn"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return "Error: Failed to fetch weather data."
    data = response.json()
    result = json.dumps(data)
    # print(result)
    return result

class Write_Query(BaseModel):
    content: str = Field(description="需要写入文档的具体内容")
    filename: str = Field(description="需要写入的文件名")

@tool(args_schema= Write_Query)
def write_file(content: str, filename: str) -> str:
    """
    将指定内容写入本地文件。
    :param content: 必要参数，字符串类型，用于表示需要写入文档的具体内容
    :return: 是否写入成功
    """
    print("写入的内容为：", content)
    # with open(filename, "w", encoding="utf-8") as file:
    #     file.write(content)
    return "写入成功"

tools = [get_weather, write_file, search_tool]

# print(get_weather(loc="BeiJing"))
# print(f"""
#         工具函数get_weather的描述信息如下：{get_weather.description}
#         工具函数get_weather的参数信息如下：{get_weather.args}
#         工具函数get_weather的name：{get_weather.name}
#     """)
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

checkpoint = InMemorySaver()

def log_prompt(state):
    # print("发送给模型的prompt:", state["messages"])
    # for i in state["messages"]:
    #     print("----------------------------------------------------------------------------------------------------------")
    #     print(i.type, ":\t", i.content, ":\n")
    # for i in state.get("messages"):
    #     print("----------------------------------------------------------------------------------------------------------")
    #     print(i.type, ":\t", i.content, ":\n")
    # print("----------------------------------------------------------------------------------------------------------")
    message = state["messages"][-1]
    # print("message是:",message)
    if message.type == "ai":
        print("prompt 信息如下：","\n",message.type ,message.additional_kwargs)
    else:
        print("prompt 信息如下：","\n",message.type, message.content)
    return state

config = {
    "configurable" : {
        "thread_id" : "1"
    }
}
# agent = create_react_agent(model=model, tools=tools, checkpointer=checkpoint, debug=True)
agent = create_react_agent(model=model, tools=tools, checkpointer=checkpoint, pre_model_hook=log_prompt)
# create_tool_cal
# response = agent.invoke({"messages": [{"role": "user", "content": "请帮我查询下杭州现在的天气"}]})
# response = agent.invoke({"messages": [{"role": "user", "content": "请问现在北京和大连哪里更热？并将结果写入文档"}]})
# print(agent.get_prompts())

# response = agent.invoke({"messages": [{"role": "user", "content": "帮我搜索下国内外当前最新的大模型有哪些,并且用表格形式归纳总结下他们的特点以及支持的特性，并写入llms.txt文件中，然后再以Excel表格的形式写入到llms.xlsx文件中。"}]})
# response = agent.invoke({"messages": [{"role": "user", "content": "帮我搜索下国内外当前最新的大模型有哪些"}]})
# response = agent.invoke(
#      {"messages": [{"role": "user", "content": "你好，我叫tom"}]},
#      config=config)
# for i in response.get("messages"):
#     print("----------------------------------------------------------------------------------------------------------")
#     print(i.type, ":\t", i, ":\n")
# response = agent.invoke(
#      {"messages": [{"role": "user", "content": "请问现在北京和大连哪里更热？"}]},
#      config=config)
# response = agent.stream(
#      {"messages": [{"role": "user", "content": "请帮我查询下杭州现在的天气"}]},
#      config=config)
# response = agent.invoke("你是谁？请帮我查询下杭州现在的天气")
# for i,j in response.items():
#     print("----------------------------------------------------------------------------------------------------------")
#     print(i, ":\t", j, ":\n")
# print(response.__dict__)
# # print(response.additional_kwargs)
# print("-----------------------------final answer-----------------------------------------------------------------")
# print("----------------------------------------------------------------------------------------------------------")
# # print(response.get("messages")[-1])
# for i in response:
#     print(i)
# print("agent.get_prompts():",agent.get_prompts())
# for i in response.get("messages"):
#     print("----------------------------------------------------------------------------------------------------------")
#     print(i.type, ":\t", i, ":\n")

response = agent.stream(
     {"messages": [{"role": "user", "content": "请帮我查询下杭州现在的天气"}]},
     config=config,
     stream_mode="updates")
for i in response:
     print(i)

