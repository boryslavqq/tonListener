import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from utils.ton_api import TonApi
from database.dao.holder import DAO


class TonListener:
    def __init__(self, on_transaction, ton: TonApi, session: AsyncSession):
        self.ton = ton
        self.on_transaction = on_transaction
        self.session = session

    async def start(self):

        while True:
            last_block = await self.ton.get_last_block()
            print(last_block)
            seqno = last_block["result"]["last"]["seqno"]

            for transaction in await self.ton.get_transactions_by_seqno(str(seqno)):
                asyncio.create_task(self.on_transaction(transaction, DAO(self.session)))

            await asyncio.sleep(2)
