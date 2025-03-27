import json
import random
from discord.ext import commands


async def handle_message(ctx: commands.Context, command):
    """
    Handles incoming messages and executes the appropriate command.

    Args:
        ctx (commands.Context): The context in which a command is being invoked under.
        command (str): The command string to be processed.

    Commands:
        - add <item>: Adds an item to the list.
        - remove <item>: Removes an item from the list.
        - list: Lists all items.
        - spin: Spins the wheel.
        - help <command>: Provides help information for a specific command.

    If the command is not recognized, it sends an error message indicating the valid commands.
    """
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
    # -- ADMIN COMMANDS --
    elif command.startswith("reset"):
        remainder = command[len("reset "):].strip()
        await parse_reset(remainder, ctx)
    else:
        await ctx.send("Unknown command. Please use `'list'`, `'add'`, `'remove'`, `'spin'`, or `'help'`.")


async def parse_reset(remainder: str, ctx: commands.Context):
    """
    ADMIN: Handles the reset command for the wheel bot.

    This function processes subcommands related to resetting the wheel's options or weights.
    It provides help information, resets weights to default values, or prompts the user for
    confirmation before resetting options.

    Args:
        remainder (str): The subcommand or additional arguments provided by the user.
        ctx (commands.Context): The context of the command invocation, including the bot and message details.

    Subcommands:
        - "help": Displays usage instructions for the reset command.
        - "weights": Resets all weights to their default value of 1.
        - "options": Prompts the user for confirmation before resetting all options to their default values.
    """
    if remainder.startswith("help") or len(remainder) == 0:
        await ctx.send("ADMIN ONLY - Usage:\n\t`$wheel reset [SUBCOMMAND]`\n\t`options` - Resets the wheel options to the default values.\n\t`weights` - Resets the wheel weights to the default values.")
    elif remainder.startswith("weights"):
        message = await ctx.send("Resetting all weights to 1...")
        await reset_weights(ctx)
        await message.edit(content="All weights have been reset to 1.")
    elif remainder.startswith("options"):
        message = await ctx.send("Resetting all options...")
        await reset_options(ctx)
        await message.edit(content="All options have been reset.")


async def reset_options(ctx: commands.Context):
    """
    Resets the options for the wheel by clearing the current options and saving an empty list.

    Args:
        ctx (commands.Context): The context of the command invocation, which provides
            information about the execution state and allows interaction with the Discord API.
    """
    await save_options_message([], ctx)


async def reset_weights(ctx: commands.Context):
    """
    Resets the weights of all options in the context to their default value of 1.

    Args:
        ctx (commands.Context): The context of the command, which includes the message and other metadata.

    This function retrieves the options from the context, updates their weights to 1, 
    and saves the updated options back to the context.
    """
    options = await parse_options_message(ctx)
    for option in options:
        option['weight'] = 1
    await save_options_message(options, ctx)


async def list_options(ctx: commands.Context):
    """
    Lists all options currently on the wheel.

    This function sends a message to the context channel indicating that it is listing all items on the wheel.
    It then retrieves the options from the wheel and formats them into a string, which is used to update the message.
    If there are no items on the wheel, it updates the message to indicate that the wheel is empty.

    Args:
        ctx (commands.Context): The context in which the command was invoked.

    Returns:
        None
    """
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
        """
        Parses the help command and sends appropriate usage instructions based on the remainder of the command.

        Args:
            remainder (str): The remaining part of the command after the initial help keyword.
            ctx (commands.Context): The context in which the command was invoked.

        Usage:
            - `$wheel` or `$wheel help`: Displays the general help message for the wheel command module.
            - `$wheel help add`: Displays usage instructions for adding items to the wheel.
            - `$wheel help remove`: Displays usage instructions for removing items from the wheel.
            - `$wheel help list`: Displays usage instructions for listing all items on the wheel.
            - `$wheel help spin`: Displays usage instructions for spinning the wheel.
        """
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
    """
    Spins a virtual wheel and sends the result to the Discord channel.

    This function sends a message indicating that the wheel is spinning,
    determines a random weighted option, updates the weights accordingly,
    and then edits the original message to display the result.

    Args:
        ctx (commands.Context): The context in which the command was invoked.

    Returns:
        None
    """
    message = await ctx.send("Spinning the wheel...")
    result = await get_random_weighted_option(ctx)
    await update_weights(result, ctx)
    await message.edit(content=f"The Wheel has Spoken! The result is `{result}`")


async def get_random_weighted_option(ctx: commands.Context):
    """
    Asynchronously retrieves a random weighted option from a list of options.

    This function parses a message to extract options, each with an associated weight,
    and then randomly selects one of the options based on their weights.

    Args:
        ctx (commands.Context): The context of the command invocation.

    Returns:
        str: The name of the randomly selected option based on weight, or None if no options are available.
    """
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
    message = await ctx.send(f"Adding '{addition}' to the wheel...")
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
            await save_options_message(options, ctx)
            await message.edit(content=f"Added the following items to the wheel: {', '.join(new_additions)}")
        else:
            await message.edit(content="All the items are already in the wheel.")
    else:
        await message.edit(content=f"Added '{addition}' to the wheel!")
        options = await parse_options_message(ctx)
        options.append({'name':addition, 'weight':1})
        await save_options_message(options, ctx)


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
    """
    Parses the pinned message in the 'wheel_data' text channel and extracts options.

    This function iterates through all text channels in the guild to find the 
    'wheel_data' channel. It then retrieves all pinned messages in that channel 
    and looks for a message authored by the bot. If such a message is found, it 
    attempts to parse the message content as JSON and extract the 'options' field.

    Args:
        ctx (commands.Context): The context of the command invocation.

    Returns:
        list: A list of options extracted from the pinned message content. 
              Returns an empty list if no valid pinned message is found or if 
              there is an error decoding the JSON content.
    """
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
    """
    Asynchronously saves the given items as a JSON string in a pinned message in the "wheel_data" text channel.

    Args:
        items (list): The list of items to be saved.
        ctx (commands.Context): The context in which the command was invoked, providing access to the guild and bot.
    """
    for channel in ctx.guild.text_channels:
        if channel.name == "wheel_data":
            pins = await channel.pins()
            for message in pins:
                if message.author == ctx.bot.user:
                    jsonStr = json.dumps({"options":items}, indent=4)
                    await message.edit(content=jsonStr)
