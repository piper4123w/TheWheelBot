import discord
import json
from wheel.handler import handle_message

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    if message.content.startswith('$hello'):
        await message.channel.send(f'Hello {message.author}! Is anything changing?')
    
    if message.content.startswith('$wheel'):
        print('handling wheel command')
        await handle_message(message)


def get_secret(key):
    with open('secrets.json', 'r') as file:
            data = json.load(file)
            return data[key]

client.run(get_secret('DISCORD_API_TOKEN'))
