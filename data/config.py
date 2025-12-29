from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("IP")  # Тоже str, но для айпи адреса хоста
GROUP_ID = env.str("GROUP_ID")
CHANNEL_ID = env.str("CHANNEL_ID")
CHANNEL_URL = env.str("CHANNEL_URL")
CHANNEL_URL2 = env.str("CHANNEL_URL2")
CHANNEL_SUBSCRIBE_ID_1 = env.str("CHANNEL_SUBSCRIBE_ID_1")
CHANNEL_SUBSCRIBE_ID_2 = env.str("CHANNEL_SUBSCRIBE_ID_2")
BOT_USERNAME = env.str("BOT_USERNAME")

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")
