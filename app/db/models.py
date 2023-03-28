from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, String, Boolean, JSON, BigInteger, ForeignKey
from sqlalchemy.orm import declarative_base, backref, relationship

Base = declarative_base()


class StateData(Base):
    __tablename__ = 'state_data'

    chat_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    bot_id = Column(BigInteger, primary_key=True)
    state = Column(String(255))
    data = Column(JSON(none_as_null=True))


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(length=32))
    first_name = Column(String)
    last_name = Column(String)
    registered = Column(TIMESTAMP, nullable=False, default=datetime.utcnow())
    activity = Column(TIMESTAMP, nullable=False, default=datetime.utcnow())
    menu_id = Column(BigInteger, nullable=False)
    state = Column(JSON(none_as_null=True))
    is_blocked = Column(Boolean, nullable=False, default=False)

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
