from typing import List, Optional, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load, selectinload

from database.dao.base import BaseDAO
from database.models.wallet import Wallet


class WalletDAO(BaseDAO[Wallet]):
    def __init__(self, session: AsyncSession):
        super().__init__(Wallet, session)

    async def get_all(self) -> List[Wallet]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_by_wallet(self, wallet: str) -> Wallet:
        res = await self.session.execute(select(self.model).filter_by(wallet=wallet))
        return res.scalar_one_or_none()
