# collector/telegram_collector.py
import logging
from typing import Any

from telethon import TelegramClient
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


class TelegramCollector:
    """Collects messages from Telegram channels using Telethon (userbot)."""

    def __init__(self, config: dict[str, Any], db=None):
        """Initialize collector with config and database.

        Args:
            config: Configuration dictionary containing telegram settings and channels.
            db: Database instance for duplicate detection and error logging.
        """
        self.config = config
        self.db = db
        self.channels = config.get("channels", [])

        telegram_config = config.get("telegram", {})
        self.api_id = telegram_config.get("api_id")
        self.api_hash = telegram_config.get("api_hash")
        self.bot_token = telegram_config.get("bot_token")

        self.client: TelegramClient | None = None

    def _format_channel(self, channel: str) -> str:
        """Format channel name (remove @ if present).

        Args:
            channel: Channel name, optionally prefixed with @.

        Returns:
            Channel name without @ prefix.
        """
        return channel.lstrip("@")

    async def start(self) -> None:
        """Start the Telegram client."""
        self.client = TelegramClient("vacancy_bot", self.api_id, self.api_hash)
        await self.client.start(bot_token=self.bot_token)
        logger.info("Telegram client started")

    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client stopped")

    async def check_channels(self) -> list[dict[str, Any]]:
        """Check all channels for new messages.

        Returns:
            List of message dictionaries from all channels.
        """
        all_messages: list[dict[str, Any]] = []

        for channel in self.channels:
            try:
                messages = await self.get_new_messages(channel)
                all_messages.extend(messages)
            except Exception as e:
                logger.error(f"Error checking channel {channel}: {e}")
                if self.db:
                    self.db.log_error("channel_error", str(e), channel)

        return all_messages

    async def get_new_messages(self, channel: str) -> list[dict[str, Any]]:
        """Get new (unprocessed) messages from a channel.

        Args:
            channel: Channel name to fetch messages from.

        Returns:
            List of new message dictionaries.
        """
        if not self.client:
            await self.start()

        formatted_channel = self._format_channel(channel)
        messages: list[dict[str, Any]] = []

        try:
            # Get last 10 messages
            assert self.client is not None
            async for message in self.client.iter_messages(formatted_channel, limit=10):
                if isinstance(message, Message):
                    # Check if already processed
                    if self.db and self.db.is_message_processed(formatted_channel, message.id):
                        continue

                    # Process message
                    message_data = {
                        "channel": formatted_channel,
                        "id": message.id,
                        "text": message.text or "",
                        "date": message.date,
                        "link": f"https://t.me/{formatted_channel}/{message.id}",
                    }
                    messages.append(message_data)

                    # Mark as processed
                    if self.db:
                        self.db.mark_message_processed(formatted_channel, message.id)

        except Exception as e:
            logger.error(f"Error getting messages from {channel}: {e}")
            if self.db:
                self.db.log_error("message_error", str(e), channel)

        return messages
