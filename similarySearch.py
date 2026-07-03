# from langchain_core.documents import Document
# from langchain_core.runnables import RunnableLambda
# from vectorsave import vectorstore

# retrive = RunnableLambda(vectorstore.similarity_search).bind(k=1);
# result = retrive.batch(["cat", "dog"]);
# print(f"相似度查询结果: {result}")
# result = vectorstore.as_retriever(search_kwargs={"k": 1}, search_type="similarity").batch(["cat", "dog"]);
# print(f"相似度查询结果: {result}")

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = os.getenv("OPENAI_API_KEY")
vectorstore = FAISS.from_texts(["Harrison worked at Google as a software engineer."], embedding=OpenAIEmbeddings(base_url=base_url, api_key=api_key, model="text-embedding-v3"));
retriever = vectorstore.as_retriever(search_kwargs={"k": 1}, search_type="similarity");
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

model = ChatOpenAI(model_name="qwen-turbo", temperature=0, base_url=base_url, api_key=api_key);
retriever_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
result = retriever_chain.invoke("where did harrison work?")
print(f"相似度查询结果: {result}")