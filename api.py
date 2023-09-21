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
import psycopg2
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

    try:
        time = int(time.time())
        # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname='verceldb',user='default',password='9RKMIJP8GHSE',host='ep-aged-hall-03402926-pooler.us-east-1.postgres.vercel-storage.com')
        cursor = conn.cursor
        cursor.execute('SELECT CASE WHEN (select Time from scientist where City = %s) is NULL THEN \'NULL\' ELSE (select Time from scientist where City = %s) END', (city, city))
        if(cursor.fetchone()=='NULL'):   # Запись о городе не существует
            # API-запрос
            r = requests.get(url, params=params, headers={'X-Yandex-API-Key': api_key})
            # проверяем статус ответа
            if(r.status_code==200):
                # преобразуем ответ в JSON формат
                data = r.json()
                temp = data["fact"]["temp"]
                feel = data["fact"]["feels_like"]
                cond = data["fact"]["condition"]
                #Добавление записи
                cursor.execute('INSERT INTO whether (City, Time, Temp, Feel, Cond) VALUES(%s, %s, %s, %s, %s)', (city, time, temp, feel, cond))
                conclusion(temp,feel,cond)
            else:
                res["response"]["text"] = "АЛАРМ!!! КАКАЯ-ТО ПРОБЛЕМА! " + r.status_code
        else:   # Запись о городе существует
            if(time-cursor.fetchone()<10900): # Используем данные из базы
                cursor.execute('SELECT Temp, Feel, Cond FROM whether WHERE City = %s', (city))
                #temp, feel, cond = cursor.fetchone()
                conclusion(cursor.fetchone())
            else: # Вносим спаршенные данные в базу
                # API-запрос
                r = requests.get(url, params=params, headers={'X-Yandex-API-Key': api_key})
                # проверяем статус ответа
                if(r.status_code==200):
                    # преобразуем ответ в JSON формат
                    data = r.json()
                    temp = data["fact"]["temp"]
                    feel = data["fact"]["feels_like"]
                    cond = data["fact"]["condition"]
                    #Обновление записи
                    cursor.execute('UPDATE whether SET Time = %s, Temp = %s, Feel = %s, Cond = %s WHERE City = %s', (time, temp, feel, cond, city));
                else:
                    res["response"]["text"] = "АЛАРМ!!! КАКАЯ-ТО ПРОБЛЕМА! " + r.status_code
    except:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def conclusion(Temp, Feel, Cond):
    prognoz = "Температура воздуха: " + Temp + "°C\n"
    prognoz += "Ощущается как: " + Feel + "°C\n"
    if (Cond=="clear"):
        prognoz += "Ясно"
    elif (Cond=="partly-cloudy"):
        prognoz += "Малооблачно"
    elif (Cond=="cloudy"):
        prognoz += "Облачно с прояснениями"
    elif (Cond=="overcast"):
        prognoz += "Пасмурно"
    elif (Cond=="light-rain"):
        prognoz += "Небольшой дождь"
    elif (Cond=="rain"):
        prognoz += "Дождь"
    elif (Cond=="heavy-rain"):
        prognoz += "Сильный дождь"
    elif (Cond=="showers"):
        prognoz += "Ливень"
    elif (Cond=="wet-snow"):
        prognoz += "Дождь со снегом"
    elif (Cond=="light-snow"):
        prognoz += "Небольшой снег"
    elif (Cond=="snow"):
        prognoz += "Снег"
    elif (Cond=="snow-showers"):
        prognoz += "Снегопад"
    elif (Cond=="hail"):
        prognoz += "Град"
    elif (Cond=="thunderstorm"):
        prognoz += "Гроза"
    elif (Cond=="thunderstorm-with-rain"):
        prognoz += "Дождь с грозой"
    elif (Cond=="thunderstorm-with-hail"):
        prognoz += "Гроза с градом"
    else:
        prognoz += "Не удалось получить значение погодных условий"
    return prognoz
'''
try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='verceldb', user='default', password='9RKMIJP8GHSE', 
            host='ep-aged-hall-03402926-pooler.us-east-1.postgres.vercel-storage.com')
    with conn.cursor as curs:
        cursor.execute('SELECT Time, Temp, Feel, Cond FROM whether WHERE City = %s', (City = city))
        TimeBD, TempBD, FeelBD, CondBD = cursor.fetchone()
        if(time-TimeBD<360000)
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')
finally:
    if connection:
        connection.close()

#cursor.execute('сюда вводить SQL запрос')
#cursor.execute('SELECT * FROM whether WHERE name=%s', ('Alfred')) - запрос с параметром
#cursor.fetchone() — вернуть одну строку
#connection.commit() — отправить коммит (после изменений базы)

curs.execute('select CASE WHEN (select Time from scientist where City = %s) is NULL THEN 'NULL'
        ELSE (select Time from whether where City = %s) END', (city, city))
if(cursor.fetchone()=='NULL'):   # Запись о городе не существует
    cursor.execute('INSERT INTO whether (City, Time, Temp, Feel, Cond) VALUES(%s, %s, %s, %s, %s)', (city, time, temp, feel, cond))  #Добавление записи
else:   # Запись о городе существует
    if(time-cursor.execute()<7200):



# SQL command not used
SELECT Time FROM whether
WHERE City = %s

INSERT INTO whether (City, Time, Temp, Feel, Cond)
VALUES(%s, %s, %s, %s, %s) 
ON CONFLICT (City) 
DO 
    UPDATE SET 
        Time = EXCLUDED.Time, 
        Temp = EXCLUDED.Temp, 
        Feel = EXCLUDED.Feel, 
        Cond = EXCLUDED.Cond;


'''