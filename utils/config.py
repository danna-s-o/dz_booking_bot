from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')