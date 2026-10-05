from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    order_id: Mapped[str] = mapped_column(String(60), index=True)
    customer_id: Mapped[str | None] = mapped_column(String(60), nullable=True)
    sku: Mapped[str | None] = mapped_column(String(60), nullable=True)
    failure_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(60), default="NEW")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    classifications: Mapped[list["Classification"]] = relationship(back_populates="case")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="case")
    reviews: Mapped[list["HumanReview"]] = relationship(back_populates="case")


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    failure_reason: Mapped[str] = mapped_column(String(150))
    confidence_score: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(40))
    decision: Mapped[str] = mapped_column(String(80))
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="classifications")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    workflow_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    agent_name: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    case: Mapped[Case] = relationship(back_populates="agent_runs")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(50), default="INIT")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    reviewer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    original_classification: Mapped[str | None] = mapped_column(String(150), nullable=True)
    final_classification: Mapped[str | None] = mapped_column(String(150), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="reviews")


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
