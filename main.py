import telethon
from telethon.tl.custom import Button
from telethon import TelegramClient
from decouple import config
import aiohttp
import re, os

if not config("BOT_TOKEN"):
    print("Please provide your bot token on BOT_TOKEN environment variable or add in .env file")
    os._exit(1)

client = TelegramClient("bot", 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e")
client.start(bot_token=os.getenv("BOT_TOKEN"))
print("Bot started")

@client.on(telethon.events.NewMessage(pattern="^/start"))
async def start(event):
    await event.reply("Merhaba, verilen sorgudan sohbetleri ve kanalları aramak için bir botum\nAramak Icin /search aranacak kelimeyi yazın.\nOrnek : /search pdf", buttons=[Button.url("Sahip", "https://t.me/kamileecher"), Button.url("Channel", "https://t.me/kamileecherch")])

@client.on(telethon.events.NewMessage(pattern="^/search"))
async def search(event):
    msg = await event.respond("Aranıyor...")
    async with aiohttp.ClientSession() as session:
        start = 1
        async with session.get(f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={event.text.split()[1]}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}", headers={"x-referer": "https://explorer.apis.google.com"}) as r:
            response = await r.json()
            result = ""
            
            if not response.get("items"):
                return await msg.edit("Sonuç Yok!")
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r'\/\d', item["link"]):
                    link = re.sub(r'\/\d', "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    # remove duplicates
                    continue
                result += f"{title}\n{link}\n\n"
            prev_and_next_btns = [Button.inline("▶️ Ileri", data=f"next {start+10} {event.text.split()[1]}")]
            await msg.edit(result, link_preview=False, buttons=prev_and_next_btns)
            await session.close()

@client.on(telethon.events.CallbackQuery(data=re.compile(r"prev (.*) (.*)")))
async def prev(event):
    start = int(event.data.split()[1])
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={(event.data.split()[2]).decode('utf-8')}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}", headers={"x-referer": "https://explorer.apis.google.com"}) as r:
            response = await r.json()
            if response.get("error"):
                return await event.answer("Başka Sonuç Yok!")
            result = ""            
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r'\/\d', item["link"]):
                    link = re.sub(r'\/\d', "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    # remove duplicates
                    continue
                result += f"{title}\n{link}\n\n"
            prev_and_next_btns = [Button.inline("◀️ Geri", data=f"prev {start-10} {event.data.split()[2].decode('utf-8')}"), Button.inline("▶️ Ileri", data=f"next {start+10} {event.data.split()[2].decode('utf-8')}")]
            await event.edit(result, link_preview=False, buttons=prev_and_next_btns)
            await session.close()

@client.on(telethon.events.CallbackQuery(data=re.compile(r"next (.*) (.*)")))
async def next(event):
    start = int(event.data.split()[1])
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={(event.data.split()[2]).decode('utf-8')}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}", headers={"x-referer": "https://explorer.apis.google.com"}) as r:
            response = await r.json()
            print(response["searchInformation"]["totalResults"])
            if response["searchInformation"]["totalResults"] == "0":
                return await event.answer("Başka Sonuç Yok!")
            result = ""
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r'\/\d', item["link"]):
                    link = re.sub(r'\/\d', "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    # remove duplicates
                    continue
                result += f"{title}\n{link}\n\n"
            prev_and_next_btns = [Button.inline("◀️ Geri", data=f"prev {start-10} {(event.data.split()[2]).decode('utf-8')}"), Button.inline("▶️ Ileri", data=f"next {start+10} {(event.data.split()[2]).decode('utf-8')}")]
            await event.edit(result, link_preview=False, buttons=prev_and_next_btns)
            await session.close()

client.run_until_disconnected()
