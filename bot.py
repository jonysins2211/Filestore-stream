
# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
import pytz
from datetime import datetime
#rohit_1888 on Tg
from config import *
from database.db_premium import *
from database.database import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

# Suppress APScheduler logs below WARNING level
logging.getLogger("apscheduler").setLevel(logging.WARNING)

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(remove_expired_users, "interval", seconds=10)

# Reset verify count for all users daily at 00:00 IST
async def daily_reset_task():
    try:
        await db.reset_all_verify_counts()
    except Exception:
        pass  

scheduler.add_job(daily_reset_task, "cron", hour=0, minute=0)

# ── Premium expiry notifications ──────────────────────────────────────────
# Runs daily at 10:00 AM IST
# Notifies user 1 day before expiry and on expiry day
async def premium_expiry_notify_task():
    """Check all premium users and notify them 1 day before and on expiry day."""
    try:
        from pytz import timezone as pytz_tz
        from datetime import datetime, timedelta
        ist = pytz_tz("Asia/Kolkata")
        now = datetime.now(ist)
        
        async for user in collection.find({}):
            user_id = user.get("user_id")
            expiry_str = user.get("expiration_timestamp")
            if not user_id or not expiry_str:
                continue
            try:
                expiry_dt = datetime.fromisoformat(expiry_str).astimezone(ist)
                delta = expiry_dt - now
                days_left = delta.days
                hours_left = delta.seconds // 3600

                # 1 day before expiry (between 20-24 hours remaining)
                if days_left == 0 and 20 <= hours_left <= 24:
                    try:
                        bot_instance = Bot._running_instance if hasattr(Bot, '_running_instance') else None
                        if bot_instance:
                            await bot_instance.send_message(
                                user_id,
                                f"⚠️ <b>Premium Expiring Soon!</b>\n\n"
                                f"Your premium access will expire in <b>~{hours_left} hours</b>.\n\n"
                                f"📅 Expiry: <code>{expiry_dt.strftime('%d %b %Y %H:%M IST')}</code>\n\n"
                                f"🔄 Renew now to keep uninterrupted access!\n"
                                f"Contact: @{OWNER_TAG}"
                            )
                    except Exception as e:
                        print(f"Premium 1-day notify error for {user_id}: {e}")

                # On expiry day (expired in last 1 hour)
                elif -1 <= delta.total_seconds() / 3600 <= 0:
                    try:
                        bot_instance = Bot._running_instance if hasattr(Bot, '_running_instance') else None
                        if bot_instance:
                            await bot_instance.send_message(
                                user_id,
                                f"❌ <b>Premium Expired!</b>\n\n"
                                f"Your premium access has expired.\n\n"
                                f"📅 Expired on: <code>{expiry_dt.strftime('%d %b %Y %H:%M IST')}</code>\n\n"
                                f"🔄 Contact @{OWNER_TAG} to renew your premium access."
                            )
                        # Remove expired user from DB
                        await collection.delete_one({"user_id": user_id})
                    except Exception as e:
                        print(f"Premium expiry notify error for {user_id}: {e}")

            except Exception as e:
                print(f"Premium expiry check error for {user_id}: {e}")
    except Exception as e:
        print(f"premium_expiry_notify_task error: {e}")

scheduler.add_job(premium_expiry_notify_task, "interval", hours=1)
#scheduler.start()


name ="""
 BY CODEFLIX BOTS
"""

def get_indian_time():
    """Returns the current time in IST."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        Bot._running_instance = self  # Store for scheduler access
        scheduler.start()
        usr_bot_me = await self.get_me()
        self.uptime = get_indian_time()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/weebs_support")
        self.LOGGER(__name__).info(f"""       


  ___ ___  ___  ___ ___ _    _____  _____  ___ _____ ___ 
 / __/ _ \|   \| __| __| |  |_ _\ \/ / _ )/ _ \_   _/ __|
| (_| (_) | |) | _|| _|| |__ | | >  <| _ \ (_) || | \__ \
 \___\___/|___/|___|_| |____|___/_/\_\___/\___/ |_| |___/
                                                         
 
                                          """)

        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username
        self.LOGGER(__name__).info(f"Bot Running..! Made by @Codeflix_Bots")   

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()


        try: await self.send_message(OWNER_ID, text = f"<b><blockquote> Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @Codeflix_Bots</blockquote></b>")
        except: pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @rohit_1888")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())

#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.