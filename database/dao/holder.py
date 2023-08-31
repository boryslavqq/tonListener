from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.wallet import WalletDAO


class DAO:
    """Holder data access object"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def wallet(self):
        return WalletDAO(self.session)
