import os
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None


load_dotenv()

router = APIRouter()


class GenerateRequest(BaseModel):
    document_type: str = Field(..., min_length=1)
    parties: str = Field(..., min_length=1)
    terms: str = Field(..., min_length=1)
    dates: str = Field(..., min_length=1)


MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _fallback_content(data: GenerateRequest) -> str:
    document_type = data.document_type.strip()
    parties = data.parties.strip()
    terms = data.terms.strip()
    dates = data.dates.strip()

    return (
        f"{document_type}\n\n"
        f"This {document_type} is entered into as of {dates}.\n\n"
        f"Parties:\n{parties}\n\n"
        f"Terms and Conditions:\n{terms}\n\n"
        "This document is intended as an AI-assisted drafting template for informational purposes only. "
        "It should be reviewed by qualified legal counsel before use."
    )


def _generate_with_gemini(payload: GenerateRequest) -> str:
    if genai is None:
        return _fallback_content(payload)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_content(payload)

    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            "Draft a polished legal document in clear professional legal language. "
            "Use the following inputs and preserve the structure of a real legal agreement. "
            "Return only the document text without markdown fences or commentary.\n\n"
            f"Document Type: {payload.document_type}\n"
            f"Parties: {payload.parties}\n"
            f"Terms and Conditions: {payload.terms}\n"
            f"Effective Date / Dates: {payload.dates}\n"
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if text and text.strip():
            return text.strip()
        if hasattr(response, "candidates") and response.candidates:
            first = response.candidates[0]
            if hasattr(first, "content") and hasattr(first.content, "parts"):
                parts = []
                for part in first.content.parts:
                    if hasattr(part, "text") and part.text:
                        parts.append(part.text)
                combined = "".join(parts)
                if combined.strip():
                    return combined.strip()
        return _fallback_content(payload)
    except Exception:
        return _fallback_content(payload)


@router.post("/generate")
def generate_document(payload: GenerateRequest) -> dict[str, Any]:
    content = _generate_with_gemini(payload)
    return {
        "content": content,
        "document_type": payload.document_type,
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
