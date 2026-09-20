# notifier/telegram_notifier.py
import logging
from typing import Dict, Any, Optional
from telethon import TelegramClient
from filter.vacancy_filter import FilterResult

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, config: Dict[str, Any]):
        """Initialize notifier with config."""
        self.config = config
        telegram_config = config.get("telegram", {})
        self.bot_token = telegram_config.get("bot_token")
        self.target_channel = telegram_config.get("target_channel", "").lstrip("@")
        self.client: Optional[TelegramClient] = None

    async def start(self) -> None:
        """Start the Telegram client."""
        api_id = self.config["telegram"]["api_id"]
        api_hash = self.config["telegram"]["api_hash"]
        self.client = TelegramClient('notifier_bot', api_id, api_hash)
        await self.client.start(bot_token=self.bot_token)
        logger.info("Notifier client started")

    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Notifier client stopped")

    def format_message(self, vacancy: FilterResult, channel: str = None, message_id: int = None) -> str:
        """Format vacancy as message."""
        link = f"https://t.me/{channel}/{message_id}" if channel and message_id else "N/A"

        message = f"""🔍 Найдена вакансия!

📁 Категория: {vacancy.category}
🔑 Фраза: {vacancy.matched_phrase}
📡 Канал: {channel or 'N/A'}
📅 Дата: {vacancy.original_text[:50]}...
🔗 Ссылка: {link}

---
{vacancy.original_text}"""

        return message

    async def send_vacancy(self, vacancy: FilterResult, channel: str = None, message_id: int = None) -> bool:
        """Send vacancy notification to target channel."""
        if not self.client:
            await self.start()

        try:
            message = self.format_message(vacancy, channel, message_id)
            await self.client.send_message(self.target_channel, message)
            logger.info(f"Vacancy sent to {self.target_channel}")
            return True
        except Exception as e:
            logger.error(f"Error sending vacancy: {e}")
            return False

    async def send_error(self, error: str) -> bool:
        """Send error notification."""
        if not self.client:
            await self.start()

        try:
            message = f"❌ Ошибка бота:\n\n{error}"
            await self.client.send_message(self.target_channel, message)
            return True
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
