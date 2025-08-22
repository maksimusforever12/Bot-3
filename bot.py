import os
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, F
from aiogram.types import Update
import yt_dlp
from aiogram import html

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не установлена")

RENDER_SERVICE_NAME = os.environ.get('RENDER_SERVICE_NAME')
if not RENDER_SERVICE_NAME:
    raise ValueError("Переменная окружения RENDER_SERVICE_NAME не установлена")

app = FastAPI()
bot = Bot(TOKEN)
dp = Dispatcher()

def get_direct_link(video_url):
    ydl_opts = {
        'format': 'bestvideo[height>=1080]+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '%(id)s.%(ext)s',
        'merge_output_format': 'mp4'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            # Фильтруем форматы с height >= 1080 и сортируем по height descending
            high_quality_formats = [f for f in formats if f.get('height', 0) >= 1080]
            if not high_quality_formats:
                return "Видео не доступно в разрешении 1080p или выше."
            # Выбираем лучший (с наибольшей height)
            best_format = max(high_quality_formats, key=lambda f: f.get('height', 0))
            return best_format['url']
    except Exception as e:
        return f"Ошибка при обработке видео: {str(e)}"

@dp.message(F.text == '/start')
async def start_handler(message):
    await message.reply('Просто напиши мне ссылку на видео YouTube, а я скачаю его для тебя)')

@dp.message(F.text.regexp(r'^https:\/\/(www\.youtube\.com\/watch\?v=|youtu\.be\/|www\.youtube\.com\/shorts\/)[^\s]+'))
async def video_handler(message):
    url = message.text
    direct_link = get_direct_link(url)
    if isinstance(direct_link, str) and direct_link.startswith('http'):
        text = html.link('Вот, лови', html.quote(direct_link))
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(direct_link if isinstance(direct_link, str) else "Не удалось получить ссылку на видео. Проверьте URL или попробуйте позже.")

@app.post("/webhook/{token}")
async def webhook_handler(request: Request, token: str):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    update_data = await request.json()
    telegram_update = Update(**update_data)
    await dp.process_update(telegram_update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://{RENDER_SERVICE_NAME}.onrender.com/webhook/{TOKEN}"
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(webhook_url)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

if __name__ == '__main__':
    # Для локального тестирования (не используется на Render)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
