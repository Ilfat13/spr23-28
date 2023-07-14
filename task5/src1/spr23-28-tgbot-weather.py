import os
import json
import requests

FUNC_RESPONSE = {
    'statusCode': 200,
    'body': ''
}
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/2.5/weather"


def send_message(text, message):
    message_id = message['message_id']
    chat_id = message['chat']['id']
    reply_message = {
        'chat_id': chat_id,
        'text': text,
        'reply_to_message_id': message_id
    }

    requests.post(url=f'{TELEGRAM_API_URL}/sendMessage', json=reply_message)


def get_weather(city_name):
    params = {
        'q': city_name,
        'appid': OPENWEATHERMAP_API_KEY,
        'units': 'metric'
    }

    response = requests.get(url=OPENWEATHERMAP_API_URL, params=params)
    data = response.json()

    return data


def process_text_message(message):
    text = message.get('text', '').strip()

    if text == '/start' or text == '/help':
        response_text = """Я сообщу вам о погоде в том месте, которое сообщите мне.
Я могу ответить на:
- Текстовое сообщение с названием населенного пункта.
- Голосовое сообщение с названием населенного пункта.
- Сообщение с точкой на карте."""
        send_message(response_text, message)
    else:
        capitalized_text = text.capitalize()
        weather_data = get_weather(capitalized_text)

        if 'main' in weather_data:
            weather_description = weather_data['weather'][0]['description']
            temperature = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            pressure = weather_data['main']['pressure']
            humidity = weather_data['main']['humidity']
            visibility = weather_data.get('visibility')
            wind_speed = weather_data['wind']['speed']
            wind_direction = weather_data['wind']['deg']
            sunrise = weather_data['sys']['sunrise']
            sunset = weather_data['sys']['sunset']

            wind_direction_str = get_wind_direction(wind_direction)
            sunrise_time = convert_timestamp_to_time(sunrise)
            sunset_time = convert_timestamp_to_time(sunset)

            response_text = f"""{weather_description}.
Температура {temperature} ℃, ощущается как {feels_like} ℃.
Атмосферное давление {pressure} мм рт. ст.
Влажность {humidity} %.
Видимость {visibility} метров.
Ветер {wind_speed} м/с {wind_direction_str}.
Восход солнца {sunrise_time} МСК. Закат {sunset_time} МСК."""

            send_message(response_text, message)
        else:
            response_text = f"Я не нашел населенный пункт \"{text}\"."
            send_message(response_text, message)


def process_voice_message(message):
    voice = message.get('voice')
    if voice:
        response_text = "Распознавание голосовых сообщений пока не поддерживается."
        send_message(response_text, message)


def process_location_message(message):
    location = message.get('location')
    if location:
        response_text = "Распознавание координат сообщений пока не поддерживается."
        send_message(response_text, message)


def process_message(update):
    message = update.get('message')

    if not message:
        return

    if 'text' in message:
        process_text_message(message)
    elif 'voice' in message:
        process_voice_message(message)
    elif 'location' in message:
        process_location_message(message)


def get_wind_direction(degrees):
    directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
    index = round(degrees / 45) % 8
    return directions[index]


def convert_timestamp_to_time(timestamp):
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%H:%M')


def handler(event, context):
    if TELEGRAM_BOT_TOKEN is None or OPENWEATHERMAP_API_KEY is None:
        return FUNC_RESPONSE

    update = json.loads(event['body'])

    if 'message' not in update:
        return FUNC_RESPONSE

    process_message(update)

    return FUNC_RESPONSE
