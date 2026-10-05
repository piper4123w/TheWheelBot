from dataclasses import dataclass

import discord

ACTIVE_VOTE="ACTIVE VOTE"
COMPLETE_VOTE_EMOJI="✅"

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

    Each active vote message starts with:

        [ACTIVE VOTE - {TITLE_KEY}]

    Example:

        [ACTIVE VOTE - FoodSelectionTest]
    """

    def __init__(
        self,
        messageContent: str
    ):
        

    def __init__(
        self,
        bot: discord.Client,
        channel_id: int,
        title_key: str,
        options: list[str],
        termination_reaction: str = ":)"
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

    def get_vote_header(
        self,
        title_key: str | None = None
    ) -> str:
        """
        Returns the identifying header for this vote.

        If no title key is provided, the Vote object's configured
        title key is used.
        """

        if title_key is None:
            title_key = self.title_key

        return f"[{ACTIVE_VOTE} - {title_key}]"

    async def create(self) -> discord.Message:
        """
        Creates the vote message and adds reactions for every
        available option.

        The returned Message can be passed directly to other
        methods to avoid searching Discord again.
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
        # get_vote_counts() subtracts this baseline.
        for option in self.options:
            emoji = self.letter_to_emoji(option.letter)

            await message.add_reaction(emoji)

        return message

    async def find_active_vote_message(
        self,
        title_key: str | None = None
    ) -> discord.Message | None:
        """
        Searches the channel history for the latest vote message
        with the given vote title key.

        The most recent matching message is returned.

        This is the only method that should need to search Discord
        message history for an existing vote.
        """

        if title_key is None:
            title_key = self.title_key

        channel = self.bot.get_channel(self.channel_id)

        if channel is None:
            raise ValueError(
                f"Could not find channel {self.channel_id}"
            )

        header = self.get_vote_header(title_key)

        # Search newest messages first.
        async for message in channel.history(limit=None):

            # Only consider messages created by this bot.
            if message.author.id != self.bot.user.id:
                continue

            # Check whether the message starts with our vote header.
            if message.content.startswith(header):
                return message

        return None

    def get_vote_counts(
        self,
        message: discord.Message
    ) -> dict[str, int]:
        """
        Counts the reactions on an already-located vote message.

        This method does NOT search Discord.

        The bot's initial reaction is removed from each count.
        """

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

    def count_votes(
        self,
        message: discord.Message
    ) -> list[str]:
        """
        Counts an already-located vote message and returns
        all options tied for the highest vote count.
        """

        vote_counts = self.get_vote_counts(message)

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

    async def complete(
        self,
        title_key: str | None = None
    ) -> list[str]:
        """
        Finds the latest active vote message with the given title key,
        counts the votes, marks the message as completed, and returns
        the winning options.

        Discord history is searched only once.
        """

        if title_key is None:
            title_key = self.title_key

        # Search Discord once.
        message = await self.find_active_vote_message(
            title_key
        )

        if message is None:
            raise ValueError(
                f"Could not find an active vote with title key "
                f"'{title_key}'"
            )

        # Count the already-located message.
        winners = self.count_votes(message)

        # Mark the same message as completed.
        completed_content = message.content.replace(
            self.get_vote_header(title_key),
            "[VOTING COMPLETED!]",
            1
        )

        await message.edit(
            content=completed_content
        )

        return winners
