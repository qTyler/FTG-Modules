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


# requires: glQiwiApi pycryptodome

import asyncio
import hashlib

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from glQiwiApi import QiwiWrapper
from telethon import types

from .. import loader, utils


@loader.tds
class QiwiMod(loader.Module):
    "Модуль для работы с Qiwi кошельком"

    strings = {
        "name": "Qiwi",
        "pref": "<b>[Qiwi]</b> ",
        "need_arg": "{}need args...",
        "phone_setted_successfully": "{}Номер и токен установлены!",
        "p2p_setted_successfully": "{}Секретный P2P токен установлен!",
        "need_phone_token": "{}Необходимо установить номер токен!",
        "need_p2p": "{}Необходимо установить P2P токен!",
        "bal": "{}Баланс: {}",
        "commission": "{}Итоговая сумма: {}\nКомиссия Qiwi: {}\nСумма к зачислению: {}",
        "sent": "{}Средства отправлены!\nID: <code>{}</code>",
        "bill_created": "{}Счёт создан!\n{}\nСтатус счёта: <code>{}</code>",
        "bill_payed": "Оплачен",
        "bill_notpayed": "Не оплачен",
        "bill_disabled": "Автопроверка отключена после 5 минут",
        "bill_link_exp": "Ссылка истекла по причине оплаты",
        "_cfg_qiwi_phone": "Установить номер кошелька",
        "_cfg_qiwi_token": "Установить токен",
        "_cfg_qiwi_p2p_token":"Установить P2P токен"
    }
    _db = "QiwiMod"
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue( # self.config["qiwi_phone"]
                "qiwi_phone",
                "None",
                lambda: self.strings("_cfg_qiwi_phone"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue( # self.config["qiwi_token"]
                "qiwi_token",
                "None",
                lambda: self.strings("_cfg_qiwi_token"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue( # self.config["qiwi_p2p_token"]
                "qiwi_p2p_token",
                "None",
                lambda: self.strings("_cfg_qiwi_p2p_token"),
                validator=loader.validators.String(),
            )
        )    
                
    async def client_ready(self, _, db):
        self.db = db
        self.me = await _.get_me()


    def __need_token(func):
        async def wrapper(self, m: types.Message):
            if not self.config["qiwi_phone"] or not self.config["qiwi_token"]:
                return await utils.answer(
                    m,
                    self.strings("need_phone_token").format(self.strings("pref")),
                )
            return await func(self, m)

        return wrapper

    def __need_p2p(func):
        async def wrapper(self, m: types.Message):
            return (
                await func(self, m)
                if sself.config["qiwi_p2p_token"]
                else await utils.answer(
                    m,
                    self.strings("need_p2p").format(self.strings("pref")),
                )
            )

        return wrapper

    #async def qsetp2pcmd(self, m: types.Message):
    #    """ <TOKEN>
    #    Установить секретный p2p ключ"""
    #    if args := utils.get_args(m):
    #        self.db.set(self._db,"p2p", args[0])
    #        return await utils.answer(
    #            m, self.strings("p2p_setted_successfully").format(self.strings("pref"))
    #        )
    #    await utils.answer(m, self.strings("need_arg").format(self.strings("pref")))

    # async def qsetcmd(self, m: types.Message):
        # """ <phone> <TOKEN>
        # Установить номер и токен"""
        # if args := utils.get_args(m):
            # self.db.set(self._db,"phone", args[0])
            # self.db.set(self._db,"token", args[1])
            # return await utils.answer(
                # m,
                # self.strings("phone_setted_successfully").format(self.strings("pref")),
            # )
        # await utils.answer(m, self.strings("need_arg").format(self.strings("pref")))

    @__need_token
    async def qbalcmd(self, m: types.Message):
        " - Получить баланс"
        async with QiwiWrapper(self.config["qiwi_token"], "+" + self.config["qiwi_phone"]) as w:
            w: QiwiWrapper
            bal = await w.get_balance()
            await utils.answer(
                m,
                self.strings("bal").format(
                    self.strings("pref"), str(bal.amount) + bal.currency.symbol
                ),
            )

    @__need_token
    async def qswalcmd(self, m: types.Message):
        " <phone> <amount> <?comment> - Отправить средства по номеру"
        async with QiwiWrapper(self.config["qiwi_token"], self.config["qiwi_phone"]) as w:
            w: QiwiWrapper
            args = utils.get_args(m)
            args_raw = utils.get_args_raw(m)
            trans_id = await w.to_wallet(
                to_number=args[0],
                amount=int(args[1]),
                comment=args_raw.split(args[1])[1].strip() if len(args) > 2 else None,
            )
            await utils.answer(
                m,
                self.strings("sent").format(
                    self.strings("pref"), str(trans_id.payment_id)
                ),
            )

    @__need_token
    async def qscardcmd(self, m: types.Message):
        " <card_num[no_spaces]> <amount> - Отправить средства на карту"
        async with QiwiWrapper(self.config["qiwi_token"], self.config["qiwi_phone"]) as w:
            w: QiwiWrapper
            args = utils.get_args(m)
            trans_id = await w.to_card(
                to_card=args[0],
                trans_sum=float(args[1]),
            )
            await utils.answer(
                m,
                self.strings("sent").format(
                    self.strings("pref"), str(trans_id.payment_id)
                ),
            )

    @__need_token
    async def qcmscmd(self, m: types.Message):
        " <card_num/phone> <amount> - Посчитать комиссию"
        async with QiwiWrapper(self.config["qiwi_token"], self.config["qiwi_phone"]) as w:
            w: QiwiWrapper
            args = utils.get_args(m)
            commission = await w.calc_commission(args[0], float(args[1]))
            await utils.answer(
                m,
                self.strings("commission").format(
                    self.strings("pref"),
                    str(commission.withdraw_sum.amount)
                    + commission.withdraw_sum.currency.symbol,
                    str(commission.qiwi_commission.amount)
                    + commission.qiwi_commission.currency.symbol,
                    str(commission.enrollment_sum.amount)
                    + commission.enrollment_sum.currency.symbol,
                ),
            )

    @__need_p2p
    async def qp2pcmd(self, m: types.Message):
        " <amount> <?comment> - Создать счёт для оплаты"
        async with QiwiWrapper(secret_p2p=self.config["qiwi_p2p_token"]) as w:
            w: QiwiWrapper
            args = utils.get_args(m)
            args_raw = utils.get_args_raw(m)
            bill = await w.create_p2p_bill(
                amount=args[0],
                comment=args_raw.split(args[0])[1].strip() if len(args) > 1 else None,
            )
            last_status = None
            url = bill.pay_url
            n = 0
            while True:
                if n >= 72:
                    await utils.answer(
                        m,
                        self.strings("bill_created").format(
                            self.strings("pref"),
                            self.strings("bill_link_exp"),
                            self.strings("bill_disabled"),
                        ),
                    )
                    break
                status = (await w.check_p2p_bill_status(bill_id=bill.id)) == "PAID"
                if status != last_status:
                    last_status = status
                    await utils.answer(
                        m,
                        self.strings("bill_created").format(
                            self.strings("pref"),
                            url,
                            self.strings("bill_payed" if status else "bill_notpayed"),
                        ),
                    )
                    if status:
                        break
                n += 1
                await asyncio.sleep(5)
