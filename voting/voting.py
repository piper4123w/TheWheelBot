from dataclasses import dataclass
from typing import Optional

import discord


@dataclass
class VoteOption:
    """
    Represents one option in a vote.
    """

    letter: str
    value: str


class Vote:
    """
    Represents a multiple-selection Discord reaction vote.

    Votes are stateless. The Discord message itself contains
    everything needed to identify and count the vote.

    Each vote message starts with:

        [ACTIVE VOTE - {TITLE_KEY}]

    Example:

        [ACTIVE VOTE - FoodSelectionTest]
    """

    def __init__(
        self,
        bot: discord.Client,
        channel_id: int,
        title_key: str,
        options: list[str]
    ):
        if len(options) > 26:
            raise ValueError(
                "A vote can have a maximum of 26 options."
            )

        if len(options) == 0:
            raise ValueError(
                "A vote must contain at least one option."
            )

        if not title_key:
            raise ValueError(
                "A vote must have a title key."
            )

        self.bot = bot
        self.channel_id = channel_id
        self.title_key = title_key

        self.options = [
            VoteOption(
                letter=chr(ord('A') + index),
                value=value
            )
            for index, value in enumerate(options)
        ]

        # The message is intentionally NOT stored.
        #
        # This keeps the vote stateless. The Discord message
        # itself is the source of truth.
        self.message: Optional[discord.Message] = None

    @staticmethod
    def letter_to_emoji(letter: str) -> str:
        """
        Converts a letter into a Discord regional indicator emoji.

        A -> 🇦
        B -> 🇧
        C -> 🇨
        etc.
        """

        letter = letter.upper()

        if len(letter) != 1 or not 'A' <= letter <= 'Z':
            raise ValueError(
                f"Invalid letter: {letter}"
            )

        return chr(
            ord('🇦') + ord(letter) - ord('A')
        )

    def get_vote_header(self) -> str:
        """
        Returns the identifying header for this vote.
        """

        return f"[ACTIVE VOTE - {self.title_key}]"

    async def create(self) -> discord.Message:
        """
        Creates the vote message and adds reactions for every
        available option.
        """

        channel = self.bot.get_channel(self.channel_id)

        if channel is None:
            raise ValueError(
                f"Could not find channel {self.channel_id}"
            )

        message_lines = [
            self.get_vote_header(),
            "",
            "🗳️ **Vote! Select all that apply:**",
            ""
        ]

        for option in self.options:
            emoji = self.letter_to_emoji(option.letter)

            message_lines.append(
                f"{emoji} {option.value}"
            )

        message = await channel.send(
            "\n".join(message_lines)
        )

        # Add one reaction for every option.
        #
        # These reactions establish the baseline count of 1.
        # count_votes() subtracts this baseline.
        for option in self.options:
            emoji = self.letter_to_emoji(option.letter)

            await message.add_reaction(emoji)

        return message

    async def find_active_vote_message(
        self
    ) -> Optional[discord.Message]:
        """
        Searches the channel history for the latest vote message
        created by this bot matching this vote's title key.

        The most recent matching message is returned.
        """

        channel = self.bot.get_channel(self.channel_id)

        if channel is None:
            raise ValueError(
                f"Could not find channel {self.channel_id}"
            )

        header = self.get_vote_header()

        # Search newest messages first.
        async for message in channel.history(
            limit=None
        ):
            # Only consider messages created by this bot.
            if message.author.id != self.bot.user.id:
                continue

            # Check whether the message starts with our vote header.
            if message.content.startswith(header):
                return message

        return None

    async def get_vote_counts(
        self
    ) -> dict[str, int]:
        """
        Finds the latest matching vote message and returns
        the vote count for every option.

        The bot's initial reaction is removed from each count.
        """

        message = await self.find_active_vote_message()

        if message is None:
            raise ValueError(
                f"Could not find an active vote with title key "
                f"'{self.title_key}'"
            )

        vote_counts = {}

        for option in self.options:
            emoji = self.letter_to_emoji(option.letter)

            count = 0

            for reaction in message.reactions:
                if str(reaction.emoji) == emoji:
                    # Subtract the bot's initial reaction.
                    count = max(0, reaction.count - 1)
                    break

            vote_counts[option.value] = count

        return vote_counts

    async def count_votes(self) -> list[str]:
        """
        Finds the latest matching vote message and returns
        all options tied for the highest vote count.
        """

        vote_counts = await self.get_vote_counts()

        if not vote_counts:
            return []

        highest_vote_count = max(
            vote_counts.values()
        )

        winners = [
            option
            for option, count in vote_counts.items()
            if count == highest_vote_count
        ]

        return winners
