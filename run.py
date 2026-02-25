from config import CONFIG
from main import start_bot

if __name__ == '__main__':
    try:
        start_bot(CONFIG)
    except Exception as e:
        print(f'An error occurred: {e}')