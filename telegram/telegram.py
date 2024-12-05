import requests
import time
import os

def tl_notify(message):
    # Replace YOUR_BOT_TOKEN with the token for your bot
    # Replace YOUR_CHAT_ID with the ID of the chat where you want to send the message
    bot_token = os.environ.get('tgbot')
    chat_id = os.environ.get('tgchat')
    sent = requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}")
    return sent


def tl_notify_group(message):
    # Replace with your bot token (can use environment variable as shown)
    bot_token = os.environ.get('tgbot')
    
    # Group chat ID (replace with the ID from your response or set it in an environment variable)
    group_chat_id = "-4552035259"  # Use your actual group chat ID
    
    # Send a message to the group chat
    response = requests.get(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        params={
            "chat_id": group_chat_id,
            "text": message
        }
    )
    
    if response.status_code != 200:
        print(f"Failed to send message to group chat. Error: {response.text}")
    else:
        print("Message sent to group chat.")

# Example usage
if __name__ == "__main__":
    tl_notify_group("Hello, group! This is a test message from the bot.")