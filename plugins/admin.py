import os
import time
import math
import json
import string
import random
import traceback
import asyncio
import datetime
import motor.motor_asyncio
import aiofiles
from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserNotParticipant, UserBannedInChannel
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid


class Database:
    
    def __init__(
	self,
	url=os.environ.get("DATABASE_URI"),
	database_name="nysdb"
    ):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.cache = {}
    
    def new_user(self, id):
        return {
            "id": id,
            "domains": {
                "gplinks.in": True,
                "bit.ly": True,
                "chilp.it": True,
                "click.ru": True,
                "cutt.ly": True,
                "da.gd": True,
                "git.io": True,
                "is.gd": True,
                "osdb.link": True,
                "ow.ly": True,
                "po.st": True,
                "qps.ru": True,
                "short.cm": True,
                "tinyurl.com": True,
                "0x0.st": True,
                "ttm.sh": True
            }
        }
    
    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)
    
    async def get_user(self, id):
        user = self.cache.get(id)
        if user is not None:
            return user
        
        user = await self.col.find_one({"id": int(id)})
        self.cache[id] = user
        return user
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})
    
    async def allow_domain(self, id, domain):
        user = await self.get_user(id)
        return user["domains"].get(domain, False)
    
    async def update_domain(self, id, domain, bool):
        user = await self.get_user(id)
        domains = user["domains"]
        self.cache[id]["domains"][domain] = bool 
        domains[domain] = bool
        await self.col.update_one(
            {"id": id},
            {"$set": {"domains": domains}}
        )


BOT_OWNER = int(os.environ.get("BOT_OWNER"))
db = Database()


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


@Client.on_message(filters.private & filters.command("broadcast") & filters.user(Config.BOT_OWNER))
async def broadcast_dis(_, message: Message):
    bc_msg = await message.reply("`Processing ⚙️...`")
    r_msg = message.reply_to_message
    if not r_msg:
        return await bc_msg.edit("`Reply to a message to broadcast!`")
    users_list = await get_users_list()
    # trying to broadcast
    await bc_msg.edit("`Broadcasting has started, This may take while 🥱!`")
    success_no = 0
    failed_no = 0
    total_users = await count_users()
    for user in users_list:
        b_cast = await _do_broadcast(message=r_msg, user=user["user_id"])
        if b_cast == 200:
            success_no += 1
        else:
            failed_no += 1
    await bc_msg.edit(f"""
**Broadcast Completed ✅!**
**Total Users:** `{total_users}`
**Successful Responses:** `{success_no}`
**Failed Responses:** `{failed_no}`
    """)

