import asyncio
from telegram import Bot
from telegram.error import BadRequest

async def send_message(token: str, chat_id: str, message_text: str):
    """
    Send a message to a Telegram chat with basic validation
    Args:
        token: Your bot token
        chat_id: Target chat ID (as string)
        message_text: Message content to send
    """
    # Basic validation
    if not message_text.strip():
        raise ValueError("Message cannot be empty")
    if len(message_text) > 4096:
        raise ValueError("Message exceeds Telegram's 4096 character limit")

    bot = Bot(token)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode='MarkdownV2'  # Remove this line if not using Markdown
        )
    except BadRequest as e:
        raise ValueError(f"Invalid message format: {str(e)}") from e

# Example usage
if __name__ == "__main__":
    asyncio.run(send_message(
        token="YOUR_BOT_TOKEN",
        chat_id="TARGET_CHAT_ID",
        message_text="Hello from *Simplified Bot*!"
    ))
