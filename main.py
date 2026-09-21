# main.py
import asyncio
import os
import signal

import uvicorn
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from collector.telegram_collector import TelegramCollector
from filter.vacancy_filter import VacancyFilter
from notifier.telegram_notifier import TelegramNotifier
from utils.database import Database
from utils.logger import get_logger, setup_logger
from web.app import create_app


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file, with .env overrides.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Parsed configuration dictionary with .env overrides applied.

    Raises:
        FileNotFoundError: If config file does not exist.
        yaml.YAMLError: If config file contains invalid YAML.
    """
    # Load .env file
    load_dotenv()

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Override with .env values if present
    telegram = config.get("telegram", {})
    if os.getenv("TELEGRAM_API_ID"):
        telegram["api_id"] = os.getenv("TELEGRAM_API_ID")
    if os.getenv("TELEGRAM_API_HASH"):
        telegram["api_hash"] = os.getenv("TELEGRAM_API_HASH")
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        telegram["bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN")
    if os.getenv("TARGET_CHANNEL"):
        telegram["target_channel"] = os.getenv("TARGET_CHANNEL")
    config["telegram"] = telegram

    web = config.get("web", {})
    if os.getenv("WEB_USERNAME"):
        web["username"] = os.getenv("WEB_USERNAME")
    if os.getenv("WEB_PASSWORD"):
        web["password"] = os.getenv("WEB_PASSWORD")
    config["web"] = web

    return config


async def check_and_notify(
    collector: TelegramCollector,
    vacancy_filter: VacancyFilter,
    notifier: TelegramNotifier,
    db: Database,
) -> None:
    """Check channels and send notifications for matches.

    Collects messages from all configured channels, applies filters,
    sends notifications for matches, and saves vacancies to database.

    Args:
        collector: Telegram message collector.
        vacancy_filter: Filter engine for matching vacancies.
        notifier: Telegram notification sender.
        db: Database for persistence and duplicate detection.
    """
    logger = get_logger()
    logger.info("Starting channel check...")

    try:
        # Get new messages from all channels
        messages = await collector.check_channels()
        logger.info(f"Found {len(messages)} new messages")

        # Check each message against filters
        for message in messages:
            results = vacancy_filter.check_message(message["text"])

            for result in results:
                # Send notification
                sent = await notifier.send_vacancy(result, message["channel"], message["id"])

                if sent:
                    # Save to database
                    db.add_vacancy(
                        channel_name=message["channel"],
                        message_id=message["id"],
                        category=result.category,
                        matched_phrase=result.matched_phrase,
                        weight=result.weight,
                        text=message["text"],
                        link=message["link"],
                    )
                    logger.info(f"Vacancy sent: {result.category} - {result.matched_phrase}")

    except Exception as e:
        logger.error(f"Error in check_and_notify: {e}")
        db.log_error("check_error", str(e))
        await notifier.send_error(str(e))


async def main() -> None:
    """Main entry point for the Telegram Vacancy Bot.

    Loads configuration, initializes all components, starts the
    APScheduler for periodic checks, and runs the FastAPI web server.
    """
    # Load config
    config = load_config()

    # Setup logging
    log_config = config.get("logging", {})
    setup_logger(
        log_file=log_config.get("file", "logs/bot.log"), level=log_config.get("level", "INFO")
    )
    logger = get_logger()
    logger.info("Starting Telegram Vacancy Bot...")

    # Initialize components
    db = Database()
    collector = TelegramCollector(config, db)
    vacancy_filter = VacancyFilter(config)
    notifier = TelegramNotifier(config)

    # Start Telegram clients
    await collector.start()
    await notifier.start()

    # Health check RSS service
    if not await collector.check_health():
        logger.warning("RSS service is not available. Some channels may not work.")

    # Setup scheduler
    scheduler = AsyncIOScheduler()
    schedule_config = config.get("schedule", {})
    check_interval = schedule_config.get("check_interval_minutes", 15)

    scheduler.add_job(
        check_and_notify,
        trigger=IntervalTrigger(minutes=check_interval),
        args=[collector, vacancy_filter, notifier, db],
        id="check_channels",
        name="Check channels for new vacancies",
    )

    scheduler.start()
    logger.info(f"Scheduler started. Checking every {check_interval} minutes")

    # Run first check immediately
    await check_and_notify(collector, vacancy_filter, notifier, db)

    # Setup web panel
    web_config = config.get("web", {})
    app = create_app(db, config)

    # Start web server
    uvicorn_config = uvicorn.Config(
        app,
        host=web_config.get("host", "0.0.0.0"),
        port=web_config.get("port", 8000),
        log_level="info",
    )
    server = uvicorn.Server(uvicorn_config)

    logger.info(f"Web panel starting on {web_config.get('host')}:{web_config.get('port')}")

    # Graceful shutdown handler
    shutdown_event = asyncio.Event()

    def handle_shutdown(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Run server until shutdown signal
    try:
        server_task = asyncio.create_task(server.serve())
        shutdown_task = asyncio.create_task(shutdown_event.wait())

        # Wait for either server to stop or shutdown signal
        done, pending = await asyncio.wait(
            [server_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=True)

        logger.info("Stopping collector...")
        await collector.stop()

        logger.info("Stopping notifier...")
        await notifier.stop()

        logger.info("Bot stopped gracefully")


if __name__ == "__main__":
    asyncio.run(main())
