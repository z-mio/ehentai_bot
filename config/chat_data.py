import atexit
import os
import pickle

file_path = 'data.pkl'

# 检查文件是否存在并且不为空
if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    try:
        with open(file_path, 'rb') as file:
            chat_data = pickle.load(file)
    except (EOFError, pickle.UnpicklingError):
        # 处理读取错误，初始化为空字典
        chat_data = {}
        print("Failed to load data.pkl, initializing with empty data.")
else:
    chat_data = {}

def save_data():
    with open(file_path, 'wb') as f:
        pickle.dump(chat_data, f)

# 在程序退出时保存数据
atexit.register(save_data)
