# bot.py
import os

import discord
from dotenv import load_dotenv

import requests
import time, threading


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    
    global SERVER_CHECK_URL
    SERVER_CHECK_URL = get_global_from_config('server_check_url')
    
    global BATCH_PATH
    BATCH_PATH = get_global_from_config('bat_file')

    global SERVER_LOGS_PATH
    SERVER_LOGS_PATH = get_global_from_config('server_logs_path')

    global SERVER_DIRECTORY_PATH
    SERVER_DIRECTORY_PATH = get_global_from_config('server_directory_path')

    global SERVER_IP_ADDRESS
    SERVER_IP_ADDRESS = os.getenv('IP')
    
    global ADMIN_DISCORD_ID
    ADMIN_DISCORD_ID = get_global_from_config('admin_discord_id') 

    global BOT_CHANNEL
    BOT_CHANNEL = get_global_from_config('bot_channel_name')

    threading.Timer(60 * 20, on_save_timer).start()
    on_save_timer()

    channel = discord.utils.get(client.get_all_channels(), name=BOT_CHANNEL)

    await channel.purge()
    await send_prompt(channel)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.channel) == BOT_CHANNEL:
        print("BEEP BOOP MESSAGE DETECTED")
        print('message author id: ' + str(message.author.id))
        if ('/' in message.content) and (message.author.id == ADMIN_DISCORD_ID):
            command = message.content[message.content.index('/')+1::]
            print("Sending command: " + str(command))
            server_command(command)
            time.sleep(0.2)
            output = open(SERVER_LOGS_PATH + 'latest.log').read()
            output = output[output.rindex('[')::]
            await message.channel.purge(limit=1)
            await message.channel.send('```' + output + '```')
        if message.content.lower() == 'clear':
            await message.channel.purge()
            await send_prompt(message.channel)
    
async def send_prompt(channel):
    view = discord.ui.View(timeout=None)
    
    status_button = discord.ui.Button(label='Status', custom_id='status-id', style=discord.ButtonStyle.blurple)
    status_button.callback = on_status_button
    view.add_item(status_button)

    logs_button = discord.ui.Button(label='Get logs', custom_id='terminal-id', style=discord.ButtonStyle.secondary)
    logs_button.callback = on_logs_button
    view.add_item(logs_button)

    start_button = discord.ui.Button(label='Start Server', custom_id='start-id', style=discord.ButtonStyle.success)
    start_button.callback = on_start_button
    view.add_item(start_button)
    
    
    await channel.send(content="# Server Status Bot", view=view)

async def on_status_button(interaction : discord.Interaction):
    status_string : str = pull_status()
    emoji = ''
    # channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    if status_string == 'Online':
        emoji = ':white_check_mark: '
    else:
        emoji = ':octagonal_sign: '
    text = '# Server Status Bot\n> ## The server is currently: \n> ' + emoji + ' **' + status_string + '**'
    text += '\n> ###  :wireless:  ' + SERVER_IP_ADDRESS + '\n'
    text += '\n> ### **Players Online**: \n' + pull_player_list() + '\n'
    await interaction.response.edit_message(content=text)

async def on_logs_button(interaction : discord.Interaction):
    output = open(SERVER_LOGS_PATH + 'latest.log').read()
    send = '```'
    output = output.splitlines()
    output = output[::-1]
    output = output[0:10:]
    output = output[::-1]
    for line in output:
        send += line + '\n'
    send = send[-350::]
    send = '```' + send + '```'
    await interaction.channel.purge()
    await send_prompt(interaction.channel)
    time.sleep(0.2)
    await interaction.response.send_message(send)

async def on_start_button(interaction : discord.Interaction):
    additional_admin = 767538898737037362 
    if interaction.user.id == ADMIN_DISCORD_ID or interaction.user.id == additional_admin:
        os.chdir(SERVER_DIRECTORY_PATH)
        os.system(BATCH_PATH)
        await interaction.response.send_modal(discord.ui.Modal(title='Server Start signal sent', timeout=2))
        print(BATCH_PATH)

# Sync functions
def pull_status():
    try:
        response = requests.get(SERVER_CHECK_URL+SERVER_IP_ADDRESS)
        
        response.raise_for_status()
        data = response.json()
        return "Online" if data.get('online') else "Offline"
            
    except Exception as e:
        print(f"Error fetching status: {e}")
        return "Unknown/Error"

def pull_player_list():
    try:
        names = []
        player_list=''
        server_command('list')
        output = open(SERVER_LOGS_PATH + 'latest.log').read()
        output = output[output.rindex('online:')+len('online:')::]
        names = output.split(',')
        for name in names:
            player_list += '> * ' + name + '\n'

        return player_list
    except:
        return ''

def get_global_from_config(config_string):
    global_element = open('bot.config').read()
    global_element = global_element[global_element.index(config_string+': ')::]
    global_element = global_element[global_element.index(':') + 2:global_element.index('\n'):]

    return global_element

def get_name_between_spans(string):
    string = string[string.index('>')+1::]
    string = string[string.index('>')+1::]
    string = string[:string.index('<'):]

    return string

def server_command(cmd):
    os.system(f'screen -S minecraft-server-screen -X stuff "{cmd}\n"')

def on_save_timer():
    server_command('save-all')

client.run(TOKEN)
