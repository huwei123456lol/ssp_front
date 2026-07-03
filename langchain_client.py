from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8000/chain")
result = remote_chain.invoke({"subject": "拍照的要素是什么"})
print("结果:", result)