# main.py
import asyncio

import uvicorn
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from collector.telegram_collector import TelegramCollector
from filter.vacancy_filter import VacancyFilter
from notifier.telegram_notifier import TelegramNotifier
from utils.database import Database
from utils.logger import get_logger, setup_logger
from web.app import create_app


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If config file does not exist.
        yaml.YAMLError: If config file contains invalid YAML.
    """
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


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

    # Run forever
    try:
        await server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()
        await collector.stop()
        await notifier.stop()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
