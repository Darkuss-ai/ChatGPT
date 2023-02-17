# -*- coding: windows-1251 -*-
import openai
import speech_recognition
import wave
import json
import os
import torch
import winsound
from googletrans import Translator
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from gpt2_client import GPT2Client

openai.api_key = "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"


class VoiceAssistant:
    name = ""
    speaker = ""
    sex = ""
    speech_language = ""
    recognition_language = ""

    def __init__(self, name, sex, speech_language, recognition_language):
        self.name = name
        self.sex = sex
        self.speech_language = speech_language
        self.recognition_language = recognition_language
        if speech_language == 'ru' and sex == 'female':
            self.speaker = 'baya'
        elif speech_language == 'ru' and sex == 'male':
            self.speaker = 'aidar'
        elif speech_language == 'en' and sex == 'female':
            self.speaker = 'en_0'
        elif speech_language == 'en' and sex == 'male':
            self.speaker = 'en_1'
        else:
            self.speaker = 'random'


def play_voice_assistant_speech(text_to_speech):
    if len(text_to_speech) == 0:
        if assistant.sex == 'female':
            if assistant.speech_language == 'ru':
                text_to_speech = "Извини, я не очень тебя поняла. Можешь повторить?"
            else:
                text_to_speech = "Sorry, i don't understand you. Can you repeat what did you say?"
        else:
            if assistant.speech_language == 'ru':
                text_to_speech = "Извини, я не очень тебя понял. Можешь повторить?"
            else:
                text_to_speech = "Sorry, i don't understand you. Can you repeat what did you say?"
    model.save_wav(text=text_to_speech, speaker=assistant.speaker, sample_rate=sample_rate)

    winsound.PlaySound('test.wav', winsound.SND_FILENAME)


def record_and_recognize_audio(test=''):
    if test == '':
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
    else:
        if assistant.speech_language == 'en' and assistant.recognition_language == 'ru':
            return translator.translate(test, dest='en').text
        elif assistant.speech_language == 'ru' and assistant.recognition_language == 'en':
            return translator.translate(test, dest='ru').text

        return test


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
    # if assistant.recognition_language == 'ru':
    #     model_name = "sberbank-ai/rugpt3large_based_on_gpt2"
    #     tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    #     using_model = GPT2LMHeadModel.from_pretrained(model_name)
    #     text = message
    #     input_ids = tokenizer.encode(text, return_tensors='pt')
    #     out = using_model.generate(input_ids)
    #     generated_text = list(map(tokenizer.decode, out))[0]
    #     play_voice_assistant_speech(generated_text)
    #     update_user_context(chat_id, generated_text)
    #     print(generated_text)
    # else:
    #     gpt2 = GPT2Client("1558M")
    #     gpt2.load_model(force_download=False)
    #     gpt2.generate(interactive=True)  # Asks user for prompt
    #     gpt2.generate(n_samples=4)  # Generates 4 pieces of text
    #     text = gpt2.generate(return_text=True)  # Generates text and returns it in an array
    #     gpt2.generate(interactive=True, n_samples=3)  # A different prompt each time
    #     play_voice_assistant_speech(text)
    #     update_user_context(chat_id, message)
    #     print(text)
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


assistant = VoiceAssistant('Alice', 'female', 'ru', 'ru')
device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'modelRU.pt' if assistant.speech_language == 'ru' else 'modelEU.pt'

if not os.path.isfile(local_file):
    if local_file == 'modelRU.pt':
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                                       local_file)
    else:
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt',
                                       local_file)
if assistant.speech_language != assistant.recognition_language:
    translator = Translator()
print(local_file)
model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)
sample_rate = 48000

recognizer = speech_recognition.Recognizer()
microphone = speech_recognition.Microphone()

user_context = {0: ""}

while True:
    voice_input = record_and_recognize_audio("Привет. Я хочу сломать тебе руку.")
    # os.remove("test.wav")
    print(voice_input)
    handle_message(voice_input)
    print(user_context)

    voice_input = voice_input.split(" ")
    command = voice_input[0]
    #
    # if command == 'привет':
    #     play_voice_assistant_speech("Здравствуй")
