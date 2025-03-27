import discord
from discord.ext import commands
import json
from wheel.handler import handle_message

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command(name='hello')
async def handle_hello_command(ctx: commands.Context):
    print('handling hello command')
    await ctx.send(f'Hello {ctx.author}!')


@bot.command(name='wheel')
async def handle_wheel_command(ctx: commands.Context, *, command: str):
        await handle_message(ctx, command)


def get_secret(key):
    with open('secrets.json', 'r') as file:
            data = json.load(file)
            return data[key]

bot.run(get_secret('DISCORD_API_TOKEN'))
