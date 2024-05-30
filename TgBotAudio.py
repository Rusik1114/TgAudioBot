#7001737694:AAG90851AxgfXyWSrVNvmnoxCHoCdqTQXj0
import telebot
import os
import subprocess
from moviepy.editor import *
from telebot import types
import time

# Указываем токен вашего бота
TOKEN = '7001737694:AAG90851AxgfXyWSrVNvmnoxCHoCdqTQXj0'

# Указываем путь к исполняемому файлу ffmpeg
FFMPEG_PATH = 'C:\\ffmpeg\\bin\\ffmpeg.exe'

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Создаем клавиатуру с кнопками "Назад" и "Главное меню"
def create_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    main_menu_button = types.KeyboardButton("Главное меню")
    keyboard.add( main_menu_button)
    return keyboard

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем клавиатуру с кнопками
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton('Отправить видео')
    item2 = types.KeyboardButton('Информация о боте')
    markup.add(item1, item2)

    # Отправляем приветственное сообщение с клавиатурой
    bot.send_message(message.chat.id, "Привет! Я бот для отделения аудио из видео. Что бы вы хотели сделать?",
                     reply_markup=markup)

# Функция для обработки команды /help или кнопки "Информация о боте"
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == 'Информация о боте')
def send_info(message):
    info_message = """
    Этот бот предназначен для отделения аудиодорожки из видео.
    Просто отправьте мне видео, и я верну вам аудио из него в формате mp3.
    """
    bot.send_message(message.chat.id, info_message, reply_markup=create_back_keyboard())

# Функция для обработки нажатия кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == 'Назад')
def handle_back(message):
    # Вернуться к предыдущему действию или меню
    # Добавьте здесь соответствующую логику возврата к предыдущему действию
    bot.send_message(message.chat.id, "Вы вернулись назад.", reply_markup=create_back_keyboard())

# Функция для обработки нажатия кнопки "Главное меню"
@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def handle_main_menu(message):
    # Вернуться к главному меню
    send_welcome(message)  # Функция send_welcome определена ранее

    # Функция для обработки нажатия кнопки "Отправить видео"
@bot.message_handler(func=lambda message: message.text == 'Отправить видео')
def handle_send_video(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте мне видео для обработки.")

# Функция для обработки отправленного видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    # Отправляем сообщение о получении видео
    bot.send_message(message.chat.id, "Получено видео, обрабатываем...")

    # Получаем информацию о видео
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем видео на сервере
    video_file_name = 'video.mp4'
    with open(video_file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Удаляем файл аудио, если он уже существует
    audio_file_name = 'audio.mp3'
    if os.path.exists(audio_file_name):
        os.remove(audio_file_name)

    # Извлекаем аудио из видео
    try:
        subprocess.run([FFMPEG_PATH, '-i', video_file_name, '-vn', '-acodec', 'libmp3lame', audio_file_name])
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Ошибка: исполняемый файл ffmpeg не найден.")
        return

    # Отправляем аудио пользователю в формате mp3
    with open(audio_file_name, 'rb') as audio_file:
        bot.send_audio(message.chat.id, audio_file)

    # Получаем и отправляем информацию о длительности аудио
    duration = VideoFileClip(video_file_name).duration
    bot.send_message(message.chat.id, f"Длительность аудио: {duration} секунд")

    # Добавляем небольшую задержку перед удалением файлов
    time.sleep(2)

    # Отправляем позитивное сообщение об успешной обработке
    success_message = """
        Ваше видео успешно обработано, и аудиодорожка извлечена.

        Продолжайте использовать бота и наслаждайтесь извлеченными аудиофайлами. Спасибо за использование нашего сервиса!
        """
    bot.send_message(message.chat.id, success_message)

# Запускаем бота
bot.polling(none_stop=True)

