# .------.------.------.------.------.------.------.------.------.------.
# |D.--. |4.--. |N.--. |1.--. |3.--. |L.--. |3.--. |K.--. |0.--. |0.--. |
# | :/\: | :/\: | :(): | :/\: | :(): | :/\: | :(): | :/\: | :/\: | :/\: |
# | (__) | :\/: | ()() | (__) | ()() | (__) | ()() | :\/: | :\/: | :\/: |
# | '--'D| '--'4| '--'N| '--'1| '--'3| '--'L| '--'3| '--'K| '--'0| '--'0|
# `------`------`------`------`------`------`------`------`------`------'
#
#                     Copyright 2022 t.me/D4n13l3k00
#           Licensed under the Creative Commons CC BY-NC-ND 4.0
#
#                    Full license text can be found at:
#       https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
#
#                           Human-friendly one:
#            https://creativecommons.org/licenses/by-nc-nd/4.0

# meta developer: @D4n13l3k00


import io

from .. import loader, utils


def register(cb):
    cb(DUsersMod())


class DUsersMod(loader.Module):
    """DUsers"""

    strings = {"name": "DUsers"}

    def __init__(self):
        self.name = self.strings["name"]
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def ducmd(self, message):
        """ <nn> <n> <m> <s>
        Дамп юзеров чата
        <nn> - Получить всех пользователей без @usernames
        <n> - Получить только пользователей с открытыми номерами
        <m> - Отправить дамп в избранное
        <s> - Тихий дамп
        """
        if not message.chat:
            await message.edit("<b>Это не чат</b>")
            return
        chat = message.chat
        num = False
        nusr = False
        silent = False
        tome = False
        if utils.get_args_raw(message):
            a = utils.get_args_raw(message)
            if "nn" in a:
                nusr = True
            if "n" in a:
                num = True
            if "s" in a:
                silent = True
            if "m" in a:
                tome = True
        if not silent:
            await message.edit("🖤Дампим чат...🖤")
        else:
            await message.delete()
        f = io.BytesIO()
        f.name = f"Dump by {chat.id}.csv"
        f.write("FIRST NAME;LAST NAME;@USERNAME;USER ID;PHONE NUMBER\n".encode())
        me = await message.client.get_me()
        for i in await message.client.get_participants(message.to_id):
            line = ''
            if i.id == me.id:
                continue
            if (nusr) and not i.username:
                line = f"{str(i.first_name)};{str(i.last_name)};{str(i.username)};{str(i.id)};{str(i.phone)}\n".encode()
            elif (num) and i.phone or not (num):
                line = f"{str(i.first_name)};{str(i.last_name)};{str(i.username)};{str(i.id)};{str(i.phone)}\n".encode()
            
            f.write(str(line))
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
                    await message.edit("🖤Дамп юзеров чата сохранён в избранных!🖤")
                else:
                    await message.edit(
                        "🖤Дамп юзеров чата с открытыми номерами сохранён в избранных!🖤"
                    )
            else:
                await message.delete()
        f.close()
