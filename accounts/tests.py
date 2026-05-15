from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
import io
from .models import employee_account
from .validators import validate_resume_size_and_type as validate_pdf_resume
from .skills_extraction import extract_skills_with_gemini
from docx import Document


class EmployeeAccountModelTests(TestCase):
    """Test the employee_account model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee = employee_account.objects.create(user=self.user, name='John', surname='Doe', username='johndoe', email='john@example.com')
    
    def test_employee_account_creation(self):
        """Test that an employee account is created successfully."""
        self.assertEqual(self.employee.name, 'John')
        self.assertEqual(self.employee.surname, 'Doe')
        self.assertEqual(self.employee.user, self.user)
    
    def test_employee_account_string_representation(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.employee), 'johndoe')
    
    def test_employee_default_cognitive_scores(self):
        """Test that cognitive scores default to 0."""
        self.assertEqual(self.employee.target_analytical, 0)
        self.assertEqual(self.employee.target_practical, 0)
        self.assertEqual(self.employee.target_relational, 0)
        self.assertEqual(self.employee.target_experimental, 0)
    
    def test_employee_skills_list_field(self):
        """Test that skills_list field can store comma-separated skills."""
        self.employee.skills_list = 'python, java, sql'
        self.employee.save()
        self.assertEqual(self.employee.skills_list, 'python, java, sql')


class ValidateResumeTests(TestCase):
    """Test the resume validation function."""
    
    def test_validate_oversized_file(self):
        """Test that oversized files (>2MB) are rejected."""
        large_file = SimpleUploadedFile("large.pdf", b"x" * int(2.5 * 1024 * 1024), content_type="application/pdf")
        with self.assertRaises(ValidationError) as context:
            validate_pdf_resume(large_file)
        self.assertIn("too large", str(context.exception).lower())
    
    def test_validate_unsupported_file_type(self):
        """Test that unsupported file types are rejected."""
        unsupported_file = SimpleUploadedFile("resume.txt", b"Resume content", content_type="text/plain")
        unsupported_file.name = "resume.txt"
        with self.assertRaises(ValidationError) as context:
            validate_pdf_resume(unsupported_file)
        self.assertIn("Unsupported", str(context.exception))
    
    def test_validate_corrupted_pdf(self):
        """Test that corrupted PDFs are rejected."""
        corrupted_pdf = SimpleUploadedFile("corrupted.pdf", b"not a real pdf", content_type="application/pdf")
        with self.assertRaises(ValidationError) as context:
            validate_pdf_resume(corrupted_pdf)
        self.assertIn("corrupt", str(context.exception).lower())
    
    def test_validate_valid_pdf_size(self):
        """Test that valid PDF under 2MB is accepted."""
        valid_pdf = SimpleUploadedFile("valid.pdf", b"x" * (1 * 1024 * 1024), content_type="application/pdf")
        valid_pdf.size = 1 * 1024 * 1024
        # Should not raise
        try:
            validate_pdf_resume(valid_pdf)
        except ValidationError as e:
            # File integrity check might fail, which is ok for this test
            if "too large" in str(e).lower():
                self.fail("Valid file size should not raise 'too large' error")


class SkillsExtractionTests(TestCase):
    """Test the skills extraction function with mocking."""
    
    @patch('accounts.skills_extraction.model.generate_content')
    def test_extract_skills_success(self, mock_generate):
        """Test successful skills extraction."""
        mock_response = MagicMock()
        mock_response.text = "Python, Java, Project Management, SQL"
        mock_generate.return_value = mock_response
        
        skills = extract_skills_with_gemini("Resume text with python and java skills")
        self.assertIsInstance(skills, list)
        self.assertIn("python", skills)
        self.assertIn("java", skills)
    
    @patch('accounts.skills_extraction.model.generate_content')
    def test_extract_skills_with_various_separators(self, mock_generate):
        """Test skills extraction with different separators."""
        mock_response = MagicMock()
        mock_response.text = "Python\nJava;\nSQL, Project Management"
        mock_generate.return_value = mock_response
        
        skills = extract_skills_with_gemini("Resume text")
        self.assertGreaterEqual(len(skills), 3)
    
    @patch('accounts.skills_extraction.model.generate_content')
    def test_extract_skills_empty_response(self, mock_generate):
        """Test handling of empty Gemini response."""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_generate.return_value = mock_response
        
        with self.assertRaises(ValueError):
            extract_skills_with_gemini("Resume text")
    
    def test_extract_skills_empty_input(self):
        """Test handling of empty input text."""
        skills = extract_skills_with_gemini("")
        self.assertEqual(skills, [])
    
    @patch('accounts.skills_extraction.model.generate_content')
    def test_extract_skills_removes_duplicates(self, mock_generate):
        """Test that duplicate skills are removed."""
        mock_response = MagicMock()
        mock_response.text = "Python, Java, Python, SQL, Java"
        mock_generate.return_value = mock_response
        
        skills = extract_skills_with_gemini("Resume text")
        # Count occurrences of Python and Java
        python_count = sum(1 for s in skills if s == "python")
        java_count = sum(1 for s in skills if s == "java")
        self.assertEqual(python_count, 1)
        self.assertEqual(java_count, 1)
    
    @patch('accounts.skills_extraction.model.generate_content')
    def test_extract_skills_limit_to_50(self, mock_generate):
        """Test that skills are limited to 50."""
        mock_response = MagicMock()
        skills_text = ", ".join([f"Skill{i}" for i in range(100)])
        mock_response.text = skills_text
        mock_generate.return_value = mock_response
        
        skills = extract_skills_with_gemini("Resume text")
        self.assertLessEqual(len(skills), 50)


class ResumeUploadViewTests(TestCase):
    """Test the ResumeUploadView."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee = employee_account.objects.create(user=self.user, name='John', surname='Doe', username='johndoe', email='john@example.com')
        self.client.login(username='testuser', password='testpass123')
    
    def test_resume_upload_get(self):
        """Test GET request to upload page."""
        response = self.client.get('/accounts/upload/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/upload.html')
    
    def test_resume_upload_no_file(self):
        """Test upload with no file submitted."""
        response = self.client.post('/accounts/upload/', {})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No file uploaded', response.content)
    
    def test_resume_upload_invalid_pdf(self):
        """Test upload with invalid PDF file."""
        # Use a text file disguised as PDF
        invalid_pdf = SimpleUploadedFile("fake.pdf", b"This is not a PDF", content_type="application/pdf")
        response = self.client.post('/accounts/upload/', {'resume': invalid_pdf})
        # Should show error page (200) not redirect (302)
        self.assertEqual(response.status_code, 200)
        # Error should mention invalid PDF
        self.assertTrue(b'invalid' in response.content.lower() or b'corrupt' in response.content.lower() or b'failed' in response.content.lower())
    
    def test_resume_upload_not_logged_in(self):
        """Test that non-logged-in users cannot upload."""
        self.client.logout()
        response = self.client.get('/accounts/upload/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    @patch('accounts.skills_extraction.extract_skills_with_gemini')
    def test_resume_upload_api_failure(self, mock_extract):
        """Test handling of Gemini API failure."""
        mock_extract.side_effect = Exception("API key invalid")
        
        # Upload a file that will pass validation but fail at API call
        # Create a minimal valid DOCX
        from docx import Document as DocxDoc
        docx_file_obj = io.BytesIO()
        doc = DocxDoc()
        doc.add_paragraph("Sample resume text with Python and Java skills")
        doc.save(docx_file_obj)
        docx_file_obj.seek(0)
        
        resume_file = SimpleUploadedFile("resume.docx", docx_file_obj.getvalue(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        response = self.client.post('/accounts/upload/', {'resume': resume_file})
        self.assertEqual(response.status_code, 200)  # Error page
        # Check that error message appears in response
        self.assertTrue(b'Failed to extract skills' in response.content or b'API' in response.content)


class CreateEmployeeProfileTests(TestCase):
    """Test the create_employee_profile view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
    
    def test_create_profile_get(self):
        """Test GET request to profile creation."""
        response = self.client.get('/accounts/create-profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/create_profile.html')
    
    def test_create_profile_post_valid(self):
        """Test profile creation with valid data."""
        data = {
            'name': 'John',
            'surname': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'location': 'New York',
            'bio': 'Software Engineer'
        }
        response = self.client.post('/accounts/create-profile/', data)
        self.assertEqual(response.status_code, 302)  # Redirect to employee_profile


class TakeSurveyTests(TestCase):
    """Test the take_survey view and cognitive score calculation."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee = employee_account.objects.create(user=self.user, name='John', surname='Doe', username='johndoe', email='john@example.com')
        self.client.login(username='testuser', password='testpass123')
    
    def test_take_survey_get(self):
        """Test GET request to survey page."""
        response = self.client.get('/accounts/survey/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/take_survey.html')
    
    def test_take_survey_post_valid(self):
        """Test survey submission with valid data."""
        # Each question has 5 possible scores (1-5)
        data = {
            'q1': 1, 'q2': 1, 'q3': 1, 'q4': 1, 'q5': 1,  # Analytical: 1+1+1+1+1 = 5 * 4 = 20
            'q6': 2, 'q7': 2, 'q8': 2, 'q9': 2, 'q10': 2,  # Practical: 2+2+2+2+2 = 10 * 4 = 40
            'q11': 3, 'q12': 3, 'q13': 3, 'q14': 3, 'q15': 3,  # Relational: 3*5 = 15 * 4 = 60
            'q16': 4, 'q17': 4, 'q18': 4, 'q19': 4, 'q20': 4,  # Experimental: 4*5 = 20 * 4 = 80
        }
        response = self.client.post('/accounts/survey/', data)
        self.assertEqual(response.status_code, 302)  # Redirect to employee_profile
        
        # Verify scores were saved
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.target_analytical, 20)
        self.assertEqual(self.employee.target_practical, 40)
        self.assertEqual(self.employee.target_relational, 60)
        self.assertEqual(self.employee.target_experimental, 80)
    
    def test_survey_score_calculation_formula(self):
        """Test the cognitive score calculation formula."""
        # Formula: (q1 + q2 + q3 + q4 + q5) * 4
        # Max score per category: 5 * 5 * 4 = 100
        data = {
            'q1': 5, 'q2': 5, 'q3': 5, 'q4': 5, 'q5': 5,  # 25 * 4 = 100
            'q6': 5, 'q7': 5, 'q8': 5, 'q9': 5, 'q10': 5,  # 25 * 4 = 100
            'q11': 1, 'q12': 1, 'q13': 1, 'q14': 1, 'q15': 1,  # 5 * 4 = 20
            'q16': 1, 'q17': 1, 'q18': 1, 'q19': 1, 'q20': 1,  # 5 * 4 = 20
        }
        response = self.client.post('/accounts/survey/', data)
        
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.target_analytical, 100)
        self.assertEqual(self.employee.target_practical, 100)
        self.assertEqual(self.employee.target_relational, 20)
        self.assertEqual(self.employee.target_experimental, 20)

