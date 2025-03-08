# from dotenv import load_dotenv
import os
#
# load_dotenv()

TOKEN = os.getenv('TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')

if not TOKEN or not PAYMENT_TOKEN:
    raise ValueError("Переменные окружения TOKEN и PAYMENT_TOKEN не установлены!")