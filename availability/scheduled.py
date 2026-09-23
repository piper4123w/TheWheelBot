import asyncio

from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from voting.voting import Vote


# ============================================================
# Configuration
# ============================================================

CHANNEL_ID = 1352336757240369274  # TODO: Change from kylesbottesting channel

# Central Time - automatically handles CST/CDT
CENTRAL = ZoneInfo("America/Chicago")


# ============================================================
# Scheduled Jobs
# ============================================================

async def friday_message_task(bot):
    """
    Sends a message to the configured Discord channel
    every Friday at 9:00 PM Central Time.
    """

    await bot.wait_until_ready()

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print(
            f"[Friday Message] Could not find channel "
            f"{CHANNEL_ID}"
        )
        return

    print("[Friday Message] Scheduler started.")

    while not bot.is_closed():
        now = datetime.now(CENTRAL)

        # Friday = 4
        days_until_friday = (4 - now.weekday()) % 7

        target = datetime.combine(
            now.date() + timedelta(days=days_until_friday),
            time(hour=21, minute=0),
            tzinfo=CENTRAL
        )

        # If it's already Friday at or after 9:00 PM,
        # schedule the next occurrence for the following Friday.
        if target <= now:
            target += timedelta(days=7)

        seconds_until_target = (
            target - now
        ).total_seconds()

        print(
            "[Friday Message] Next message scheduled for "
            f"{target.strftime('%Y-%m-%d %I:%M %p %Z')}"
        )

        await asyncio.sleep(seconds_until_target)

        try:
            await channel.send(
                "🎉 Happy Friday everyone! 🍻"
            )

            print("[Friday Message] Message sent.")

        except Exception as e:
            print(
                f"[Friday Message] Failed to send message: {e}"
            )


async def test_scheduled_message_task(bot):
    """
    Temporary development task.

    Sends a test message 15 seconds after the bot starts.
    """

    await bot.wait_until_ready()

    print("[Test Message] Waiting 15 seconds...")

    await asyncio.sleep(15)

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print(
            f"[Test Message] Could not find channel "
            f"{CHANNEL_ID}"
        )
        return

    try:
        await channel.send(
            "🧪 Test scheduled message!"
        )

        print("[Test Message] Message sent.")

    except Exception as e:
        print(
            f"[Test Message] Failed to send message: {e}"
        )


async def test_scheduled_vote_task(bot):
    """
    Temporary development task.

    Creates a food vote 15 seconds after the bot starts.
    """

    await bot.wait_until_ready()

    print("[Test Vote] Waiting 15 seconds...")

    await asyncio.sleep(15)

    try:
        vote = Vote(
            bot=bot,
            channel_id=CHANNEL_ID,
            title_key="FoodSelectionTest",
            options=[
                "Pizza",
                "Burgers",
                "Tacos",
                "Chinese"
            ]
        )

        await vote.create()

        print(
            "[Test Vote] Vote created successfully."
        )

    except Exception as e:
        print(
            f"[Test Vote] Failed to create vote: {e}"
        )


async def test_count_vote_task(bot):
    """
    Temporary development task.

    Counts the FoodSelectionTest vote 30 seconds after
    the bot starts.

    The vote is located by searching Discord message
    history rather than relying on in-memory state.
    """

    await bot.wait_until_ready()

    print(
        "[Test Vote Count] Waiting 30 seconds..."
    )

    await asyncio.sleep(60)

    try:
        # Reconstruct the vote from its configuration.
        #
        # No reference to the original Vote object is required.
        vote = Vote(
            bot=bot,
            channel_id=CHANNEL_ID,
            title_key="FoodSelectionTest",
            options=[
                "Pizza",
                "Burgers",
                "Tacos",
                "Chinese"
            ]
        )

        vote_counts = await vote.get_vote_counts()
        winners = await vote.count_votes()

        print(
            f"[Test Vote Count] Vote counts: "
            f"{vote_counts}"
        )

        print(
            f"[Test Vote Count] Winners: "
            f"{winners}"
        )

        channel = bot.get_channel(CHANNEL_ID)

        if channel is None:
            print(
                f"[Test Vote Count] Could not find channel "
                f"{CHANNEL_ID}"
            )
            return

        # Format individual vote counts.
        results = "\n".join(
            f"**{option}**: {count}"
            for option, count in vote_counts.items()
        )

        # Format winning result.
        if len(winners) == 0:
            winner_text = (
                "🏆 **No results found.**"
            )
        elif len(winners) == 1:
            winner_text = (
                f"🏆 **Winner: {winners[0]}**"
            )
        else:
            winner_text = (
                "🏆 **Tie:** "
                + ", ".join(winners)
            )

        await channel.send(
            f"📊 **Vote Results**\n\n"
            f"{results}\n\n"
            f"{winner_text}"
        )

        print(
            "[Test Vote Count] Results sent."
        )

    except Exception as e:
        print(
            f"[Test Vote Count] Failed to count vote: {e}"
        )


# ============================================================
# Scheduler Startup
# ============================================================

def start_scheduled_jobs(bot):
    """
    Starts all recurring and development scheduled jobs.
    """

    # Recurring Friday message
    bot.loop.create_task(
        friday_message_task(bot)
    )

    # Temporary development test message
    bot.loop.create_task(
        test_scheduled_message_task(bot)
    )

    # Temporary scheduled vote test
    bot.loop.create_task(
        test_scheduled_vote_task(bot)
    )

    # Temporary scheduled vote count test
    bot.loop.create_task(
        test_count_vote_task(bot)
    )

    print(
        "[Scheduler] Scheduled jobs started."
    )
