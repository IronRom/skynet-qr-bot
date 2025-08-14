from sqlalchemy import BigInteger, String, Column, Boolean
from .db_base import Base

class User(Base):
    __tablename__ = 'users'
    

    telegram_id = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_owner = Column(Boolean)
    is_admin = Column(Boolean)
