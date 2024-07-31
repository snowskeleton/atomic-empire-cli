from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Column, String

from .database import Base


class Credentials(Base):
    __tablename__ = "credentials"

    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(String)

    def __init__(self, email: str, password: str):
        self.id = str(uuid4())
        self.email = email
        self.password = password
