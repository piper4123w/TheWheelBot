import asyncio
import json

import discord
from discord.ext import commands

from wheel.handler import handle_message
from availability.scheduled import start_scheduled_jobs


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='$',
    intents=intents
)


@bot.command(name='hello')
async def handle_hello_command(ctx: commands.Context):
    print('handling hello command')
    await ctx.send(f'Hello {ctx.author}!')


@bot.command(name='wheel')
async def handle_wheel_command(
    ctx: commands.Context,
    *,
    command: str
):
    await handle_message(ctx, command)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def main():
    async with bot:
        start_scheduled_jobs(bot)

        await bot.start(get_secret('DISCORD_API_TOKEN'))


def get_secret(key):
    with open('secrets.json', 'r') as file:
        data = json.load(file)

    return data[key]


asyncio.run(main())
