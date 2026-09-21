# notifier/telegram_notifier.py
import asyncio
import logging
from typing import Any

import httpx

from filter.vacancy_filter import FilterResult

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds


class TelegramNotifier:
    def __init__(self, config: dict[str, Any]):
        """Initialize notifier with config."""
        self.config = config
        telegram_config = config.get("telegram", {})
        self.bot_token = telegram_config.get("bot_token")
        self.target_channel = telegram_config.get("target_channel", "").lstrip("@")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"

    async def start(self) -> None:
        """No-op: Bot API doesn't need persistent connection."""
        logger.info("Notifier started (Bot API mode)")

    async def stop(self) -> None:
        """No-op."""
        logger.info("Notifier stopped")

    def format_message(
        self, vacancy: FilterResult, channel: str = None, message_id: int = None
    ) -> str:
        """Format vacancy as message."""
        link = f"https://t.me/{channel}/{message_id}" if channel and message_id else "N/A"

        message = f"""🔍 Найдена вакансия!

📁 Категория: {vacancy.category}
🔑 Фраза: {vacancy.matched_phrase}
📡 Канал: {channel or 'N/A'}
🔗 Ссылка: {link}

---
{vacancy.original_text}"""

        return message

    async def _send_with_retry(self, payload: dict, description: str = "message") -> dict | None:
        """Send via Bot API with exponential backoff retry."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(f"{self.api_base}/sendMessage", json=payload)
                    data = response.json()

                    if response.status_code == 200 and data.get("ok"):
                        return data
                    elif response.status_code == 429:
                        # Rate limited - wait longer
                        retry_after = data.get("parameters", {}).get("retry_after", 30)
                        logger.warning(f"Rate limited. Waiting {retry_after}s...")
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        last_error = f"HTTP {response.status_code}: {data}"
                        logger.warning(
                            f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {description}: {last_error}"
                        )

            except httpx.RequestError as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {description}: {e}")

            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2**attempt)
                await asyncio.sleep(delay)

        logger.error(f"All {MAX_RETRIES} attempts failed for {description}: {last_error}")
        return None

    async def send_vacancy(
        self, vacancy: FilterResult, channel: str = None, message_id: int = None
    ) -> bool:
        """Send vacancy notification to target channel via Bot API."""
        text = self.format_message(vacancy, channel, message_id)

        payload = {
            "chat_id": f"@{self.target_channel}",
            "text": text,
            "parse_mode": "HTML",
        }

        data = await self._send_with_retry(payload, f"vacancy/{vacancy.category}")

        if data:
            tg_message_id = data.get("result", {}).get("message_id")
            logger.info(
                f"Vacancy sent to @{self.target_channel} "
                f"[message_id={tg_message_id}, category={vacancy.category}, "
                f"channel={channel}/{message_id}]"
            )
            return True
        return False

    async def send_error(self, error: str) -> bool:
        """Send error notification."""
        payload = {
            "chat_id": f"@{self.target_channel}",
            "text": f"❌ Ошибка бота:\n\n{error}",
        }

        data = await self._send_with_retry(payload, "error_notification")
        return data is not None
