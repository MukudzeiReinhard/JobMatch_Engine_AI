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
        # Initialization using the modern SDK client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"Analyze the following resume text and extract a clean list of technical and soft skills: {text}"

        # Request structured JSON matching our Pydantic schema
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Leveraging the modern, stable flash model
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SkillsInventory,
                temperature=0.1,  # Low temperature for factual consistency
            ),
        )

        # Safely parse data structured natively by the SDK configuration
        structured_data = SkillsInventory.model_validate_json(response.text)
        return [skill.strip().lower() for skill in structured_data.skills]

    except Exception as e:
        # API Failure Handling: Log the error safely and return a clear fallback
        logger.error(f"Gemini API Skill Extraction Failed: {str(e)}")
        return []  # Safe fallback so your entire user view doesn't throw a 500 error