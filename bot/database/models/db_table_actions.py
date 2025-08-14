from sqlalchemy import BigInteger, String, Column, Boolean, ForeignKey
from .db_base import Base

class Actions(Base):
    __tablename__ = "actions"


    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    qr_request = Column(String, nullable=False)
