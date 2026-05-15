import google.generativeai as genai
import os
import re

from mysite import settings

# Configure the API
genai.configure(api_key=settings.GEMINI_API_KEY)
# Use a supported Gemini model that works with the current SDK/API version
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def extract_skills_with_gemini(cv_text):
    """Extract professional skills from resume text using Gemini API.
    
    Args:
        cv_text: Raw text extracted from resume
        
    Returns:
        list: List of extracted skill strings (lowercase, cleaned)
        
    Raises:
        Exception: If API call fails
    """
    if not cv_text or not cv_text.strip():
        return []
    
    prompt = f"""
    You are an expert HR recruiter. Extract a list of professional skills from the following CV text.
    Return ONLY a comma-separated list of skills. 
    Example: Python, Project Management, SQL, Public Speaking.
    
    CV Text:
    {cv_text[:5000]}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = getattr(response, 'text', None)

        if not response_text:
            raise ValueError("Gemini returned an empty response. Check your API key and service availability.")

        response_text = response_text.strip()
        if not response_text:
            raise ValueError("Gemini returned empty text. Check the request format or API response.")

        # Parse response - handle various formats
        # Remove common list markers (numbers, bullets)
        cleaned = re.sub(r'^[\d\.\-\*\•\s]+', '', response_text, flags=re.MULTILINE)
        
        # Split by comma, newline, or semicolon
        skills_list = re.split(r'[\,\n;]', cleaned)
        
        # Clean each skill: strip whitespace, lowercase, remove empty strings
        skills_list = [
            s.strip().lower() 
            for s in skills_list 
            if s.strip() and len(s.strip()) > 0 and len(s.strip()) < 50
        ]
        
        if not skills_list:
            raise ValueError(f"Gemini did not return extractable skills. Response was: {response_text[:200]}")

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills_list:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills[:50]  # Limit to 50 skills to prevent storage issues
        
    except Exception as e:
        print(f"Error extracting skills with Gemini: {e}")
        raise