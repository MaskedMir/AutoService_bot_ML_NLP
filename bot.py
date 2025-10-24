from config import BOT_CONFIG
from ml_model import classify_intent
from utils import clear_phrase
from dialogue_base import generate_answer
import random
import datetime
from gtts import gTTS


def get_answer_by_intent(intent):
    return random.choice(BOT_CONFIG['intents'][intent]['responses'])

def get_failure_phrase():
    return random.choice(BOT_CONFIG['failure_phrases'])

def log_dialog(user_text, bot_response):
    with open("log.txt", "a", encoding="utf-8") as log:
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log.write(f"{timestamp} USER: {user_text}\n")
        log.write(f"{timestamp} BOT : {bot_response}\n\n")


# Функция для логирования диалога
def log_dialog(user_text, bot_response):
    with open("log.txt", "a", encoding="utf-8") as log:
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log.write(f"{timestamp} USER: {user_text}\n")
        log.write(f"{timestamp} BOT : {bot_response}\n\n")


# Функция для озвучивания ответа
def speak(text, lang='ru'):
    tts = gTTS(text=text, lang=lang, slow=False)
    file_name = "response.mp3"
    tts.save(file_name)
    return file_name


# Основная логика бота
def bot(replica):
    cleared = clear_phrase(replica)
    intent = classify_intent(cleared)

    if intent in BOT_CONFIG['intents']:
        answer = get_answer_by_intent(intent)
    else:
        answer = generate_answer(cleared)
        if not answer:
            answer = get_failure_phrase()

    log_dialog(replica, answer)

    # Генерируем голосовое сообщение
    audio_file = speak(answer)

    return answer, audio_file  # Возвращаем ответ и путь к аудиофайлу
