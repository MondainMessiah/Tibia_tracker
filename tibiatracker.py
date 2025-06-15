import os
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CHARACTERS = [
    "Ilumine",
    "Jay the pally",
    "Zanron the monk",
    "Hex good",
    "kamikadzei"
]

def fetch_character(name):
    url = f"https://api.tibiadata.com/v1/characters/{name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def extract_relevant_info(data):
    char_data = data.get("characters", {}).get("data", {})
    if not char_data:
        return None
    info = {
        "level": char_data.get("level"),
        "world": char_data.get("world"),
        "vocation": char_data.get("vocation"),
        "online": char_data.get("status") == "online",
        "last_login": char_data.get("last_login"),
        "married_to": char_data.get("married_to") or "None",
        "guild": char_data.get("guild_name") or "None"
    }
    return info

def send_daily_summary():
    print(f"Running daily summary at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} GMT")
    
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(title="Daily Tibia Characters Update", color='03b2f8')
    embed.set_footer(text="Tibia Character Tracker")

    medal_emojis = ["🥇", "🥈", "🥉"]
    description_lines = []

    for idx, char in enumerate(CHARACTERS):
        data = fetch_character(char)
        if not data:
            description_lines.append(f"**{char}**: Failed to fetch data.")
            continue

        info = extract_relevant_info(data)
        if not info:
            description_lines.append(f"**{char}**: No data available.")
            continue

        status = "Online" if info["online"] else "Offline"

        medal = medal_emojis[idx] if idx < 3 else ""

        line = (
            f"{medal} **{char}**\n"
            f"Level: {info['level']}\n"
            f"World: {info['world']}\n"
            f"Vocation: {info['vocation']}\n"
            f"Status: {status}\n"
            f"Last Login: {info['last_login']}\n"
            f"Married To: {info['married_to']}\n"
            f"Guild: {info['guild']}\n"
        )
        description_lines.append(line)

    embed.description = "\n\n".join(description_lines)
    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code in (200, 204):
        print("Daily summary posted successfully.")
    else:
        print(f"Failed to post summary: {response.status_code}")

if __name__ == "__main__":
    send_daily_summary()
