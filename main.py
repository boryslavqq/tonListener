import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from tonsdk.contract.wallet import WalletVersionEnum

from config import config
from database.dao.holder import DAO
from database.models.base import Base
from utils.listener import TonListener
from utils.ton_api import TonApi


async def on_transaction(transaction, db: DAO, ton: TonApi):
    wallets = await db.wallet.get_all()

    account = transaction["account"]

    _wallet = next((wal for wal in wallets if wal.wallet == account), None)

    if _wallet is not None:
        balance = transaction["in_msg"]["value"]
        balance = int(balance * 0.99)
        wallet = await ton.get_wallet_by_keys(_wallet.public_key, _wallet.private_key, WalletVersionEnum.v3r2,
                                              workchain=0)

        await ton.send_tons(wallet, config.MAIN_ADDRESS, balance)


async def main():
    engine: AsyncEngine = create_async_engine(config.DATABASE_URI, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    #
    ton = TonApi(config.TON_URL,
                 config.API_TON_KEY)

    listener = TonListener(on_transaction, ton, async_sessionmaker())

    try:
        await listener.start()
    finally:
        async_sessionmaker.close_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Program stopped")
