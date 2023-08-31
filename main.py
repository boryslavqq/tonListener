import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import config
from database.dao.holder import DAO
from database.models.base import Base
from utils.listener import TonListener
from utils.ton_api import TonApi


async def on_transaction(transaction, db: DAO):
    wallets = await db.wallet.get_all()

    account = transaction["account"]

    if account in [wal.wallet for wal in wallets]:
        print(account)


async def main():
    engine: AsyncEngine = create_async_engine(config.DATABASE_URI, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    ton = TonApi("https://toncenter.com",
                 "6cda0934e83bf49807ae65817dab80318ba494aa734fbcc923d607d930a2db61")

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
