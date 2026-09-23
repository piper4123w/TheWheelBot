import asyncio

from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo


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

        # Python weekday():
        # Monday    = 0
        # Tuesday   = 1
        # Wednesday = 2
        # Thursday  = 3
        # Friday    = 4
        # Saturday  = 5
        # Sunday    = 6

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


# ============================================================
# Scheduler Startup
# ============================================================

def start_scheduled_jobs(bot):
    """
    Starts all recurring scheduled jobs.

    Add additional scheduled jobs here as the availability
    module grows.
    """

    bot.loop.create_task(
        friday_message_task(bot)
    )

    # Example future jobs:
    #
    # bot.loop.create_task(
    #     another_scheduled_task(bot)
    # )

    print("[Scheduler] Scheduled jobs started.")
