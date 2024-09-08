import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import F, Router, Bot
from os import getenv
from dotenv import load_dotenv
from app.keyboards import start_keyboard, admin_keyboard
from aiogram.types import ChatPermissions
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import CallbackQuery
from better_profanity import profanity
import re


#Routers
router_admin = Router()
router_user = Router()
router = Router()
router_messages =Router()
router_congat = Router()
router_profinity = Router()
load_dotenv()
ADMIN = int(getenv('ADMIN'))
profanity.load_censor_words()


@router.message()
async def handler_antiflood():
    return


@router_congat.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated, bot: Bot):
    await bot.send_message(chat_id=event.chat.id, text=f"Congratulations to {event.new_chat_member.user.first_name}!")


@router_congat.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated, bot: Bot):
     await bot.send_message(chat_id=event.chat.id, text=f"Goodbye {event.new_chat_member.user.first_name}!")


@router_messages.message(F.new_chat_members)
async def delete_new_member_message(message: Message):
    await message.delete()

@router_messages.message(F.left_chat_member)
async def delete_left_member_message(message: Message):
    await message.delete()

@router_messages.message(F.new_chat_photo)
async def delete_new_chat_photo_message(message: Message):
    await message.delete()

@router_messages.message(F.delete_chat_photo)
async def delete_delete_chat_photo_message(message: Message):
    await message.delete()

@router_messages.message(F.new_chat_title)
async def delete_new_chat_title_message(message: Message):
    await message.delete()

@router_messages.message(F.pinned_message)
async def delete_pinned_message(message: Message):
    await message.delete()

@router_messages.message(F.unpin_all_messages)
async def delete_unpin_all_messages(message: Message):
    await message.delete()


@router_profinity.message(F.text)
async def handle_message(message: Message):
    text = message.text
    if profanity.contains_profanity(text):
        await message.delete()
        return



@router_profinity.edited_message(F.text)
async def bad_words_edited(message: Message):
    text = message.text
    if profanity.contains_profanity(text):
        await message.delete()
        return
    

#Mute command(for admin)
@router_admin.message(Command('mute'), F.text)
async def mute_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("User not found.")
    
    args = message.text.split()

    if len(args) < 2:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply(f"User {message.reply_to_message.from_user.first_name} muted")
    else:
        try:
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.reply_to_message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.reply(f"User {message.reply_to_message.from_user.first_name} muted for {args[1]}s")
            await asyncio.sleep(int(args[1]))
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.reply_to_message.from_user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_other_messages=True,
                    can_pin_messages=True,
                    can_invite_users=True,
                    can_change_info=True
                )
            )
        except Exception:
            await message.reply("Invalid arguments or you try mute administrator")
    

#Unmute command(for admin)
@router_admin.message(Command('unmute'), F.text)
async def unmute_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("User not found.")
    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.reply_to_message.from_user.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_other_messages=True,
            can_pin_messages=True,
            can_invite_users=True,
            can_change_info=True
        )
    )
    await message.reply(f"User {message.reply_to_message.from_user.first_name} unmuted")


#Ban command(for admin)
@router_admin.message(Command('ban'), F.text)
async def ban_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("User not found.")
    await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.reply(f"User {message.reply_to_message.from_user.first_name} banned")


#Help for admin
@router_admin.message(Command('help_admin'), F.text)
async def cmd_help(message: Message):
    await message.reply("Commands for admins:\n-----------------\n/mute or /mute (time in seconds) - mute member as reply for message\n-----------------\n/unmute - unmute member as reply for message\n-----------------\n/ban - ban member as reply for message")


#Show user id
@router_admin.message(Command('id'), F.text)
async def cmd_id(message: Message):
    if not message.reply_to_message:
        return await message.reply("User not found.")
    else:
        await message.reply(f"{message.reply_to_message.from_user.first_name} id:{message.reply_to_message.from_user.id}")
    

#Start
@router_user.message(CommandStart(), F.text)
async def cmd_start(message: Message):
    await message.answer(f"Welcome to ModX! 🎉\nI’m here to help keep your chat safe and clean. Customize my settings to fit your needs, and let’s start moderating together! \nType /help to see all available commands.", reply_markup=start_keyboard)


#Help for users
@router_user.message(Command('help'), F.text)
async def cmd_help(message: Message):
    await message.reply("Commands for users:\n-----------------\n/start - show start message\n-----------------\nIf you admin use \n/help_admin")


@router_user.callback_query(lambda callback_query: callback_query.data == 'show_help')
async def send_help_message(callback_query: CallbackQuery):
    text = "Commands for users:\n-----------------\n/start - show start message\n-----------------\nIf you admin use button"

    await callback_query.message.answer(text, reply_markup=admin_keyboard)

    await callback_query.answer()


@router_user.callback_query(lambda callback_query: callback_query.data == 'admin_help')
async def send_admin_help(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id == ADMIN:
        text = "Commands for admins:\n-----------------\n/mute or /mute (time in seconds) - mute member as reply for message\n-----------------\n/unmute - unmute member as reply for message\n-----------------\n/ban - ban member as reply for message"

        await callback_query.message.answer(text)

        await callback_query.answer()
    else:
        await callback_query.answer()
        

