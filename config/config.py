from environs import Env
import os

_path = os.path.abspath(os.curdir)
env = Env()
env.read_env()

DATABASE_URI = env.str('DATABASE_URI')
TON_URL = env.str("TON_URL")
API_TON_KEY = env.str("API_TON_KEY")
