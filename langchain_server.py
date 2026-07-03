# from typing import Optional

# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_community.chat_models.tongyi import ChatTongyi
import os
from dotenv import load_dotenv
# from fastapi import FastAPI
# from langchain_protocol import Annotated, TypedDict
# from langserve import add_routes
# from langsmith import Client
# from langchain.evaluation import load_evaluator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


# 加载 .env 文件中的环境变量
load_dotenv()

# class Joke(TypedDict):
#     think: Annotated[str, ..., "思考过程"]
#     method: Annotated[str, ..., "调用的工具或方法"]
#     obersive: Annotated[str, ..., "工具或方法的观察结果"]

# class Joke(TypedDict):
#     setup: Annotated[str, ..., "The setup of the joke"]
#     punchline: Annotated[str, ..., "The punchline of the joke"]
#     rating: Annotated[Optional[int], None, "How funny the joke is, from 1 to 10"]

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("错误：未找到 OPENAI_API_KEY。请检查 .env 文件是否在正确位置且格式正确。")
    print(f"当前工作目录: {os.getcwd()}")
else:
    # 为了安全，只打印前几位
    print(f"API Key 已加载: {api_key[:10]}...")

base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# model = ChatOpenAI(model_name="qwen-turbo", temperature=0, base_url=base_url, api_key=api_key)

documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Goldfish are popular pets for beginners, requiring relatively simple care.",
        metadata={"source": "fish-pets-doc"},
    ),
    Document(
        page_content="Parrots are intelligent birds capable of mimicking human speech.",
        metadata={"source": "bird-pets-doc"},
    ),
    Document(
        page_content="Rabbits are social animals that need plenty of space to hop around.",
        metadata={"source": "mammal-pets-doc"},
    ),
]

# 向量存储
vectorstore = Chroma.from_documents(documents=documents, embedding=OpenAIEmbeddings(base_url=base_url, api_key=api_key, model="text-embedding-v3"));

cats = vectorstore.similarity_search("cat");
print(f"相似的文档：{cats}")
# cats = await vectorstore.asimilarity_search("cat");

# message = model.invoke([HumanMessage(content="我是hw")])
# print(f'回答：{message.content}')
# model.invoke([HumanMessage(content="我是谁？")])
# print(f'回答：{message.content}')
# value = model.invoke([HumanMessage(content="我是胡伟"), AIMessage(content="你好，胡伟！我有什么可以帮助你的吗？"), HumanMessage(content="我是谁？")])
# print(f'回答：{value.content}')
# store = {};
# def getSessionHistory(sessionId: str) -> BaseChatMessageHistory:
#     if sessionId not in store:
#         store[sessionId] = InMemoryChatMessageHistory()
#     return store[sessionId]
# model = RunnableWithMessageHistory(model, getSessionHistory);
# session_id = "111"
# config = {"configurable": {"session_id": session_id}}
# response = model.invoke([HumanMessage(content="我是胡伟")], config=config)
# print(f'回答：{response.content}')
# # response = model.invoke([HumanMessage(content="我是谁？")], config={"configurable": {"session_id": "111"}})
# response = model.invoke([HumanMessage(content="我是谁？")], config=config)
# print(f'回答：{response.content}')
# prompt = ChatPromptTemplate.from_messages([
#     (
#         "system",
#         "You are a helpful assistant. Answer all questions to the best of your ability."
#     ),
#     MessagesPlaceholder(variable_name="messages")
# ])
# chain = prompt | model
# withMessageHistory = RunnableWithMessageHistory(chain, getSessionHistory, input_key="messages", output_key="output");
# response =withMessageHistory.invoke({"messages": [HumanMessage(content="我是胡伟")]}, config=config)
# print(f'回答：{response.content}')
# response = withMessageHistory.invoke({"messages": [HumanMessage(content="我是谁？")]}, config=config);
# print(f'回答：{response.content}')

# response = chain.invoke({"messages": [HumanMessage(content="我是胡伟")]})
# print(f'回答：{response.content}')
# prompt = PromptTemplate.from_template("请你扮演一个幽默的笑话生成器，生成一个关于{subject}的笑话，并且详细描述你的思考过程、使用的方法和观察到的结果。")
# llm = ChatTongyi(model_name="qwen-turbo", temperature=0)
# output_parser = StrOutputParser()
# llm_structe = llm.with_structured_output(Joke);

# for chunk in llm_structe.stream("讲个笑话"):
#     print(chunk)
# llm_chain = prompt | llm_structe

# for chunk in llm_structe.stream("请你扮演一个幽默的笑话生成器，生成一个关于可笑的女人的笑话，并且详细描述你的思考过程、使用的方法和观察到的结果。"):
#     print(chunk)

# value = prompt.invoke({"subject": "苦逼的码农"});

# print(f"输入：{value}");

# chain = prompt | llm | output_parser
# result = chain.invoke({"subject": "苦逼的码农"})
# print(result)

# client = Client();
# evaluator = load_evaluator("criteria", client=client, criteria=["factuality", "fluency", "correctness"])

# for chunk in chain.stream({"subject": "苦逼的码农"}):
#     print(chunk, end="|", flush=True)



# app = FastAPI(title="LangChain Demo", version="0.1.0", description="A demo of LangChain using DashScope's Qwen model")

# add_routes(app, chain, path="/chain")

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="localhost", port=8000)

# ai agent的逻辑  thought -> action -> observation -> thought -> action -> observation -> ... -> final answer
# 或者  列出执行计划 -> 执行计划 -> 观察 -> 执行计划 -> 观察 -> ... -> 最终答案
