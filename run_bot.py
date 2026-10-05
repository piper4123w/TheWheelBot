import asyncio
import json

import discord
from discord.ext import commands

from wheel.handler import handle_message as wheel_handle
from vote.handler import handle_message as vote_handle
from vote.handler import handle_reaction as vote_handle_reaction
from vote.voting import ACTIVE_VOTE
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
    await wheel_handle(ctx, command)


@bot.command(name='vote')
async def handle_vote_command(
    ctx: commands.Context,
    *,
    command: str
):
    await vote_handle(ctx, command)


@bot.event
async def on_raw_reaction_add(payload):
    # Ignore reactions by bots
    if payload.user_id == bot.user.id:
        return

    # Fetch the message to check its author and content
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    # Check if this is the active vote message
    if ACTIVE_VOTE in message.content:
        await vote_handle_reaction(payload.emoji, message.content)
    else:
        print("Unhandled reaction")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    start_scheduled_jobs(bot)


async def main():
    async with bot:
        await bot.start(get_secret('DISCORD_API_TOKEN'))



def get_secret(key):
    with open('secrets.json', 'r') as file:
        data = json.load(file)

    return data[key]


asyncio.run(main())
