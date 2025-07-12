import json
import random
from discord.ext import commands

# Constants for command names
ADD = "add"
REMOVE = "remove"
LIST = "list"
SPIN = "spin"
HELP = "help"
TAG = "tag"
RESET = "reset"
COMMANDS = [ADD, REMOVE, LIST, SPIN, HELP, TAG, RESET]

# Constants for entry fields
OPTIONS = "options"
NAME = "name"
WEIGHT = "weight"
TAGS = "tags"


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
        - reset <subcommand>: Resets the wheel options, weights, or tags.

    If the command is not recognized, it sends an error message indicating the valid commands.
    """
    if command.startswith(ADD):
        remainder = command[len(f"{ADD} "):].strip()
        # You can now use item_to_add for further processing
        await parse_add(remainder, ctx)
    elif command.startswith(REMOVE):
        remainder = command[len(f"{REMOVE} "):].strip()
        await parse_remove(remainder, ctx)
    elif command.startswith(LIST):
        remainder = command[len(f"{LIST} "):].strip()
        await list_options(remainder, ctx)
    elif command.startswith(SPIN):
        remainder = command[len(f"{SPIN} "):].strip()
        await spin_wheel(remainder, ctx, debug=("debug" in remainder.lower()))
    elif command.startswith(HELP):
        remainder = command[len(f"{HELP} "):].strip()
        await parse_help(remainder, ctx)
    elif command.startswith(TAG):
        remainder = command[len(f"{TAG} "):].strip()
        await parse_tag(remainder, ctx)
    elif command.startswith(RESET):
        remainder = command[len("reset "):].strip()
        await parse_reset(remainder, ctx)
    else:
        await ctx.send(f"Unknown command. Please use `{', '.join(COMMANDS)}`.")


async def parse_tag(remainder: str, ctx: commands.Context):
    """    Parses the tag command and handles adding or removing tags from options."""
    parts = remainder.split()
    if len(parts) != 2:
        await ctx.send(f"Usage:\n\t`$wheel {TAG} <item> <tags_separated_by_commas>`")
        return
    tags = parts[0].split(",")
    item = parts[1:].join(" ")
    if ',' in tags:
        for tag in tags:
            if not tag:
                await ctx.send("Tag cannot be an empty string.")
                return
            await add_tag_to_item(item, tag, ctx)
        return
    await add_tag_to_item(item, tags, ctx)


async def add_tag_to_item(item: str, tag: str, ctx: commands.Context):
    """
    Adds a tag to an item in the wheel options.

    Args:
        item (str): The name of the item to which the tag will be added.
        tag (str): The tag to be added to the item.
        ctx (commands.Context): The context of the command invocation.
    """
    options = await parse_options_message(ctx)
    for option in options:
        if option[NAME] == item:
            if TAGS not in option:
                option[TAGS] = []
            if tag not in option[TAGS]:
                option[TAGS].append(tag)
                await save_options_message(options, ctx)
                await ctx.send(f"Added tag `{tag}` to item `{item}`.")
                return
            else:
                await ctx.send(f"Item `{item}` already has tag `{tag}`.")
                return
    await ctx.send(f"Item `{item}` not found.")


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
        - "weight": Resets all weights to their default value of 1.
        - "tag": Resets all tags to an empty list.
        - "options": Prompts the user for confirmation before resetting all options to their default values.
    """
    if remainder.startswith(HELP) or len(remainder) == 0:
        await ctx.send("Usage:\n\t`$wheel {RESET} "
                        "\n[SUBCOMMANDS]`" \
                        "\n\t`options` - Resets the wheel options to an empty list." \
                        "\n\t`weights` - Resets the wheel weights to the default values." \
                        "\n\t`tags` - Resets the wheel tags to an empty list." \
                        "\n\t`help` - Displays this help message.")
    elif remainder.startswith(WEIGHT):
        message = await ctx.send("Resetting all weights to 1...")
        await reset_weights(ctx)
        await message.edit(content="All weights have been reset to 1.")
    elif remainder.startswith(TAG):
        message = await ctx.send("Resetting all tags to an empty list...")
        options = await parse_options_message(ctx)
        for option in options:
            option[TAGS] = []
        await save_options_message(options, ctx)
        await message.edit(content="All tags have been reset to an empty list.")
    elif remainder.startswith(OPTIONS):
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
        option[WEIGHT] = 1
    await save_options_message(options, ctx)


