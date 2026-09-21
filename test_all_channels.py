# test_all_channels.py — send 1 test vacancy from each channel
import asyncio
import io
import sys

import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from collector.telegram_collector import TelegramCollector  # noqa: E402
from notifier.telegram_notifier import TelegramNotifier  # noqa: E402


async def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    collector = TelegramCollector(config)
    notifier = TelegramNotifier(config)
    await collector.start()
    await notifier.start()

    channels = config["channels"]
    print(f"Channels: {len(channels)}\n")

    for ch in channels:
        ch_clean = ch.lstrip("@").split("/")[0]
        print(f"=== {ch} ===")

        msgs = await collector.get_new_messages(ch)
        if not msgs:
            print("  No messages from RSS\n")
            continue

        m = msgs[0]
        text_short = m["text"][:100].replace("\n", " ")
        print(f"  [{m['id']}] {text_short}")

        # Send as test message with channel prefix
        test_text = f"TEST from {ch_clean}:\nMsg #{m['id']}\n{m['text'][:500]}\n\nLink: {m['link']}"

        import httpx

        r = httpx.post(
            f"https://api.telegram.org/bot{notifier.bot_token}/sendMessage",
            json={
                "chat_id": config["telegram"]["target_channel"],
                "text": test_text,
            },
            timeout=15,
        )
        status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
        print(f"  Sent: {status}\n")

    await collector.stop()
    await notifier.stop()


if __name__ == "__main__":
    asyncio.run(main())
