import atexit
import os
import pickle

if os.path.exists('data.pkl'):
    with open('data.pkl', 'rb') as file:
        chat_data = pickle.load(file)
else:
    chat_data = {}


def save_data():
    with open('data.pkl', 'wb') as f:
        pickle.dump(chat_data, f)


atexit.register(save_data)
