"""Pydantic models for findings."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class FindingCreate(BaseModel):
    bug_id: str
    repo: str
    charm_name: str
    round: int
    category: str
    title: str
    severity: str
    location: str
    pattern: str
    issue: str
    impact: str
    evidence: str
    recommended_fix: str
    historical_precedent: str = ""
    source_file: Optional[str] = None


class FindingUpdate(BaseModel):
    review_status: Optional[str] = None
    reviewer_notes: Optional[str] = None


class FindingOut(FindingCreate):
    id: int
    review_status: str = "pending"
    reviewer_notes: str = ""
    reviewed_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class ConfirmedSafeCreate(BaseModel):
    repo: str
    round: int
    location: str
    explanation: str
    source_file: Optional[str] = None


class Stats(BaseModel):
    total: int = 0
    pending: int = 0
    reviewed: int = 0
    false_positive: int = 0
    by_severity: dict = Field(default_factory=dict)
    by_repo: dict = Field(default_factory=dict)
    by_round: dict = Field(default_factory=dict)
