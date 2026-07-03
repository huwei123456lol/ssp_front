import dashscope
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List
import os
from dotenv import load_dotenv
import asyncio
from langchain_openai import OpenAIEmbeddings

load_dotenv();

class DashScopeEmbeddings:
    def __init__(self, api_key: str, model: str = "text-embedding-v3"):
        self.api_key = api_key
        self.model = model
        dashscope.api_key = api_key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        responses = []
        for text in texts:
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=text
            )
            if response.status_code == 200:
                # 提取嵌入向量
                embedding = response.output['embeddings'][0]['embedding']
                responses.append(embedding)
            else:
                raise Exception(f"DashScope API error: {response.message}")
        return responses

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

# 使用自定义 Embeddings
api_key = os.getenv("DASHSCOPE_API_KEY") # 确保 .env 中是 DASHSCOPE_API_KEY 或 OPENAI_API_KEY 通用
embeddings = DashScopeEmbeddings(api_key=api_key)

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

vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

cats = vectorstore.similarity_search("cat")
print(f"相似的文档：{cats}")
score = vectorstore.similarity_search_with_score("cat")
print(f"相似的文档和分数：{score}")

async def async_get(keyWord: str):
    return await vectorstore.asimilarity_search(keyWord)

cats = asyncio.run(async_get("cat"));
print(f"相似的文档：{cats}")

# embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key, embeddings=embeddings).embed_query("cat")
# cats = vectorstore.similarity_search_by_vector(embeddings);
# print(f"相似的文档：{cats}")