from sqlalchemy import Column, BigInteger, String, DateTime, func, JSON

from database.models.base import Base


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(BigInteger, primary_key=True)
    wallet = Column(String(70), unique=True, index=True)
    mnemonics = Column(JSON, default=None)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
