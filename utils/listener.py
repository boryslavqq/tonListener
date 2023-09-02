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

        last_proceed_masterBlock = 0

        while True:
            last_block = await self.ton.get_last_block()
            last_masterchain_block_number = last_block["result"]["last"]["seqno"]

            if last_proceed_masterBlock == 0:
                last_proceed_masterBlock = last_masterchain_block_number
            elif last_masterchain_block_number > last_proceed_masterBlock:
                last_proceed_masterBlock += 1

            for transaction in await self.ton.get_transactions_by_seqno(str(last_proceed_masterBlock)):
                asyncio.create_task(self.on_transaction(transaction, DAO(self.session), self.ton, ))
            await asyncio.sleep(2)
