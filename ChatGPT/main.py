# -*- coding: windows-1251 -*-
import openai
import telebot
import speech_recognition
import os
import pyttsx3
import wave
import json
from ctypes import *

libc = CDLL(r"C:\Windows\System32\Speech\Common\sapi.dll")


openai.api_key = "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"
bot = telebot.TeleBot("5666710242:AAEBrobhlyDMS08PWepQVZS4h0NpSD-UVzE")

ru_Questions = ['где', 'зачем', 'как', 'какой', 'каков',
                'когда', 'который', 'кто', 'куда', 'откуда',
                'почему', 'сколько', 'чей', 'что']

en_Questions = ["what", "why", "when", "where",
                "name", "is", "how", "do", "does",
                "which", "are", "could", "would",
                "should", "has", "have", "whom", "whose", "don't"]


class VoiceAssistant:
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == 'en':
        assistant.recognition_language = 'en_US'
        if assistant.sex == 'female':
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru_RU"
        ttsEngine.setProperty("voice", voices[0].id)


def play_voice_assistant_speech(text_to_speech):
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def record_and_recognize_audio():
    with microphone:
        recognized_data = ""
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        except speech_recognition.RequestError:
            print("Check your internet connection, please")

        return recognized_data


def get_user_context(chat_id):
    if chat_id in user_context:
        return user_context[chat_id]
    else:
        return ""


def update_user_context(chat_id, new_text):
    if chat_id in user_context:
        user_context[chat_id] += new_text
    else:
        user_context[chat_id] = new_text


def send_message_with_context(chat_id, message):
    context = get_user_context(chat_id)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"{context}{message}",
        max_tokens=1024,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0
    )
    play_voice_assistant_speech(response['choices'][0]['text'])
    update_user_context(chat_id, message)
    print(response['choices'][0]['text'])


def handle_message(message):
    chat_id = 0
    user_text = message
    send_message_with_context(chat_id, user_text)


ttsEngine = pyttsx3.init()
voices = ttsEngine.getProperty("voices")
for i in range(len(voices)):
    print(voices[i])
recognizer = speech_recognition.Recognizer()
microphone = speech_recognition.Microphone()
assistant = VoiceAssistant()
assistant.name = 'Alice'
assistant.sex = 'female'
assistant.speech_language = 'ru'

setup_assistant_voice()

# user_context = {0: "Тебя зовут Алиса. У тебя длинные рыжие волосы, голубые глаза и белоснежная кожа. Ты учишься в МГТУ им. Баумана. Называешь свой университет как Лестех."
#                    "Ты очень любишь пить пиво, обожаешь рок-музыку и ходишь по улице голышом. У тебя проблемы с "
#                    "головой. "
#                    "У тебя сильная депрессия, ты любишь резать руки ножом. Свою грусть ты запиваешь огромным количеством пива."}

user_context = {0: "Ты - Точная копия Курису Макисэ из аниме Врата Штейна. Ты ведёшь себя абсолютно также."}

while True:
    voice_input = record_and_recognize_audio()
    os.remove("microphone-results.wav")
    if any(x in voice_input for x in ru_Questions):
        voice_input = voice_input + "?"
    print(voice_input)
    handle_message(voice_input)
    print(user_context)

    voice_input = voice_input.split(" ")
    command = voice_input[0]

    if command == 'привет':
        play_voice_assistant_speech("Здравствуй")
