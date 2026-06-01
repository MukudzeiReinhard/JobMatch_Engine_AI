from google import genai
from google.genai import types
from pydantic import BaseModel
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)


# Define the exact data structure we want back
class SkillsInventory(BaseModel):
    skills: list[str]

def anonymous_text(text: str) -> str:
    # Strip out phone numbers (Handles common formats +263..., 077..., etc.) and email addresses to protect privacy before sending to Gemini
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REMOVED]', text)
    text = re.sub(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE_REMOVED]', text)
    return text 

class _DefaultModelWrapper:
    def generate_content(self, *args, **kwargs):
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return client.models.generate_content(*args, **kwargs)


# Module-level `model` object so tests can patch `accounts.skills_extraction.model.generate_content`
model = _DefaultModelWrapper()


def extract_skills_with_gemini(text: str) -> list[str]:
    text = anonymous_text(text)
    """Extract professional skills from resume text using Gemini API with structured output.
    
    Args:
        text: Raw text extracted from resume
        
    Returns:
        list: List of extracted skill strings (lowercase, cleaned)
    """
    # Fallback / Content Processing Guard: Check for empty text
    if not text or not text.strip():
        logger.warning("Empty text passed to skill extraction.")
        return []

    try:
        prompt = f"Analyze the following resume text and extract a clean list of technical and soft skills: {text}"

        # Use module-level model (so tests can patch it); default wrapper will call the real client
        response = model.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SkillsInventory,
                temperature=0.1,
            ),
        )

        resp_text = getattr(response, 'text', '') or ''
        if not resp_text.strip():
            # Explicit handling for empty API responses to aid tests
            raise ValueError('Empty response from skill extraction')

        skills_raw = []
        # Try JSON structured parse first
        rt = resp_text.strip()
        if rt.startswith('{') or rt.startswith('['):
            try:
                structured_data = SkillsInventory.model_validate_json(resp_text)
                skills_raw = structured_data.skills or []
            except Exception:
                # Fall back to splitting plain text
                pass

        if not skills_raw:
            # Split on commas, semicolons, or newlines
            tokens = re.split(r'[,;\n]+', resp_text)
            skills_raw = [t.strip() for t in tokens if t.strip()]

        # Deduplicate while preserving order and limit to 50
        seen = set()
        cleaned = []
        for s in skills_raw:
            s_clean = str(s).strip().lower()
            if not s_clean:
                continue
            if s_clean in seen:
                continue
            seen.add(s_clean)
            cleaned.append(s_clean)
            if len(cleaned) >= 50:
                break

        return cleaned

    except ValueError:
        # Propagate ValueError for explicit empty responses
        raise
    except Exception as e:
        logger.error(f"Gemini API Skill Extraction Failed: {str(e)}")
        return []