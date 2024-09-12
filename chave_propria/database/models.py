from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()

T_UsersForeignKey = Annotated[
    Mapped[int],
    mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), init=True, primary_key=True
    ),
]

# Representa uma tabela no banco de dados
@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, init=False, onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class Contatos:
    __tablename__ = 'contatos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    contato_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    status: Mapped[str] = mapped_column(default='pending', init=False)
    chat_id: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, init=False, server_default=func.now()
    )

    UniqueConstraint('user_id', 'contato_id', name='user_contato_unique')
