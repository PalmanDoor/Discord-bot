import os
import sys
import requests
import discord
import discord.ext
from discord.ext import commands
import openai
import difflib
import aiohttp
import nacl
import praw
from io import BytesIO
from bs4 import BeautifulSoup
import datetime
import asyncio
import random
import time
from openai import Completion
from keep_alive import keep_alive

# Установите ключ Openal API
api_key = 'ключ_OpenAI_API'
openai.api_key = api_key

# Установите токен бота Discord
token = os.getenv('токен_бота_Discord')

# Создать клиент Discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix= '//', intents=intents)

# Функция отправки сообщений в Discord
async def send_message(channel_id, message):
    channel = client.get_channel(channel_id)
    await channel.send(message)

async def on_message(message):
    print(f"Received message: {message.content}")

# Создать переменную для хранения времени последнего запроса
last_request_time = 0

async def restart_bot():
    await client.close()
    os.execv(sys.executable, ['python'] + sys.argv)

async def background_task():
    while True:
        await asyncio.sleep(43200)
        await restart_bot()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Помощь //gpt"))
    print(f'{client.user} has connected to Discord!')
    client.loop.create_task(background_task())

folder_path = './rimg'  # путь к папке с изображениями

def is_admin(author):
    if author.guild_permissions.administrator:
        return True
    for role in author.roles:
        if role.permissions.administrator:
            return True
    return False

@client.event
async def on_message(message):
    if not message.author.bot:
        stats_message = f'{datetime.datetime.now()};{message.author.name};{message.channel.name};{message.content}\n'
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(stats_message)

