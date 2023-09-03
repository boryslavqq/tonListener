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

            if last_proceed_masterBlock == last_masterchain_block_number:
                await asyncio.sleep(2)
                continue

            if last_proceed_masterBlock == 0:
                last_proceed_masterBlock = last_masterchain_block_number
            elif last_masterchain_block_number > last_proceed_masterBlock:
                last_proceed_masterBlock += 1

            await self.check_block(last_proceed_masterBlock)
            await asyncio.sleep(2)

    async def check_block(self, block_seqno):

        wallets = [wallet.wallet for wallet in await DAO(self.session).wallet.get_all()]

        transactions = await self.ton.get_transactions_by_seqno(str(block_seqno))

        # TODO: wrap transaction['in_msg']['destination'] into same format as wallet.wallet
        valid_transactions = [transaction for transaction in transactions if
                              transaction.get('in_msg') is not None and transaction['in_msg'].get(
                                  'destination') in wallets]

        if valid_transactions:
            for trans in valid_transactions:
                await self.on_transaction(trans, self.ton, DAO(self.session))
