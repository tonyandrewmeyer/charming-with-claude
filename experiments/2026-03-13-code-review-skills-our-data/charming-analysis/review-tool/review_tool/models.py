"""Pydantic models for findings."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FindingCreate(BaseModel):
    """A finding submitted for review."""

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
    source_file: str | None = None


class FindingUpdate(BaseModel):
    """The reviewable fields of a finding."""

    review_status: str | None = None
    reviewer_notes: str | None = None


class FindingOut(FindingCreate):
    """A finding as returned by the API."""

    id: int
    review_status: str = "pending"
    reviewer_notes: str = ""
    reviewed_at: str | None = None
    created_at: str = ""
    updated_at: str = ""


class ConfirmedSafeCreate(BaseModel):
    """A finding confirmed as a false positive."""

    repo: str
    round: int
    location: str
    explanation: str
    source_file: str | None = None


class Stats(BaseModel):
    """Aggregate review progress counts."""

    total: int = 0
    pending: int = 0
    reviewed: int = 0
    false_positive: int = 0
    by_severity: dict = Field(default_factory=dict)
    by_repo: dict = Field(default_factory=dict)
    by_round: dict = Field(default_factory=dict)
