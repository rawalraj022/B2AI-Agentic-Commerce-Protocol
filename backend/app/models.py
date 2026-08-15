"""SQLAlchemy ORM models for the B2AI protocol."""
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    network = Column(String, default="Avalanche C-Chain")
    asset = Column(String, default="XSGD")
    created_at = Column(DateTime, default=utcnow)

    policies = relationship("Policy", back_populates="wallet", cascade="all, delete-orphan")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    max_transaction = Column(Float, default=100.0)
    daily_limit = Column(Float, default=500.0)
    allowed_merchants = Column(JSON, default=list)
    currency = Column(String, default="XSGD")
    created_at = Column(DateTime, default=utcnow)

    wallet = relationship("Wallet", back_populates="policies")


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True, index=True)
    authorization_id = Column(String, unique=True, index=True, nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    wallet_address = Column(String, nullable=False)
    merchant = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="XSGD")
    nonce = Column(String, nullable=False)
    commitment = Column(String, nullable=False)
    expiry = Column(DateTime, nullable=False)
    status = Column(String, default="AUTHORIZED")  # AUTHORIZED | CANCELLED | SETTLED
    created_at = Column(DateTime, default=utcnow)

    credential = relationship("Credential", back_populates="authorization", uselist=False)
    payment = relationship("Payment", back_populates="authorization", uselist=False)


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(String, unique=True, index=True, nullable=False)
    authorization_id = Column(Integer, ForeignKey("authorizations.id"), nullable=False)
    credential_hash = Column(String, nullable=False)
    type = Column(String, default="single_use")
    max_amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE | USED | EXPIRED
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    authorization = relationship("Authorization", back_populates="credential")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    authorization_id = Column(Integer, ForeignKey("authorizations.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING | EXECUTED | SETTLED | FAILED
    transaction_hash = Column(String, nullable=True)
    network = Column(String, default="Avalanche Fuji C-Chain")
    simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    authorization = relationship("Authorization", back_populates="payment")