from typing import List
from datetime import datetime
from sqlalchemy import String, Integer, DECIMAL, DateTime, ForeignKey, JSON, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(100))
    signup_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders: Mapped[List["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    profile: Mapped["CustomerProfile | None"] = relationship(back_populates="customer", uselist=False)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    customer: Mapped[Customer] = relationship(back_populates="orders")


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), unique=True)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_spend: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), default=0.00)
    average_order_value: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), default=0.00)
    last_purchase_date: Mapped[datetime | None] = mapped_column(DateTime)
    days_since_last_purchase: Mapped[int | None] = mapped_column(Integer)
    purchase_frequency: Mapped[DECIMAL | None] = mapped_column(DECIMAL(5, 2))
    customer_segment: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer: Mapped[Customer] = relationship(back_populates="profile")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    audience_name: Mapped[str | None] = mapped_column(String(255))
    filters: Mapped[dict | None] = mapped_column(JSON)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    strategy: Mapped[str | None] = mapped_column(Text)
    message_template: Mapped[str | None] = mapped_column(Text)
    subject_line: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    audience_size: Mapped[int] = mapped_column(Integer, default=0)
    business_goal: Mapped[str | None] = mapped_column(Text)
    ai_reasoning: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CampaignAudience(Base):
    __tablename__ = "campaign_audience"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    personalized_message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="sent")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, name="metadata")


class CampaignConversion(Base):
    __tablename__ = "campaign_conversions"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    communication_log_id: Mapped[int | None] = mapped_column(ForeignKey("communication_logs.id"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    converted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    conversion_value: Mapped[DECIMAL | None] = mapped_column(DECIMAL(10, 2))
    attribution_window_days: Mapped[int] = mapped_column(Integer, default=7)
