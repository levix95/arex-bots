import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
TOKEN = os.getenv('TOKEN', 'YOUR_TOKEN_HERE')
COMMAND_PREFIX = '!'
INTENTS = 'all'

# Settings
MAX_BAN_COUNT = 50000
MAX_CHANNEL_CREATE = 50000
MAX_ROLE_CREATE = 50000

# Colors
COLOR_SUCCESS = 0x00ff00
COLOR_ERROR = 0xff0000
COLOR_INFO = 0x0000ff