# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)
from geopy.geocoders import Nominatim
import requests
import time
import json
logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        res['response']['text'] = 'Привет! В каком населённом пункте ты находишься?'
        return

    # Обрабатываем ответ пользователя.
    # Вводим название населённого пункта
    city = req["request"]["original_utterance"].lower()
    getLoc = loc.geocode(city)

    # Получаем координаты населённого пункта
    lat = getLoc.latitude
    lon = getLoc.longitude
    # "Флаг для выбора старого или нового файла"
    null = 0
    # Задаём параметры запроса
    params = {
        'lat': lat,
        'lon': lon,
        'lang': 'ru_RU'# язык ответа
    }
    # задаём значение ключа API
    api_key = '96bb9ee0-d4fc-482b-9ba7-f4f7dbb0993d'
    #задаём url API
    url = 'https://api.weather.yandex.ru/v2/forecast'

    # проверка существования файла Weather.json
    try:
        # если файл Weather_'название города'.json существует, сравниваем время в файле с временем в моменте
        with open("Weather_" + city + ".json", "r") as q:
            time = int(time.time()) # время в моменте
            filedata = json.load(q)
            filetime = filedata ['now'] # время в файле

            if time-filetime<360000:# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Вернуть значение 3600 после тестов!!!!!!!!!!!!!!!!!!!!!!
                res["response"]["text"] = "Старый файл" # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!убрать после тестов!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                conclusion(filedata)
            else:
                null = 1
    except:
        null = 1
    if null == 1:
        # делаем запрос API
        r = requests.get(url, params=params, headers={'X-Yandex-API-Key': api_key})

        # проверяем статус ответа
        if(r.status_code==200):
            # преобразуем ответ в JSON формат
            data = r.json()

            # файл с инфой о погоде
            with open("Weather_" + city + ".json", "w+") as f:
                json.dump(data, f)

                # выводим данные о текущей погоде
                #res["response"]["text"] = "Новый файл" # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!убрать после тестов!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                res["response"]["text"] = conclusion(data)
        else:
            res["response"]["text"] = "АЛАРМ!!! КАКАЯ-ТО ПРОБЛЕМА! " + r.status_code

def conclusion(filedata):
    prognoz = "Температура воздуха: " + filedata["fact"]["temp"] + "°C\n"
    prognoz += "Ощущается как: " + filedata["fact"]["feels_like"] + "°C\n"
    if (filedata["fact"]["condition"]=="clear"):
        prognoz += "Ясно"
    elif (filedata["fact"]["condition"]=="partly-cloudy"):
        prognoz += "Малооблачно"
    elif (filedata["fact"]["condition"]=="cloudy"):
        prognoz += "Облачно с прояснениями"
    elif (filedata["fact"]["condition"]=="overcast"):
        prognoz += "Пасмурно"
    elif (filedata["fact"]["condition"]=="light-rain"):
        prognoz += "Небольшой дождь"
    elif (filedata["fact"]["condition"]=="rain"):
        prognoz += "Дождь"
    elif (filedata["fact"]["condition"]=="heavy-rain"):
        prognoz += "Сильный дождь"
    elif (filedata["fact"]["condition"]=="showers"):
        prognoz += "Ливень"
    elif (filedata["fact"]["condition"]=="wet-snow"):
        prognoz += "Дождь со снегом"
    elif (filedata["fact"]["condition"]=="light-snow"):
        prognoz += "Небольшой снег"
    elif (filedata["fact"]["condition"]=="snow"):
        prognoz += "Снег"
    elif (filedata["fact"]["condition"]=="snow-showers"):
        prognoz += "Снегопад"
    elif (filedata["fact"]["condition"]=="hail"):
        prognoz += "Град"
    elif (filedata["fact"]["condition"]=="thunderstorm"):
        prognoz += "Гроза"
    elif (filedata["fact"]["condition"]=="thunderstorm-with-rain"):
        prognoz += "Дождь с грозой"
    elif (filedata["fact"]["condition"]=="thunderstorm-with-hail"):
        prognoz += "Гроза с градом"
    else:
        prognoz += "Не удалось получить значение погодных условий"
    
    '''match filedata["fact"]["condition"]:
        case "clear":
            prognoz += "Ясно"
        case 'partly-cloudy':
            prognoz += "Малооблачно"
        case 'cloudy':
            prognoz += "Облачно с прояснениями"
        case 'overcast':
            prognoz += "Пасмурно"
        case 'light-rain':
            prognoz += "Небольшой дождь"
        case 'rain':
            prognoz += "Дождь"
        case 'heavy-rain':
            prognoz += "Сильный дождь"
        case 'showers':
            prognoz += "Ливень"
        case 'wet-snow':
            prognoz += "Дождь со снегом"
        case 'light-snow':
            prognoz += "Небольшой снег"
        case 'snow':
            prognoz += "Снег"
        case 'snow-showers':
            prognoz += "Снегопад"
        case 'hail':
            prognoz += "Град"
        case 'thunderstorm':
            prognoz += "Гроза"
        case 'thunderstorm-with-rain':
            prognoz += "Дождь с грозой"
        case 'thunderstorm-with-hail':
            prognoz += "Гроза с градом"
        case _:
            prognoz += "Не удалось получить значение погодных условий"
        '''
    return prognoz
