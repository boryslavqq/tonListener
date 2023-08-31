from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.base import BaseDAO
from database.models.wallet import Wallet


class WalletDAO(BaseDAO[Wallet]):
    def __init__(self, session: AsyncSession):
        super().__init__(Wallet, session)

    async def get_all(self) -> List[Wallet]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()