@client.event
async def on_message(message):
    global last_request_time

    if message.author == client.user:
        return

    if message.content.startswith('//'):
        if message.content.startswith('//gpt'):
            embed = discord.Embed(title='Как использовать бота', description='Привет! Я бот, который может генерировать текст на основе заданного контекста. Для использования меня введите мое имя @Skiffy, затем напишите свой текст, и я сгенерирую продолжение для него. Если генерация занимает более 15 секунд, я попрошу вас подождать. Если сгенерированный текст слишком длинный для одного сообщения, я разделю его на части по 2000 символов. Существует команда //try (ваш текст) она выглядит так @Skiffy попытался (ваш текст) и него получилось либо не получилось.')
            await message.channel.send(embed=embed)
        
        elif message.content.startswith('//try'):
            embed = discord.Embed(title='', description=f"**{message.author.name}** попытался {message.content[6:]} и у него {'' if random.random() > 0.5 else 'не '}получилось.", color=discord.Color.green())
            await message.channel.send(embed=embed)
        
        elif message.content.startswith('//donate'):
            await message.channel.send('Вы можете поддержать нашего бота перейдя по ссылке: qiwi.com/n/HITAB204') 
            
        elif message.content.startswith('//search'):
            query = message.content[9:]  # Получаем тему запроса
            search_folder = os.path.join(os.getcwd(), 'Search')  # Путь к папке Search

            # Получаем список всех папок в папке Search
            all_folders = [folder for folder in os.listdir(search_folder) if os.path.isdir(os.path.join(search_folder, folder))]

            # Используем модуль difflib для нахождения наиболее похожей папки
            closest_folder = difflib.get_close_matches(query, all_folders, n=1)

            if closest_folder:
                folder_path = os.path.join(search_folder, closest_folder[0])
                file_list = os.listdir(folder_path)

                # Отправляем текстовый файл
                text_files = [file for file in file_list if file.endswith('.txt')]
                for text_file in text_files:
                    file_path = os.path.join(folder_path, text_file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    await message.channel.send(text)

                # Отправляем изображения
                image_files = [file for file in file_list if file.endswith(('.png', '.jpg', '.jpeg'))]
                for image_file in image_files:
                    file_path = os.path.join(folder_path, image_file)
                    await message.channel.send(file=discord.File(file_path))
            
            else:
                await message.channel.send('По вашему запросу ничего не найдено.')
                
        # Выключено @---
        
        # elif message.content.startswith('//bl'):
            # path = './rimg'  # путь к папке с изображениями (удалена)
            # image = random.choice(os.listdir(path))  # выбираем случайное изображение
            # await message.delete()  # удаляем сообщение пользователя
            # await message.channel.send(f'{message.author.mention} вот рандомное изображение', file=discord.File(os.path.join(path, image)))
            
        # @---
        
        elif message.content.startswith('//image'):
            search_term = message.content[8:]
            url = f'https://www.bing.com/images/search?q={search_term}&form=HDRSC2&first=1&tsc=ImageBasicHover&cw=1309&ch=602&scenario=ImageBasicHover&dpr=1&thid=OIP.EY9I4g4L4CvsiplGk0KDLwHaHa&mediaurl=https%3A%2F%2Fencrypted-tbn0.gstatic.com%2Fimages%3Fq%3Dtbn%3AANd9GcQo7fM_9XKjxVq3vLZxx7Nk-6gMLFO6IJjK6A%26usqp%3DCAU&exph=600&expw=600&qft=+filterui:imagesize-large&simid=608051586662411862&ck=9D4F129E8F4FA22E3E3AED0965514327&selectedIndex=0&ajaxhist=0&ajaxserp=0&safeSearch=off'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.text
                start = data.find('https://tse2.mm.bing.net/')
                end = data.find('&', start)
                if start != -1 and end != -1:
                    link = data[start:end]
                    await message.channel.send(f'{message.author.name}, вот твоя картинка по запросу "{search_term}":', file=discord.File(BytesIO(requests.get(link).content), filename='image.png'))
                    await message.delete()
                else:
                    await message.channel.send(f'Изображения по запросу "{search_term}" не найдены')
            else:
                await message.channel.send(f'Ошибка при поиске изображений по запросу "{search_term}"')
                
        elif message.content.startswith('//reload'):
            if not is_admin(message.author):
                await message.channel.send("Вы не имеете права использовать эту команду.")
                return
            await message.channel.send("Перезагрузка бота...")
            try:
                os.execv(sys.executable, ['python'] + sys.argv)
            except:
                await message.channel.send("Произошла ошибка при перезагрузке бота.")
            await client.logout()

        # проверяет, упоминается ли бот в сообщении
    if client.user.mentioned_in(message):
        # рассчитать время с момента последнего запроса
        time_since_last_request = time.time() - last_request_time
        # проверяет, достаточно ли времени прошло с момента последнего запроса
        if time_since_last_request < 10:
            # рассчитывает время, оставшееся до разрешения следующего запроса
            time_remaining = 10 - time_since_last_request
            # отправляет сообщение с оставшимся временем
            await message.channel.send(f"```Не прошло достаточно времени с момента последнего запроса. Пожалуйста, подождите {int(time_remaining)} секунд, прежде чем попробовать снова.```")
        else:
            response = openai.Completion.create(
                engine='text-davinci-003', # Модель для генерации, доступно: text-davinci-002, text-davinci-003, ChatGPT-2, ChatGPT-3, ChatGPT-4, DALLE-2
                prompt=f'{message.content}',
                temperature=0.5,
                max_tokens=2048,
            )

            if len(response.choices[0].text) > 2000:
                # разделяет сообщение на фрагменты по 2000 символов
                chunks = [response.choices[0].text[i:i+2000] for i in range(0, len(response.choices[0].text), 2000)]
                # отправляет каждый фрагмент в виде отдельного сообщения
                for chunk in chunks:
                    await message.channel.send(chunk)
                    # ждет 1 секунду перед отправкой следующего сообщения
                    await asyncio.sleep(1)
            elif response.choices[0].text:
                await message.channel.send(response.choices[0].text)
            else:
                await message.channel.send("Я не понимаю вас, пожалуйста, уточните вопрос.")
            
            # обновиляет last_request_time до текущего времени
            last_request_time = time.time()

# Запускает веб-сервер, чтобы поддерживать работу бота
keep_alive()

# Ищет токен бота и запускает бота
token = open( 'token.txt', 'r' ).readline()

client.run( token )
