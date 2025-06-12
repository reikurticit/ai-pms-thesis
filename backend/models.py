from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    vault = relationship("PasswordVault", back_populates="owner")


class PasswordVault(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    nonce = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="vault")