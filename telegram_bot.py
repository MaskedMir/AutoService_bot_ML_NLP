import os
import speech_recognition as sr
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from bot import bot
import db

TOKEN = '7742460259:AAEeRistZpZmup5HiElr6gQZhhcN39zmGe0'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот по ремонту авто. Напиши или отправь голосовое сообщение.")


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_db_id = db.save_user(user)  # Сохраняем пользователя

    voice_file = await update.message.voice.get_file()
    file_data = await voice_file.download_as_bytearray()

    with open('user_voice.ogg', 'wb') as f:
        f.write(file_data)

    conversion_command = 'ffmpeg -i user_voice.ogg user_voice.wav'
    print(f"Executing command: {conversion_command}")

    try:
        conversion_result = os.system(conversion_command)
        if conversion_result != 0:
            print("Error in FFmpeg conversion!")
            await update.message.reply_text("Произошла ошибка при конвертации файла. Попробуй снова.")
            return

        if not os.path.exists('user_voice.wav'):
            await update.message.reply_text("Не удалось создать файл .wav. Попробуй снова.")
            return

        recognizer = sr.Recognizer()
        with sr.AudioFile('user_voice.wav') as source:
            audio = recognizer.record(source)

        try:
            user_message = recognizer.recognize_google(audio, language="ru-RU")
            await update.message.reply_text(f"Вы сказали: {user_message}")

            response, audio_file = bot(user_message)
            db.log_interaction(user_db_id, user_message, response)  # Логируем взаимодействие

            await update.message.reply_text(response)
            with open(audio_file, 'rb') as voice:
                await update.message.reply_voice(voice)

        except sr.UnknownValueError:
            await update.message.reply_text("Не понял, что ты сказал. Попробуй снова.")
        except sr.RequestError:
            await update.message.reply_text("Ошибка распознавания. Попробуй позже.")

    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        if os.path.exists("user_voice.wav"):
            os.remove("user_voice.wav")
        if os.path.exists("user_voice.ogg"):
            os.remove("user_voice.ogg")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_db_id = db.save_user(user)  # Сохраняем пользователя
    user_message = update.message.text
    response, audio_file = bot(user_message)

    db.log_interaction(user_db_id, user_message, response)  # Логируем взаимодействие

    await update.message.reply_text(response)
    with open(audio_file, 'rb') as voice:
        await update.message.reply_voice(voice)

    os.remove(audio_file)


def main():
    db.init_db()  # Инициализация БД
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    print("✅ Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()