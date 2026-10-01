import asyncio

from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

class ScheduledTrigger:
    """
    Represents a recurring weekly day/time trigger.

    The trigger waits until the next occurrence of the configured
    day and time.

    Days use Python's weekday numbering:

        Monday    = 0
        Tuesday   = 1
        Wednesday = 2
        Thursday  = 3
        Friday    = 4
        Saturday  = 5
        Sunday    = 6

    Example:

        #Friday at 9PM Central Time
        trigger = ScheduledTrigger(
            day=4,
            time=time(hour=21, minute=0),
            timezone=ZoneInfo("America/Chicago")
        )

        await trigger.async_awaitTrigger()
    """

    def __init__(
        self,
        day: int,
        time: time,
        timezone: ZoneInfo
    ):
        if not 0 <= day <= 6:
            raise ValueError(
                "Day must be between 0 (Monday) and 6 (Sunday)."
            )

        self.day = day
        self.time = time
        self.timezone = timezone

    def get_next_occurrence(self) -> datetime:
        """
        Calculates the next occurrence of the configured day/time.

        If the configured time is later today, today's occurrence
        is returned.

        If the configured time has already passed today, the next
        occurrence will be in the following week.
        """

        now = datetime.now(self.timezone)

        days_until_trigger = (
            self.day - now.weekday()
        ) % 7

        target_date = (
            now.date()
            + timedelta(days=days_until_trigger)
        )

        target = datetime.combine(
            target_date,
            self.time,
            tzinfo=self.timezone
        )

        # If the trigger is today but the time has already passed,
        # schedule it for the following week.
        if target <= now:
            target += timedelta(days=7)

        return target

    def get_seconds_until_trigger(self) -> float:
        """
        Returns the number of seconds until the next occurrence.
        """

        now = datetime.now(self.timezone)
        target = self.get_next_occurrence()

        return (
            target - now
        ).total_seconds()

    async def async_awaitTrigger(self):
        """
        Asynchronously waits until the next occurrence
        of the configured day/time.

        This method returns once the trigger time has been reached.
        """

        target = self.get_next_occurrence()
        seconds_until_trigger = (
            target - datetime.now(self.timezone)
        ).total_seconds()

        await asyncio.sleep(
            max(0, seconds_until_trigger)
        )
