from datetime import time
from zoneinfo import ZoneInfo

from voting.voting import Vote
from availability.scheduled_trigger import ScheduledTrigger

# ============================================================

# Configuration

# ============================================================

CHANNEL_ID = 1352333984067092644  # TODO: manually set to general for now, probably should come from the json OR the wheel data channel

# Central Time - automatically handles CST/CDT

CENTRAL = ZoneInfo("America/Chicago")

HH_Day_Selection_TitleKey = "HH Day Selection"

# ============================================================

# Scheduled Jobs

# ============================================================

async def send_day_selection_vote(bot):
    """
    Creates a HH Day Selection vote every Friday night
    at 9:00 PM Central Time.
    """

    await bot.wait_until_ready()

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print(
            f"[{HH_Day_Selection_TitleKey}-StartVote] "
            f"Could not find channel {CHANNEL_ID}"
        )
        return

    print(
        f"[{HH_Day_Selection_TitleKey}-StartVote] "
        "Scheduler started."
    )

    while not bot.is_closed():

        trigger = ScheduledTrigger(
            day=4,  # Friday
            time=time(hour=21),
            timezone=CENTRAL
        )

        # Pause until the next Friday at 9:00 PM.
        await trigger.async_awaitTrigger()

        try:
            vote = Vote(
                bot=bot,
                channel_id=CHANNEL_ID,
                title_key=HH_Day_Selection_TitleKey,
                options=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                ]
            )

            await vote.create()

            print(
                f"[{HH_Day_Selection_TitleKey}-StartVote] "
                "Vote created successfully."
            )

        except Exception as e:
            print(
                f"[{HH_Day_Selection_TitleKey}-StartVote] "
                f"Failed to create vote: {e}"
            )

async def count_day_selection_vote_task(bot):
    """
    Counts the HH Day Selection vote every Sunday at 9:00 PM
    Central Time.

    The vote is located by searching Discord message history
    rather than relying on in-memory state.
    """

    await bot.wait_until_ready()

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print(
            f"[{HH_Day_Selection_TitleKey}-EndVote] "
            f"Could not find channel {CHANNEL_ID}"
        )
        return

    print(
        f"[{HH_Day_Selection_TitleKey}-EndVote] "
        "Scheduler started."
    )

    while not bot.is_closed():

        trigger = ScheduledTrigger(
            day=6,  # Sunday
            time=time(hour=21, minute=0),
            timezone=CENTRAL
        )

        # Pause until the next Sunday at 9:00 PM.
        await trigger.async_awaitTrigger()

        try:
            # Reconstruct the vote configuration.
            #
            # No reference to the original Vote object is required.
            vote = Vote(
                bot=bot,
                channel_id=CHANNEL_ID,
                title_key=HH_Day_Selection_TitleKey,
                options=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                ]
            )

            # Find, count, and complete the vote.
            winners = await vote.complete(
                HH_Day_Selection_TitleKey
            )

            # Format winning result.
            if len(winners) == 0:
                winner_text = (
                    "😢 **No one voted :(**"
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
                f"📊 **{HH_Day_Selection_TitleKey} - Vote Results**\n\n"
                f"{winner_text}"
            )

            print(
                f"[{HH_Day_Selection_TitleKey}-EndVote] "
                f"Vote completed. Winners: {winners}"
            )

        except Exception as e:
            print(
                f"[{HH_Day_Selection_TitleKey}-EndVote] "
                f"Failed to count vote: {e}"
            )

# ============================================================

# Scheduler Startup

# ============================================================

def start_scheduled_jobs(bot):
    """
    Starts all recurring scheduled jobs.
    """

    bot.loop.create_task(
        send_day_selection_vote(bot)
    )

    bot.loop.create_task(
        count_day_selection_vote_task(bot)
    )

    print(
        "[Scheduler] Scheduled jobs started."
    )