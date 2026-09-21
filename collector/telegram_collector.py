# collector/telegram_collector.py
import asyncio
import logging
import re
import xml.etree.ElementTree as ET
from html import unescape
from typing import Any

import httpx

logger = logging.getLogger(__name__)

RSS_BASE_URL = "https://tg-channel-to-rss.vercel.app/api/rss"

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds


class TelegramCollector:
    """Collects messages from public Telegram channels via RSS feed."""

    def __init__(self, config: dict[str, Any], db=None):
        """Initialize collector with config and database."""
        self.config = config
        self.db = db
        self.channels = config.get("channels", [])
        self._consecutive_failures: dict[str, int] = {}  # channel -> failure count

    def _format_channel(self, channel: str) -> str:
        """Format channel name (remove @ if present)."""
        return channel.lstrip("@")

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and decode entities."""
        text = unescape(text)
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()

    async def start(self) -> None:
        """No-op: RSS doesn't need startup."""
        logger.info("Collector started (RSS mode)")

    async def stop(self) -> None:
        """No-op: RSS doesn't need shutdown."""
        logger.info("Collector stopped (RSS mode)")

    async def check_health(self) -> bool:
        """Check if RSS service is available."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{RSS_BASE_URL}/test")
                if response.status_code < 500:
                    logger.info("RSS service is available")
                    self._consecutive_failures.clear()
                    return True
                logger.warning(f"RSS service returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"RSS service health check failed: {e}")
            return False

    async def _fetch_with_retry(self, rss_url: str, channel: str) -> str | None:
        """Fetch RSS feed with exponential backoff retry."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(
                    timeout=30, follow_redirects=True, headers={"User-Agent": "VacancyBot/1.0"}
                ) as client:
                    response = await client.get(rss_url)
                    response.raise_for_status()
                    return response.text

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_error = e
                delay = RETRY_BASE_DELAY * (2**attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {channel}: {e}. "
                    f"Retrying in {delay}s..."
                )
                if self.db:
                    self.db.log_error("retry_attempt", f"Attempt {attempt + 1}: {e}", channel)
                await asyncio.sleep(delay)

        # All retries exhausted
        logger.error(f"All {MAX_RETRIES} attempts failed for {channel}: {last_error}")
        if self.db:
            self.db.log_error("fetch_error", f"All retries exhausted: {last_error}", channel)
        return None

    async def check_channels(self) -> list[dict[str, Any]]:
        """Check all channels for new messages."""
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
        """Get new (unprocessed) messages from a channel via RSS."""
        formatted_channel = self._format_channel(channel)
        messages: list[dict[str, Any]] = []

        rss_url = f"{RSS_BASE_URL}/{formatted_channel}"

        # Fetch with retry
        response_text = await self._fetch_with_retry(rss_url, formatted_channel)
        if response_text is None:
            self._consecutive_failures[formatted_channel] = (
                self._consecutive_failures.get(formatted_channel, 0) + 1
            )
            if self._consecutive_failures[formatted_channel] >= 3:
                logger.critical(
                    f"Channel {formatted_channel} failed {self._consecutive_failures[formatted_channel]} "
                    f"consecutive times. Check RSS service status."
                )
            return messages

        try:
            root = ET.fromstring(response_text)
            items = root.findall(".//item")

            for item in items[-10:]:  # Last 10 items
                guid_el = item.find("guid")
                if guid_el is None or not guid_el.text:
                    continue

                try:
                    message_id = int(guid_el.text.strip())
                except ValueError:
                    continue

                if self.db and self.db.is_message_processed(formatted_channel, message_id):
                    continue

                desc_el = item.find("description")
                text = ""
                if desc_el is not None and desc_el.text:
                    text = self._clean_html(desc_el.text)

                title_el = item.find("title")
                if not text and title_el is not None and title_el.text:
                    text = self._clean_html(title_el.text)

                date_str = ""
                pub_date = item.find("pubDate")
                if pub_date is not None and pub_date.text:
                    date_str = pub_date.text.strip()

                link_el = item.find("link")
                link = f"https://t.me/{formatted_channel}/{message_id}"
                if link_el is not None and link_el.text:
                    link = link_el.text.strip()

                message_data = {
                    "channel": formatted_channel,
                    "id": message_id,
                    "text": text,
                    "date": date_str,
                    "link": link,
                }
                messages.append(message_data)

                if self.db:
                    self.db.mark_message_processed(formatted_channel, message_id)

            # Reset failure count on success
            self._consecutive_failures[formatted_channel] = 0
            logger.info(f"Fetched {len(messages)} new messages from {formatted_channel}")

        except ET.ParseError as e:
            logger.error(f"RSS parse error for {formatted_channel}: {e}")
            if self.db:
                self.db.log_error("parse_error", str(e), formatted_channel)

        return messages
