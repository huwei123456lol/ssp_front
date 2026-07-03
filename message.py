import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1. 加载环境变量
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("错误：未找到 OPENAI_API_KEY。请检查 .env 文件是否在正确位置且格式正确。")
    sys.exit(1)
else:
    # 为了安全，只打印前几位
    print(f"API Key 已加载: {api_key[:10]}...")

# 2. 初始化模型 (Qwen-Turbo)
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model = ChatOpenAI(
    model="qwen-turbo", 
    temperature=0.7, 
    base_url=base_url, 
    api_key=api_key,
    max_tokens=1024,
    stream_options={"include_usage": True}  # 可选：包含使用信息
)

# 3. 定义历史存储
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 4. 定义 Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. Answer all questions to the best of your ability."
    ),
    MessagesPlaceholder(variable_name="messages")
])

# 5. 构建 Chain
chain = prompt | model

# 6. 包装为带历史的 Chain
# 【重要】使用 input_messages_key 指定输入字典中哪个键包含消息列表
with_message_history = RunnableWithMessageHistory(
    chain, 
    get_session_history, 
    input_messages_key="messages"
)

# 7. 配置 Session ID
session_id = "111"
config = {"configurable": {"session_id": session_id}}

def start_chat():
    print("="*50)
    print("欢迎使用 Qwen-Turbo 实时聊天工具")
    print("输入 'quit' 或 'exit' 退出")
    print("="*50)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ")
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            # 实时流式输出
            print("🤖 AI: ", end="", flush=True)
            
            # 调用 stream，每次只传入当前这一条用户消息
            # RunnableWithMessageHistory 会自动拼接历史消息
            for chunk in with_message_history.stream(
                {"messages": [HumanMessage(content=user_input)]}, 
                config=config
            ):
                # chunk.content 包含生成的文本片段
                if chunk.content:
                    print(chunk.content, end="", flush=True)
            
            print() # 每轮对话结束后换行
            
        except KeyboardInterrupt:
            print("\n👋 检测到中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    start_chat()