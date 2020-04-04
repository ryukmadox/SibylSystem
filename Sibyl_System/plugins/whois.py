from telethon.tl.functions.users import GetFullUserRequest
from Sibyl_System import Sibyl_logs, ENFORCERS, ACCEPTORS, Sibyl_approved_logs
from Sibyl_System.strings import scan_request_string, scan_approved_string
from Sibyl_System import Sibyl
from telethon import events
import asyncio

@Sibyl.on(events.NewMessage(pattern=r'[\.\?!]whois'))
async def whois(event):
 if event.from_id in ACCEPTORS:
  try:
   to_get = event.pattern_match.group(1)
  except:
    if event.reply:
         replied = await event.get_reply_message()
         to_get = int(replied.sender.id)
    else:
         return
  try: to_get = int(to_get) 
  except: pass 
  data = Sibyl(GetFullUserRequest(to_get))
  await Sibyl.send_message(event.chat_id, f"Name: `{data.user.first_name}`\nUser ID: `{data.user.id}`\nAbout: {data.user.about}")