import json
import random
import asyncio


MODULE_COMMAND="$wheel"


async def handle_message(message):
    if message.content.startswith(f"{MODULE_COMMAND} add"):
        remainder = message.content[len("$wheel add "):].strip()
        # You can now use item_to_add for further processing
        await parse_add(remainder, message)
    elif message.content.startswith(f"{MODULE_COMMAND} remove"):
        remainder = message.content[len("$wheel remove "):].strip()
        await parse_remove(remainder, message)
    elif message.content.startswith(f"{MODULE_COMMAND} list"):
        await list_options(message)
    elif message.content.startswith(f"{MODULE_COMMAND} spin"):
        await spin_wheel(message)
    elif "help" in message.content:
        remainder = message.content[len("$wheel help "):].strip()
        await parse_help(remainder, message)
    else:
        await message.channel.send("Unknown command. Please use `'list'`, `'add'`, `'remove'`, `'spin'`, or `'help'`.")


async def list_options(message):
    options = parse_options_file()
    if options:
        optionsStr = "\n\t" + "\n\t".join(options)
        await message.channel.send(f"Current items on the wheel: {optionsStr}")
    else:
        await message.channel.send("The wheel is empty! Please add items first.")


async def parse_help(remainder: str, message):
        if len(remainder) == 0:
            await message.channel.send("$wheel - command module for spinning the wheel of fate\n\tCommands: `'add'`, `'remove'`, `'spin'`, `'help'`")
        if "add" in remainder:
            await message.channel.send("Usage:\n\t`$wheel add <item>` - Adds an item to the wheel.\n\t`$wheel add <item1>,<item2>,...` - Adds multiple items to the wheel.")
        if "remove" in remainder:
            await message.channel.send("Usage:\n\t`$wheel remove <item>` - Removes an item from the wheel.")
        if "list" in remainder:
            await message.channel.send("Usage:\n\t`$wheel list` - Lists all items currently on the wheel.")
        if "spin" in remainder:
            await message.channel.send("Usage:\n\t`$wheel spin` - Spins the wheel and randomly selects an item.")


async def spin_wheel(message):
    await message.channel.send("Spinning the wheel...")
    options = parse_options_file()
    if not options:
        await message.channel.send("The wheel is empty! Please add items first.")
        return
    else:
        await list_options(message)
    await asyncio.sleep(3) # pause for dramatic effect
    result = random.choice(options)
    await message.channel.send(f"...and the result is: {result}")


async def parse_add(addition: str, message):
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
    if len(addition) == 0:
        await message.channel.send("Please specify a new item to add.")
        return
    if "," in addition:
        additions = [item.strip() for item in addition.split(",")]
        options = parse_options_file()
        new_additions = [item for item in additions if item not in options]
        if new_additions:
            await message.channel.send(f"Adding the following items to the wheel: {', '.join(new_additions)}")
            options.extend(new_additions)
            save_options_file(options)
        else:
            await message.channel.send("All the items are already in the wheel.")
    else:
        await message.channel.send(f"Adding '{addition}' to the wheel!")
        options = parse_options_file()
        options.append(addition)
        save_options_file(options)


async def parse_remove(removal: str, message):
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
        await message.channel.send("Please specify an item to remove.")
        return
    options = parse_options_file()
    if removal in options:
        options.remove(removal)
        save_options_file(options)
        await message.channel.send(f"Removed '{removal}' from the wheel!")
    else:
        await message.channel.send(f"'{removal}' is not in the wheel.")


def parse_options_file():
    """
    Parses the 'options.json' file and retrieves the options.

    This function attempts to open and read the 'options.json' file located in the current directory.
    If the file is found and successfully decoded, it returns the list of options contained in the file.
    If the file is not found or there is an error decoding the file, it prints an error message and returns an empty list.

    Returns:
        list: A list of options if the file is successfully read and decoded, otherwise an empty list.
    """
    try:
        with open('options.json', 'r') as file:
            data = json.load(file)
            return data['options']
    except FileNotFoundError:
        print("The options file was not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding the options file.")
        return []


def save_options_file(items):
    """
    Save the updated list of items to the options file in JSON format.

    Args:
        items (list): A list of items to be saved to the options file.

    The function writes the list of items to a file named 'options.json' in the
    current working directory. The items are stored under the key 'options' in
    the JSON file, and the JSON is formatted with an indentation of 4 spaces.
    """
    # This function saves the updated list of items back to the options file.
    # It writes the list to a JSON file.
    with open('options.json', 'w') as file:
        json.dump({"options":items}, file, indent=4)