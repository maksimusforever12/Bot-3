import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp

# Инициализация бота с токеном из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Папка для сохранения файлов (должна быть доступна на сервере)
DOWNLOAD_DIR = "/tmp/downloads"

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Пожалуйста, отправь мне ссылку на YouTube-видео.")

# Обработчик текстовых сообщений (скачивание видео)
@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    video_url = message.text
    if not video_url.startswith("https://www.youtube.com/"):
        await message.reply("Пожалуйста, отправьте корректную ссылку на YouTube.")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ydl_opts = {
        'format': 'bestvideo[height>=1080]+bestaudio/best[height>=1080]/bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'retries': 3,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video_file:
                await message.reply_document(video_file)
            os.remove(file_path)  # Удаление файла после отправки
    except Exception as e:
        await message.reply(f"Ошибка при скачивании: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
