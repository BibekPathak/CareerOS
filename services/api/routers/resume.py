import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_user_repo, get_document_repo, get_resume_profile_repo,
)
from models.models import User, Document, DocumentType, DocumentStatus, ResumeProfile
from schemas import ResumeUploadResponse, ResumeProfileResponse
from packages.ai.agents.resume_agent import parse_resume

router = APIRouter(prefix="/resume", tags=["resume"])

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: uuid.UUID = "00000000-0000-0000-0000-000000000001",
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    document = Document(
        user_id=user_id,
        type=DocumentType.RESUME,
        file_path=str(file_path),
        status=DocumentStatus.PENDING,
    )
    doc_repo = get_document_repo(db)
    document = await doc_repo.create(document)

    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        raw_text = "\n".join(page.get_text() for page in doc)
        doc.close()

        parsed = await parse_resume(raw_text)

        profile = ResumeProfile(
            user_id=user_id,
            skills=parsed.skills,
            projects=[p.model_dump() for p in parsed.projects],
            experience=[e.model_dump() for e in parsed.experience],
            technologies=parsed.technologies,
            seniority=parsed.seniority,
            preferred_roles=parsed.preferred_roles,
            company_interests=parsed.company_interests,
            raw_text=raw_text,
        )
        profile_repo = get_resume_profile_repo(db)
        await profile_repo.upsert(profile)

        document.status = DocumentStatus.PROCESSED
        await doc_repo.update(document)

        return ResumeUploadResponse(id=document.id, status="processed", message="Resume parsed successfully")

    except Exception as e:
        document.status = DocumentStatus.FAILED
        await doc_repo.update(document)
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.get("/{user_id}", response_model=ResumeProfileResponse)
async def get_resume(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    profile_repo = get_resume_profile_repo(db)
    profile = await profile_repo.get_by_user(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Resume not found")
    return profile
