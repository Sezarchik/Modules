# -*- coding: utf-8 -*-
# Module author: @ftgmodulesbyfl1yd, @dekftgmodules, @memeframe
# modify by: @caesar_do_not_touch, @zet1csce

import asyncio
import io
from asyncio import sleep
from os import remove

from telethon import errors, functions
from telethon.errors import (
    BotGroupsBlockedError,
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    InputUserDeactivatedError,
    MessageTooLongError,
    UserAlreadyParticipantError,
    UserBlockedError,
    UserIdInvalidError,
    UserKickedError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
    YouBlockedUserError,
)
from telethon.tl.functions.channels import InviteToChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetCommonChatsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChannelParticipantCreator,
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
)

from .. import loader, utils


@loader.tds
class ChatMod(loader.Module):
    """Чат модуль"""

    strings = {"name": "Chat Tools"}

    async def client_ready(self, client, db):
        self.db = db

    async def useridcmd(self, message):
        """Команда .userid <@ или реплай> показывает ID выбранного пользователя."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        try:
            if args:
                user = await message.client.get_entity(args if not args.isdigit() else int(args))
            else:
                user = await message.client.get_entity(reply.sender_id)
        except ValueError:
            user = await message.client.get_entity(message.sender_id)
            
        message = await utils.answer(message, f"<b>Имя:</b> <code>{user.first_name}</code>\n"
                                              f"<b>ID:</b> <code>{user.id}</code>")


    async def chatidcmd(self, message):
        """Команда .chatid показывает ID чата."""
        if message.is_private:
            message = await utils.answer(message, "<b>Это не чат!</b>")
            return
        args = utils.get_args_raw(message)
        to_chat = None

        try:
            if args:
                to_chat = args if not args.isdigit() else int(args)
            else:
                to_chat = message.chat_id

        except ValueError:
            to_chat = message.chat_id

        chat = await message.client.get_entity(to_chat)

        message = await utils.answer(message, 
            f"<b>Название:</b> <code>{chat.title}</code>\n"
            f"<b>ID</b>: <code>{chat.id}</code>")

    async def invitecmd(self, event):
        """Используйте .invite <@ или реплай>, чтобы добавить пользователя в чат."""
        if event.fwd_from:
            return
        to_add_users = utils.get_args_raw(event)
        reply = await event.get_reply_message()
        if not to_add_users and not reply:
            await utils.answer(event, "<b>Нет аргументов.</b>")
        elif reply:
            to_add_users = str(reply.from_id)
        if to_add_users:
            if not event.is_group and not event.is_channel:
                return await utils.answer(event, "<b>Это не чат!</b>")
            else:
                if not event.is_channel and event.is_group:
                    # https://tl.telethon.dev/methods/messages/add_chat_user.html
                    for user_id in to_add_users.split(" "):
                        try:
                            userID = int(user_id)
                        except:
                            userID = user_id

                        try:
                            await event.client(
                                AddChatUserRequest(
                                    chat_id=event.chat_id,
                                    user_id=userID,
                                    fwd_limit=1000000,
                                )
                            )
                        except ValueError:
                            return await event.reply("<b>Неверный @ или ID.</b>")
                        except UserIdInvalidError:
                            return await event.reply("<b>Неверный @ или ID.</b>")
                        except UserPrivacyRestrictedError:
                            return await event.reply(
                                "<b>Настройки приватности пользователя не позволяют"
                                " пригласить его.</b>"
                            )
                        except UserNotMutualContactError:
                            return await event.reply(
                                "<b>Настройки приватности пользователя не позволяют"
                                " пригласить его.</b>"
                            )
                        except ChatAdminRequiredError:
                            return await event.reply("<b>У меня нет прав.</b>")
                        except ChatWriteForbiddenError:
                            return await event.reply("<b>У меня нет прав.</b>")
                        except ChannelPrivateError:
                            return await event.reply("<b>У меня нет прав.</b>")
                        except UserKickedError:
                            return await event.reply(
                                "<b>Пользователь кикнут из чата, обратитесь к"
                                " администраторам.</b>"
                            )
                        except BotGroupsBlockedError:
                            return await event.reply(
                                "<b>Бот заблокирован в чате, обратитесь к"
                                " администраторам.</b>"
                            )
                        except UserBlockedError:
                            return await event.reply(
                                "<b>Пользователь заблокирован в чате, обратитесь к"
                                " администраторам.</b>"
                            )
                        except InputUserDeactivatedError:
                            return await event.reply(
                                "<b>Аккаунт пользователя удалён.</b>"
                            )
                        except UserAlreadyParticipantError:
                            return await event.reply(
                                "<b>Пользователь уже в группе.</b>"
                            )
                        except YouBlockedUserError:
                            return await event.reply(
                                "<b>Вы заблокировали этого пользователя.</b>"
                            )
                    await utils.answer(event, "<b>Пользователь приглашён успешно!</b>")
                else:
                    # https://tl.telethon.dev/methods/channels/invite_to_channel.html
                    for user_id in to_add_users.split(" "):
                        try:
                            userID = int(user_id)
                        except:
                            userID = user_id
                        try:
                            await event.client(
                                InviteToChannelRequest(
                                    channel=event.chat_id, users=[userID]
                                )
                            )
                        except ValueError:
                            return await event.reply("<b>Неверный @ или ID.</b>")
                        except UserIdInvalidError:
                            return await event.reply("<b>Неверный @ или ID.</b>")
                        except UserPrivacyRestrictedError:
                            return await event.reply(
                                "<b>Настройки приватности пользователя не позволяют"
                                " пригласить его.</b>"
                            )
                        except UserNotMutualContactError:
                            return await utils.answer(event, 
                                "<b>Настройки приватности пользователя не позволяют"
                                " пригласить его.</b>"
                            )
                        except ChatAdminRequiredError:
                            return await event.reply("<b>У меня нет прав.</b>")
                        except ChatWriteForbiddenError:
                            return await event.reply("<b>У меня нет прав.</b>")
                        except ChannelPrivateError:
                            return await event.reply("<b>У меня нет прав.</b>")
                        except UserKickedError:
                            return await event.reply(
                                "<b>Пользователь кикнут из чата, обратитесь к"
                                " администраторам.</b>"
                            )
                        except BotGroupsBlockedError:
                            return await event.reply(
                                "<b>Бот заблокирован в чате, обратитесь к"
                                " администраторам.</b>"
                            )
                        except UserBlockedError:
                            return await event.reply(
                                "<b>Пользователь заблокирован в чате, обратитесь к"
                                " администраторам.</b>"
                            )
                        except InputUserDeactivatedError:
                            return await event.reply(
                                "<b>Аккаунт пользователя удалён.</b>"
                            )
                        except UserAlreadyParticipantError:
                            return await event.reply(
                                "<b>Пользователь уже в группе.</b>"
                            )
                        except YouBlockedUserError:
                            return await event.reply(
                                "<b>Вы заблокировали этого пользователя.</b>"
                            )
                        await utils.answer(event, "<b>Пользователь приглашён успешно!</b>")

    async def leavecmd(self, message):
        """Используйте команду .leave, чтобы кикнуть себя из чата."""
        args = utils.get_args_raw(message)
        if message.is_private:
            message = await utils.answer(message, "<b>Это не чат!</b>")
            return
        if args:
            message = await utils.answer(message, f"<b>До связи.\nПричина: {args}</b>")
        else:
            message = await utils.answer(message, "<b>До связи.</b>")
        await message.client(LeaveChannelRequest(message.chat_id))

    async def userscmd(self, message):
        """Команда .users <имя>; ничего выводит список всех пользователей в чате."""
        if message.is_private:
            message = await utils.answer(message, "<b>Это не чат!</b>")
            return
        message = await utils.answer(message, "<b>Считаем...</b>")
        args = utils.get_args_raw(message)
        info = await message.client.get_entity(message.chat_id)
        title = info.title or "этом чате"

        if args:
            users = await message.client.get_participants(
                message.chat_id, search=f"{args}"
            )
            mentions = f'<b>В чате "{title}" найдено {len(users)} пользователей с именем {args}:</b> \n'

        else:
            users = await message.client.get_participants(message.chat_id)
            mentions = f'<b>Пользователей в "{title}": {len(users)}</b> \n'
        for user in users:
            if user.deleted:
                mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"

            else:
                mentions += f'\n• <a href ="tg://user?id={user.id}">{user.first_name}</a> | <code>{user.id}</code>'
        try:
            message = await utils.answer(message, mentions)
        except MessageTooLongError:
            message = await utils.answer(message, 
                "<b>Черт, слишком большой чат. Загружаю список пользователей в файл...</b>"
            )
            with open("userslist.md", "w+") as file:
                file.write(mentions)
            await message.client.send_file(
                message.chat_id,
                "userslist.md",
                caption="<b>Пользователей в {}:</b>".format(title),
                reply_to=message.id,
            )
            remove("userslist.md")
            await message.delete()

    async def adminscmd(self, message):
        """Команда .admins показывает список всех админов в чате."""
        if message.is_private:
            message = await utils.answer(message, "<b>Это не чат!</b>")
            return
        message = await utils.answer(message, "<b>Считаем...</b>")
        info = await message.client.get_entity(message.chat_id)
        title = info.title or "this chat"

        admins = await message.client.get_participants(
            message.chat_id, filter=ChannelParticipantsAdmins
        )
        mentions = f'<b>Админов в "{title}": {len(admins)}</b>\n'

        for user in admins:
            admin = admins[
                admins.index((await message.client.get_entity(user.id)))
            ].participant
            if admin:
                rank = admin.rank or "admin"

            else:
                rank = (
                    "creator" if type(admin) == ChannelParticipantCreator else "admin"
                )
            if user.deleted:
                mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"

            else:
                mentions += f'\n• <a href="tg://user?id={user.id}">{user.first_name}</a> | {rank} | <code>{user.id}</code>'
        try:
            message = await utils.answer(message, mentions)
        except MessageTooLongError:
            message = await utils.answer(message, 
                "Черт, слишком много админов здесь. Загружаю список админов в файл..."
            )
            with open("adminlist.md", "w+") as file:
                file.write(mentions)
            await message.client.send_file(
                message.chat_id,
                "adminlist.md",
                caption='<b>Админов в "{}":<b>'.format(title),
                reply_to=message.id,
            )
            remove("adminlist.md")
            await message.delete()

    async def botscmd(self, message):
        """Команда .bots показывает список всех ботов в чате."""
        if message.is_private:
            message = await utils.answer(message, "<b>Это не чат!</b>")
            return
        message = await utils.answer(message, "<b>Считаем...</b>")

        info = await message.client.get_entity(message.chat_id)
        title = info.title or "this chat"

        bots = await message.client.get_participants(
            message.to_id, filter=ChannelParticipantsBots
        )
        mentions = f'<b>Ботов в "{title}": {len(bots)}</b>\n'

        for user in bots:
            if not user.deleted:
                mentions += f'\n• <a href="tg://user?id={user.id}">{user.first_name}</a> | <code>{user.id}</code>'
            else:
                mentions += f"\n• Удалённый бот <b>|</b> <code>{user.id}</code> "

        try:
            message = await utils.answer(message, mentions, parse_mode="html")
        except MessageTooLongError:
            message = await utils.answer(message, 
                "Черт, слишком много ботов здесь. Загружаю " "список ботов в файл..."
            )
            with open("botlist.md", "w+") as file:
                file.write(mentions)
            await message.client.send_file(
                message.chat_id,
                "botlist.md",
                caption='<b>Ботов в "{}":</b>'.format(title),
                reply_to=message.id,
            )
            remove("botlist.md")
            await message.delete()

    async def commoncmd(self, message):
        """Используй .common <@ или реплай>, чтобы узнать общие чаты с
        пользователем."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            message = await utils.answer(message, "<b>Нет аргументов или реплая.</b>")
            return
        message = await utils.answer(message, "<b>Считаем...</b>")
        try:
            if args:
                if args.isnumeric():
                    user = int(args)
                    user = await message.client.get_entity(user)
                else:
                    user = await message.client.get_entity(args)
            else:
                user = await utils.get_user(reply)
        except ValueError:
            message = await utils.answer(message, "<b>Не удалось найти пользователя.</b>")
            return
        msg = f"<b>Общие чаты с {user.first_name}:</b>\n"
        user = await message.client(GetFullUserRequest(user.id))
        comm = await message.client(
            GetCommonChatsRequest(user_id=user.user.id, max_id=0, limit=100)
        )
        count = 0
        m = ""
        for chat in comm.chats:
            m += f'\n• <a href="tg://resolve?domain={chat.username}">{chat.title}</a> <b>|</b> <code>{chat.id}</code> '
            count += 1
        msg = f"<b>Общие чаты с {user.user.first_name}: {count}</b>\n"
        message = await utils.answer(message, f"{msg} {m}")

    async def chatdumpcmd(self, message):
        """.chatdump <n> <m> <s>
        Дамп юзеров чата
        <n> - Получить только пользователей с открытыми номерами
        <m> - Отправить дамп в избранное
        <s> - Тихий дамп
        """
        if not message.chat:
            message = await utils.answer(message, "<b>Это не чат</b>")
            return
        chat = message.chat
        num = False
        silent = False
        tome = False
        if utils.get_args_raw(message):
            a = utils.get_args_raw(message)
            if "n" in a:
                num = True
            if "s" in a:
                silent = True
            if "m" in a:
                tome = True
        if not silent:
            message = await utils.answer(message, "🖤Дампим чат...🖤")
        else:
            await message.delete()
        f = io.BytesIO()
        f.name = f"Dump by {chat.id}.csv"
        f.write("FNAME;LNAME;USER;ID;NUMBER\n".encode())
        me = await message.client.get_me()
        for i in await message.client.get_participants(message.to_id):
            if i.id == me.id:
                continue
            if num and i.phone or not num:
                f.write(
                    f"{i.first_name};{i.last_name};{i.username};{i.id};{i.phone}\n".encode()
                )

        f.seek(0)
        if tome:
            await message.client.send_file("me", f, caption="Дамп чата " + str(chat.id))
        else:
            await message.client.send_file(
                message.to_id, f, caption=f"Дамп чата {str(chat.id)}"
            )

        if not silent:
            if tome:
                if num:
                    message = await utils.answer(message, "🖤Дамп юзеров чата сохранён в " "избранных!🖤")
                else:
                    message = await utils.answer(message, 
                        "🖤Дамп юзеров чата с открытыми "
                        "номерами сохранён в избранных!🖤"
                    )
            else:
                await message.delete()
        f.close()

    async def adduserscmd(self, event):
        """Add members"""
        if len(event.text.split()) == 2:
            idschannelgroup = event.text.split(" ", maxsplit=1)[1]
            user = [
                i async for i in event.client.iter_participants(event.to_id.channel_id)
            ]
            message = await utils.answer(message, 
                f"<b>{len(user)} пользователей будет приглашено из чата {event.to_id.channel_id} в чат/канал {idschannelgroup}</b>"
            )
            for u in user:
                try:
                    try:
                        if not u.bot:
                            await event.client(
                                functions.channels.InviteToChannelRequest(
                                    idschannelgroup, [u.id]
                                )
                            )
                            await asyncio.sleep(1)
                    except Exception:
                        pass
                except errors.FloodWaitError as e:
                    print("Flood for", e.seconds)
        else:
            message = await utils.answer(message, "<b>Куда приглашать будем?</b>")

    async def reportcmd(self, message):
        """Репорт пользователя за спам."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args:
            user = await message.client.get_entity(
                args if not args.isnumeric() else int(args)
            )
        if reply:
            user = await message.client.get_entity(reply.sender_id)
        else:
            message = await utils.answer(message, "<b>Кого я должен зарепортить?</b>")
            return

        await message.client(functions.messages.ReportSpamRequest(peer=user.id))
        message = await utils.answer(message, "<b>Ты получил репорт за спам!</b>")
        await sleep(1)
        await message.delete()

    async def echocmd(self, message):
        """Активировать/деактивировать Echo."""
        echos = self.db.get("Echo", "chats", [])
        chatid = str(message.chat_id)

        if chatid not in echos:
            echos.append(chatid)
            self.db.set("Echo", "chats", echos)
            message = await utils.answer(message, "<b>[Echo Mode]</b> Активирован в этом чате!")
            return

        echos.remove(chatid)
        self.db.set("Echo", "chats", echos)
        message = await utils.answer(message, "<b>[Echo Mode]</b> Деактивирован в этом чате!")
        return

    async def watcher(self, message):
        echos = self.db.get("Echo", "chats", [])
        chatid = str(message.chat_id)

        if chatid not in str(echos):
            return
        if message.sender_id == (await message.client.get_me()).id:
            return

        await message.client.send_message(
            int(chatid), message, reply_to=await message.get_reply_message() or message
        )