async def list_options(remainder: str, ctx: commands.Context):
    """
    Lists all options currently on the wheel.

    This function sends a message to the context channel indicating that it is listing all items on the wheel.
    It then retrieves the options from the wheel and formats them into a string, which is used to update the message.
    If there are no items on the wheel, it updates the message to indicate that the wheel is empty.

    Args:
        ctx (commands.Context): The context in which the command was invoked.
    remainder (str): The remainder of the command.
    Usage:
        - `$wheel list`: Lists all items currently on the wheel.
        - `$wheel list [TAG]`: Lists all items filtered by the specified tag.
    Returns:
        None
    """
    if len(remainder) == 0:
        message = await ctx.send("Listing all items on the wheel...")
        options = await parse_options_message(ctx)
        if options:
            space = "\n\t"
            optionsStr = ""
            for option in options:
                print(f"Option: {option}")  # Debugging line to see each option
                optionsStr += f"{space}{option[NAME]} @ {option[WEIGHT]}"
                if TAGS in option and option[TAGS]:
                    optionsStr += f" - Tags: {', '.join(option[TAGS])}"
            await message.edit(content=f"Current items on the wheel: {optionsStr}")
        else:
            await message.edit(content="The wheel is empty! Please add items first.")
    else:
        message = await ctx.send(f"Listing all items with tag '{remainder}' on the wheel...")
        options = await parse_options_message(ctx)
        filtered_options = [option for option in options if TAGS in option and remainder in option[TAGS]]
        if filtered_options:
            space = "\n\t"
            optionsStr = ""
            for option in filtered_options:
                print(f"Option: {option}")
                if len(option) > 0:
                    optionsStr += f"{space}{option[NAME]} @ {option[WEIGHT]}"
            await message.edit(content=f"Current items on the wheel with tag '{remainder}':{optionsStr}")



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
            - `$wheel help tag`: Displays usage instructions for adding or removing tags from items.
            - `$wheel help reset`: Displays usage instructions for resetting the wheel options or weights.
        """
        if len(remainder) == 0:
            await ctx.send(f"$wheel - command module for spinning the wheel of fate\n\tCommands: `{ADD}`, `{REMOVE}`, `{SPIN}`, `{HELP}`")
        if ADD in remainder:
            await ctx.send(f"Usage:\n\t`$wheel {ADD} <item>` - Adds an item to the wheel.\n\t`$wheel {ADD} <item1>,<item2>,...` - Adds multiple items to the wheel.")
        if REMOVE in remainder:
            await ctx.send(f"Usage:\n\t`$wheel {REMOVE} <item>` - Removes an item from the wheel.")
        if LIST in remainder:
            await ctx.send(f"Usage:\n\t`$wheel {LIST}` - Lists all items currently on the wheel.")
        if SPIN in remainder:
            await ctx.send(f"Usage:\n\t`$wheel {SPIN}` - Spins the wheel and randomly selects an item.")
        if TAG in remainder:
            await ctx.send(f"Usage:\n\t`$wheel {TAG} <tags> <item>` - Adds tags to an item.\n\t`$wheel {TAG} <tag1>,<tag2>,... <item>` - Adds multiple tags to an item.")
        if RESET in remainder:
            await ctx.send(f"Usage:\n\t`$wheel {RESET} "
                           "\n[SUBCOMMANDS]`" \
                           "\n\t`options` - Resets the wheel options to an empty list." \
                           "\n\t`weights` - Resets the wheel weights to the default values." \
                           "\n\t`tags` - Resets the wheel tags to an empty list." \
                           "\n\t`help` - Displays this help message.")



async def spin_wheel(remainder: str, ctx: commands.Context, debug=False):
    """
    Spins a virtual wheel and sends the result to the Discord channel.

    This function sends a message indicating that the wheel is spinning,
    determines a random weighted option, updates the weights accordingly,
    and then edits the original message to display the result.

    It also Pins that message in the chat and then creates a scheduled event
    in the guild for the selected option.

    If there is a remainder in the command, it is assumed to be a list of tags to filter the wheel's options.

    Args:
        remainder (str): The remainder of the command, which can be used to pass additional parameters.
        ctx (commands.Context): The context in which the command was invoked.
        debug (bool): If True, runs in debug mode, which does not update weights or create events.

    """
    # TODO: create event?
    if len(remainder) == 0:
        print("Spinning the wheel...")
        message = await ctx.send( "Spinning the wheel..." if debug == False else "Debug mode - spinning the wheel...")
        result = await get_random_weighted_option(ctx)
        if not debug:
            await update_weights(result, ctx)
        await message.edit(content=f"The Wheel has Spoken! The result is `{result}`")
        await message.pin()
    else:
        tags = remainder.split(",")
        print(f"Spinning the wheel with tags: {remainder}")
        message = await ctx.send(f"Spinning the wheel with tags: {remainder}" if debug == False else "Debug mode - spinning the wheel with tags...")
        options = await parse_options_message(ctx)
        filtered_options = [
            option for option in options
            if TAGS in option and all(tag.strip() in option[TAGS] for tag in tags if tag.strip())
        ]
        if not filtered_options:
            await message.edit(content=f"No options found with the given tags `{remainder}`.")
            return
        weighted_options = []
        for option in filtered_options:
            weighted_options.extend([option[NAME]] * option[WEIGHT])
        result = random.choice(weighted_options)
        if not debug:
            await update_weights(result, ctx)
        await message.edit(content=f"The Wheel has Spoken! The result given the tags `{remainder}` is `{result}`")
        await message.pin()


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
        weighted_options.extend([option[NAME]] * option[WEIGHT])
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
        if option[NAME] != picked_option:
            option[WEIGHT] += 1
        else:
            option[WEIGHT] = 0
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
        new_additions = [item for item in additions if item not in options and item.strip() != ""]
        if new_additions:
            await message.edit(content=f"Adding the following items to the wheel: {', '.join(new_additions)}")
            for name in new_additions:
                options.append({NAME: name, WEIGHT: 1})
            await save_options_message(options, ctx)
            await message.edit(content=f"Added the following items to the wheel: {', '.join(new_additions)}")
        else:
            await message.edit(content="All the items are already in the wheel.")
    else:
        if addition.strip() != "":
            options = await parse_options_message(ctx)
            options.append({NAME: addition, WEIGHT: 1})
            await message.edit(content=f"Added '{addition}' to the wheel!")
            await save_options_message(options, ctx)
        else:
            await message.edit(content="Option cannot be an empty string, Please specify a new item to add.")


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
    message = await ctx.send(f"Removing '{removal}' from the wheel...")
    options = await parse_options_message(ctx)
    for option in options:
        if option[NAME] == removal:
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
                        return data[OPTIONS]
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
                    jsonStr = json.dumps({OPTIONS:items}, indent=4)
                    await message.edit(content=jsonStr)
                    return # If the message is found and edited, exit the function
            # If no message was found, create a new one
            jsonStr = json.dumps({OPTIONS:items}, indent=4)
            new_message = await channel.send(jsonStr)
            await new_message.pin()
