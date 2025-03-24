import json
import random
from discord.ext import commands


async def handle_message(ctx: commands.Context, command):
    if command.startswith(f"add"):
        remainder = command[len("add "):].strip()
        # You can now use item_to_add for further processing
        await parse_add(remainder, ctx)
    elif command.startswith("remove"):
        remainder = command[len("remove "):].strip()
        await parse_remove(remainder, ctx)
    elif command.startswith("list"):
        await list_options(ctx)
    elif command.startswith(f"spin"):
        await spin_wheel(ctx)
    elif "help" in command:
        remainder = command[len("help "):].strip()
        await parse_help(remainder, ctx)
    else:
        await ctx.send("Unknown command. Please use `'list'`, `'add'`, `'remove'`, `'spin'`, or `'help'`.")


async def list_options(ctx: commands.Context):
    message = ctx.send("Listing all items on the wheel...")
    options = await parse_options_message(ctx)
    if options:
        space = "\n\t"
        optionsStr = ""
        for option in options:
            print(f"Option: {option}")  # Debugging line to see each option
            if len(option) > 0:
                optionsStr += f"{space}{option['name']} @ {option['weight']}"
        await message.edit(content=f"Current items on the wheel: {optionsStr}")
    else:
        await message.edit(content="The wheel is empty! Please add items first.")


async def parse_help(remainder: str, ctx: commands.Context):
        if len(remainder) == 0:
            await ctx.send("$wheel - command module for spinning the wheel of fate\n\tCommands: `'add'`, `'remove'`, `'spin'`, `'help'`")
        if "add" in remainder:
            await ctx.send("Usage:\n\t`$wheel add <item>` - Adds an item to the wheel.\n\t`$wheel add <item1>,<item2>,...` - Adds multiple items to the wheel.")
        if "remove" in remainder:
            await ctx.send("Usage:\n\t`$wheel remove <item>` - Removes an item from the wheel.")
        if "list" in remainder:
            await ctx.send("Usage:\n\t`$wheel list` - Lists all items currently on the wheel.")
        if "spin" in remainder:
            await ctx.send("Usage:\n\t`$wheel spin` - Spins the wheel and randomly selects an item.")


async def spin_wheel(ctx: commands.Context):
    message = await ctx.send("Spinning the wheel...")
    result = await get_random_weighted_option(ctx)
    await update_weights(result, ctx)
    await message.edit(content=f"The Wheel has Spoken! The result is `{result}`")


async def get_random_weighted_option(ctx: commands.Context):
    options = await parse_options_message(ctx)
    if not options:
        return None
    weighted_options = []
    for option in options:
        weighted_options.extend([option['name']] * option['weight'])    
    return random.choice(weighted_options)


async def update_weights(picked_option, ctx: commands.Context):
    """
    Updates the weights of the options in the options file based on the picked option.

    This function increments all option weights by 1, except for the picked option,
    which is reset to 0. This is used to adjust the likelihood of each option being
    picked in future spins of the wheel.

    Args:
        picked_option (str): The option that was picked from the wheel.

    Returns:
        None
    """
    # options = parse_options_file()
    options = await parse_options_message(ctx)
    for option in options:
        if option['name'] != picked_option:
            option['weight'] += 1
        else:
            option['weight'] = 0
    # save_options_file(options)
    await save_options_message(options, ctx)


async def parse_add(addition: str, ctx: commands.Context):
    """
    Asynchronously parses and adds new items to the wheel.

    This function takes a string of items to add to the wheel and a message object.
    If the string contains multiple items separated by commas, it splits them into a list,
    checks for duplicates, and adds the new items to the wheel. If the string contains a single item,
    it adds that item directly to the wheel.

    Args:
        addition (str): The string containing the item(s) to add to the wheel.
        message: The message object from the Discord API.

    Returns:
        None
    """
    message = ctx.send(f"Adding '{addition}' to the wheel...")
    if len(addition) == 0:
        await message.edit(content="Please specify a new item to add.")
        return
    if "," in addition:
        additions = [item.strip() for item in addition.split(",")]
        options = await parse_options_message(ctx)
        new_additions = [item for item in additions if item not in options]
        if new_additions:
            await message.edit(content=f"Adding the following items to the wheel: {', '.join(new_additions)}")
            for name in new_additions:
                options.append({'name': name, 'weight': 1})
            await save_options_message(ctx, options)
        else:
            await message.edit(content="All the items are already in the wheel.")
    else:
        await message.edit(content=f"Adding '{addition}' to the wheel!")
        options = await parse_options_message(ctx)
        options.append({'name':addition, 'weight':1})
        await save_options_message(ctx, options)


async def parse_remove(removal: str, ctx: commands.Context):
    """
    Asynchronously parses and removes an item from the wheel.

    This function takes a string of the item to remove from the wheel and a message object.
    It checks if the item exists in the wheel and removes it if found.

    Args:
        removal (str): The string containing the item to remove from the wheel.
        message: The message object from the Discord API.

    Returns:
        None
    """
    if len(removal) == 0:
        await ctx.send("Please specify an item to remove.")
        return
    message = ctx.send(f"Removing '{removal}' from the wheel...")
    options = await parse_options_message(ctx)
    for option in options:
        if option['name'] == removal:
            options.remove(option)
            await save_options_message(options, ctx)
            await message.edit(content=f"Removed '{removal}' from the wheel!")
            return
    await message.edit(content=f"'{removal}' is not in the wheel.")


async def parse_options_message(ctx: commands.Context):
    for channel in ctx.guild.text_channels:
        if channel.name == "wheel_data":
            pins = await channel.pins()
            for message in pins:
                if message.author == ctx.bot.user:
                    try:
                        data = json.loads(message.content)
                        return data['options']
                    except json.JSONDecodeError:
                        print("Error decoding the pinned message content.")
                        return []
    return []


async def save_options_message(items, ctx: commands.Context):
    for channel in ctx.guild.text_channels:
        if channel.name == "wheel_data":
            pins = await channel.pins()
            for message in pins:
                if message.author == ctx.bot.user:
                    jsonStr = json.dumps({"options":items}, indent=4)
                    await message.edit(content=jsonStr)
