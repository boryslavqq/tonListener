import asyncio
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from tonsdk.contract.wallet import WalletVersionEnum

from config import config
from database.dao.holder import DAO
from database.models.base import Base
from database.models.wallet import Wallet
from utils.listener import TonListener
from utils.ton_api import TonApi


async def on_transaction(transaction, ton: TonApi, dao: DAO):
    account = transaction["in_msg"]["destination"]

    _wallet = await dao.wallet.get_by_wallet(account)

    if _wallet is not None:
        print(f"HERE IS THE TRANSACTION to {account} from {transaction['in_msg']['source']}")

        balance = transaction["in_msg"]["value"]
        balance = int(balance * 0.99)
        mnemonics, pub_k, priv_k, wallet = await ton.get_wallet_by_mnemonics(WalletVersionEnum.v3r2,
                                                                             workchain=0, mnemonics=_wallet.mnemonics)

        message = await ton.send_tons(wallet, config.MAIN_ADDRESS, balance)
        if message["ok"]:
            print("TRANSACTION WAS SUCCESSFULLY SENT TO THE MAIN WALLET")
            return
        print(f"error occured while trying send_tons - {message}")


async def main():
    engine: AsyncEngine = create_async_engine(config.DATABASE_URI, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    #

    async with async_sessionmaker() as session:
        ton = TonApi(config.TON_URL,
                     config.API_TON_KEY)

        listener = TonListener(on_transaction, ton, session)

        try:
            await listener.start()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit, RuntimeError):
        logging.error("Program stopped")
