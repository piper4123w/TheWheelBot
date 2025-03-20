import json
import random


MODULE_COMMAND="$wheel"


async def handle_message(message):
    print('handling wheel command')
    if message.content.startswith(f"{MODULE_COMMAND} add"):
        remainder = message.content[len("$wheel add "):].strip()
        # You can now use item_to_add for further processing
        await parse_add(remainder, message)
    elif "remove" in message.content:
        await message.channel.send("COMING SOON - Removing an item from the wheel!")
    elif message.content.startswith(f"{MODULE_COMMAND} spin"):
        await spin_wheel(message)
    elif "help" in message.content:
        await message.channel.send("$wheel - command for spinning the wheel of fate\nCommands: 'add', 'remove', 'spin', 'help'")
    else:
        await message.channel.send("Unknown command. Please use 'add', 'remove', 'spin', or 'help'.")


async def spin_wheel(message):
    await message.channel.send("Spinning the wheel...")
    options = parse_options_file()
    if not options:
        await message.channel.send("The wheel is empty! Please add items first.")
        return
    result = random.choice(options)
    await message.channel.send(f"...and the result is: {result}")


async def parse_add(addition: str, message):
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


def parse_options_file():
    # This function parses the options file to get the list of items for the wheel.
    # It reads from a file and returns a list of items.
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
    # This function saves the updated list of items back to the options file.
    # It writes the list to a JSON file.
    with open('options.json', 'w') as file:
        json.dump({"options":items}, file, indent=4)