import os
import speech_recognition as sr
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from telegram import InputFile
from bot import bot  # твоя логика из bot.py

TOKEN = '7506152312:AAGAtYRt9pvzPXIhs_GZXJ1PYB9M3mNJUOE'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот по ремонту авто. Напиши или отправь голосовое сообщение.")


# Обработка голосовых сообщений
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем файл с голосовым сообщением
    voice_file = await update.message.voice.get_file()

    # Скачиваем файл как bytearray (предпочтительный метод для новой версии библиотеки)
    file_data = await voice_file.download_as_bytearray()

    # Сохраняем файл как .ogg
    with open('user_voice.ogg', 'wb') as f:
        f.write(file_data)

    # Преобразуем .ogg в .wav (если нужно)
    conversion_command = 'ffmpeg -i user_voice.ogg user_voice.wav'

    # Печатаем команду для отладки
    print(f"Executing command: {conversion_command}")

    # Выполнение команды конвертации
    conversion_result = os.system(conversion_command)

    # Проверяем, успешно ли выполнена команда
    if conversion_result != 0:
        print("Error in FFmpeg conversion!")
        await update.message.reply_text("Произошла ошибка при конвертации файла. Попробуй снова.")
        return

    # Проверяем, создался ли файл user_voice.wav
    if not os.path.exists('user_voice.wav'):
        await update.message.reply_text("Не удалось создать файл .wav. Попробуй снова.")
        return

    # Распознаем голосовое сообщение
    recognizer = sr.Recognizer()
    with sr.AudioFile('user_voice.wav') as source:
        audio = recognizer.record(source)

    try:
        # Используем Google Web Speech API для распознавания текста
        user_message = recognizer.recognize_google(audio, language="ru-RU")
        await update.message.reply_text(f"Вы сказали: {user_message}")

        # Получаем ответ от бота
        response, audio_file = bot(user_message)

        # Отправляем текстовый ответ
        await update.message.reply_text(response)

        # Отправляем голосовой ответ
        with open(audio_file, 'rb') as voice:
            await update.message.reply_voice(voice)

        # Удаляем временные файлы
        os.remove(audio_file)
        os.remove("user_voice.wav")
        os.remove("user_voice.ogg")

    except sr.UnknownValueError:
        await update.message.reply_text("Не понял, что ты сказал. Попробуй снова.")
    except sr.RequestError:
        await update.message.reply_text("Ошибка распознавания. Попробуй позже.")# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response, audio_file = bot(user_message)

    # Отправка текстового ответа
    await update.message.reply_text(response)

    # Отправка голосового ответа
    with open(audio_file, 'rb') as voice:
        await update.message.reply_voice(voice)

    # Удаляем временный аудиофайл
    os.remove(audio_file)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))  # Обработка голосовых сообщений

    print("✅ Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()
