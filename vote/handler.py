from discord.ext import commands
import uuid

from vote.voting import Vote, ACTIVE_VOTE, COMPLETE_VOTE_EMOJI

START = "start"
HELP = "help"
COMMANDS = [START, HELP]


async def handle_message(ctx: commands.Context, command):
    """
    Handles incoming messages and executes the appropriate command.

    Args:
            ctx (commands.Context): The context in which a command is being invoked under.
            command (str): The command string to be processed.
    
    """
    if command.startswith(START):
        remainder = command[len(f"{START} "):].strip()
        await parse_start(remainder, ctx)
    else:
        await ctx.send(f"Unknown command. Please use `{', '.join(COMMANDS)}`.")


async def handle_reaction(emoji, messageContent: str):
    if(emoji.name == COMPLETE_VOTE_EMOJI):
        print("TODO: Parse the messageContent into a vote object")


async def parse_start(remainder: str, ctx: commands.Context):
    """ Parses the vote start command"""
    options = remainder.split(',')
    if len(options) <= 1:
        await ctx.send(f"Usage:\n\t$vote {START} <opt1>,<opt2>,...<optN>"
                       + "There must be at least 2 options to start a vote")
    
    vote = Vote(
        bot=ctx.bot,
        channel_id=ctx.channel.id,
        title_key=uuid.uuid1(),
        options=options
    )

    await vote.create()

    print(f"A new vote was called by {ctx.message.author}")