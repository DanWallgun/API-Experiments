import datetime
import time
import random
import logging
import requests

import numpy as np
import cv2
import telebot

TOKEN = "123:abc"
started = 0
start_messages = [
    "Howdy!",
    "Достаю фильтры. Давай же начнем!",
    "Уже начали же, не? :)",
    "Теперь точно начали!",
    "Понятно, ты Internet Explorer. Тогда я просто подожду, пока до тебя дойдет, что мы начали",
    "Я фильтрую изображения, а тебе неплохо было бы фильтровать базар.",
    "Ладно, я притворюсь, что ничего не видел."
]

random.seed(datetime.datetime.now())
bot = telebot.TeleBot(TOKEN, threaded=False)

buffer_image = cv2.imread("base_image.jpg")
edge_detection_selector = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
edge_detection_selector.add('Blurred image', 'Sharp image')
hide_board = telebot.types.ReplyKeyboardRemove()
edge_detection_selected_flag = {}


def get_ed_sel_flag(id):
    if id not in edge_detection_selected_flag:
        edge_detection_selected_flag[id] = 0
    return edge_detection_selected_flag[id]


def edge_detection_blurred(image):
    sharpen_kernel = np.array((
        [-1, -1, -1],
        [-1, 9, -1],
        [-1, -1, -1]
    ), dtype="int")
    b, g, r = cv2.split(image)
    b = cv2.equalizeHist(b)
    g = cv2.equalizeHist(g)
    r = cv2.equalizeHist(r)
    image = cv2.merge((b, g, r))
    image = cv2.filter2D(image, -1, sharpen_kernel)
    image = cv2.GaussianBlur(image, (5, 5), 5)
    image = cv2.Canny(image, 100, 200)
    return image


def edge_detection_sharp(image):
    image = cv2.Canny(image, 75, 215)
    return image


@bot.message_handler(commands=["start"])
def start_message(message):
    global started
    bot.send_message(message.chat.id, start_messages[started])
    started = (started + 1) % len(start_messages)


@bot.message_handler(func=lambda message: get_ed_sel_flag(message.chat.id) == 1)
def return_edge_detection(message):
    bot.send_chat_action(message.chat.id, "typing")

    if message.text == "Sharp image":
        img_str = cv2.imencode('.jpg', edge_detection_sharp(buffer_image))[1].tostring()
        bot.send_photo(message.chat.id, img_str, reply_markup=hide_board)
        edge_detection_selected_flag[message.chat.id] = 0
    elif message.text == "Blurred image":
        img_str = cv2.imencode('.jpg', edge_detection_blurred(buffer_image))[1].tostring()
        bot.send_photo(message.chat.id, img_str, reply_markup=hide_board)
        edge_detection_selected_flag[message.chat.id] = 0
    else:
        pass


@bot.message_handler(content_types=["photo"])
def update_buffer(message):
    global buffer_image

    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format(TOKEN, file_info.file_path))

    np_image = np.frombuffer(file.content, np.uint8)
    buffer_image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    bot.send_message(message.chat.id, "Select the correct image description", reply_markup=edge_detection_selector)
    edge_detection_selected_flag[message.chat.id] = 1

timeout = 130
while True:
    try:
        bot.polling(none_stop=True, timeout=timeout)
    except Exception as exception:
        logging.error(exception)
        time.sleep(15)
        timeout += 10
