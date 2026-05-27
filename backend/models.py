from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    file_id: str
    resume_data: dict
    filename: str


class AnalyzeRequest(BaseModel):
    file_id: str
    jd_text: Optional[str] = None
    jd_url: Optional[str] = None


class MatchedPoint(BaseModel):
    client: str
    point: str
    jd_match: str


class MissingPoint(BaseModel):
    client: str
    suggested_point: str
    jd_requirement: str


class AnalysisResult(BaseModel):
    matched_points: list[MatchedPoint]
    missing_points: list[MissingPoint]
    missing_skills: list[str]


class ClientSummary(BaseModel):
    client: str
    summary: str


class SummariesResult(BaseModel):
    per_client_summaries: list[ClientSummary]
    overall_summary: str


class AnalyzeResponse(BaseModel):
    file_id: str
    analysis: AnalysisResult
    summaries: SummariesResult
