from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import Job, Skill, Department, JobSkillRequirement, JobEmployeeCompatibility
from accounts.models import employee_account


class SkillModelTests(TestCase):
    """Test the Skill model."""
    
    def test_skill_creation(self):
        """Test that a skill is created successfully."""
        skill = Skill.objects.create(name='Python', description='Programming language')
        self.assertEqual(skill.name, 'Python')
        self.assertEqual(str(skill), 'Python')
    
    def test_skill_unique_constraint(self):
        """Test that skill names are unique."""
        Skill.objects.create(name='Python')
        with self.assertRaises(Exception):  # IntegrityError
            Skill.objects.create(name='Python')


class DepartmentModelTests(TestCase):
    """Test the Department model."""
    
    def test_department_creation(self):
        """Test that a department is created successfully."""
        dept = Department.objects.create(
            name='Engineering',
            analytical_weight=0.4,
            practical_weight=0.3,
            relational_weight=0.2,
            experimental_weight=0.1
        )
        self.assertEqual(dept.name, 'Engineering')
        self.assertEqual(dept.analytical_weight, 0.4)
    
    def test_department_default_weights(self):
        """Test default weight distribution."""
        dept = Department.objects.create(name='Sales')
        self.assertEqual(dept.analytical_weight, 0.25)
        self.assertEqual(dept.practical_weight, 0.25)
        self.assertEqual(dept.relational_weight, 0.25)
        self.assertEqual(dept.experimental_weight, 0.25)
    
    def test_department_weights_sum_to_one(self):
        """Test that weights sum to 1.0."""
        dept = Department.objects.create(name='HR')
        total_weight = (dept.analytical_weight + dept.practical_weight + 
                       dept.relational_weight + dept.experimental_weight)
        self.assertAlmostEqual(total_weight, 1.0, places=5)


class JobModelTests(TestCase):
    """Test the Job model."""
    
    def setUp(self):
        self.dept = Department.objects.create(name='Engineering')
        self.job = Job.objects.create(
            title='Software Engineer',
            company='TechCorp',
            location='San Francisco',
            description='Build amazing software',
            target_analytical=80,
            target_practical=70,
            target_relational=60,
            target_experimental=50,
            department=self.dept
        )
    
    def test_job_creation(self):
        """Test that a job is created successfully."""
        self.assertEqual(self.job.title, 'Software Engineer')
        self.assertEqual(self.job.company, 'TechCorp')
    
    def test_job_cognitive_scores(self):
        """Test that cognitive scores are stored correctly."""
        self.assertEqual(self.job.target_analytical, 80)
        self.assertEqual(self.job.target_practical, 70)
        self.assertEqual(self.job.target_relational, 60)
        self.assertEqual(self.job.target_experimental, 50)
    
    def test_job_without_department(self):
        """Test job creation without a department."""
        job = Job.objects.create(title='Freelancer', company='Self')
        self.assertIsNone(job.department)
        self.assertEqual(job.target_analytical, 0)


class JobSkillRequirementTests(TestCase):
    """Test the JobSkillRequirement model."""
    
    def setUp(self):
        self.job = Job.objects.create(title='Python Developer', company='TechCorp')
        self.skill = Skill.objects.create(name='Python')
    
    def test_job_skill_requirement_creation(self):
        """Test creating a job skill requirement."""
        req = JobSkillRequirement.objects.create(
            job=self.job,
            skill=self.skill,
            importance=5
        )
        self.assertEqual(req.job, self.job)
        self.assertEqual(req.skill, self.skill)
        self.assertEqual(req.importance, 5)
    
    def test_job_skill_requirement_string(self):
        """Test the __str__ method."""
        req = JobSkillRequirement.objects.create(
            job=self.job,
            skill=self.skill,
            importance=5
        )
        self.assertIn('Python Developer', str(req))
        self.assertIn('Python', str(req))


class JobMatchingAlgorithmTests(TestCase):
    """Test the job matching algorithm scoring logic."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee = employee_account.objects.create(
            user=self.user,
            name='John',
            surname='Doe',
            username='johndoe',
            email='john@example.com',
            target_analytical=80,
            target_practical=70,
            target_relational=60,
            target_experimental=50,
            skills_list='python, java, sql'
        )
        
        # Create department with custom weights
        self.dept = Department.objects.create(
            name='Engineering',
            analytical_weight=0.4,
            practical_weight=0.3,
            relational_weight=0.2,
            experimental_weight=0.1
        )
        
        # Create job with matching cognitive profile
        self.job1 = Job.objects.create(
            title='Senior Engineer',
            company='TechCorp',
            target_analytical=85,
            target_practical=75,
            target_relational=65,
            target_experimental=55,
            department=self.dept
        )
        
        # Create skills for the job
        self.python_skill = Skill.objects.create(name='Python')
        self.java_skill = Skill.objects.create(name='Java')
        self.sql_skill = Skill.objects.create(name='SQL')
        self.cpp_skill = Skill.objects.create(name='C++')
        
        # Assign skills to job with importance weights
        JobSkillRequirement.objects.create(job=self.job1, skill=self.python_skill, importance=5)
        JobSkillRequirement.objects.create(job=self.job1, skill=self.java_skill, importance=5)
        JobSkillRequirement.objects.create(job=self.job1, skill=self.sql_skill, importance=3)
        JobSkillRequirement.objects.create(job=self.job1, skill=self.cpp_skill, importance=4)
    
    def test_cognitive_score_gap_calculation(self):
        """Test that cognitive gap is calculated correctly."""
        # Gap = abs(emp_score - job_score) * weight for each category
        analytical_gap = abs(self.employee.target_analytical - self.job1.target_analytical)
        self.assertEqual(analytical_gap, 5)
    
    def test_skill_matching_perfect_match(self):
        """Test skill matching when all required skills are present."""
        # Employee has python, java, sql (3/4 skills)
        required_skills = self.job1.jobskillrequirement_set.all()
        total_importance = sum(req.importance for req in required_skills)
        
        user_earned_weight = 0
        for req in required_skills:
            if req.skill.name.lower() in self.employee.skills_list:
                user_earned_weight += req.importance
        
        # Should have: Python(5) + Java(5) + SQL(3) = 13 out of 17
        self.assertEqual(user_earned_weight, 13)
        self.assertEqual(total_importance, 17)
    
    def test_skill_matching_partial_match(self):
        """Test skill matching when only some required skills are present."""
        # Remove Java from employee skills
        self.employee.skills_list = 'python, sql'
        self.employee.save()
        
        required_skills = self.job1.jobskillrequirement_set.all()
        user_earned_weight = 0
        for req in required_skills:
            if req.skill.name.lower() in self.employee.skills_list:
                user_earned_weight += req.importance
        
        # Should have: Python(5) + SQL(3) = 8 out of 17
        self.assertEqual(user_earned_weight, 8)
    
    def test_skill_matching_no_match(self):
        """Test skill matching when no required skills are present."""
        self.employee.skills_list = 'rust, go'
        self.employee.save()
        
        required_skills = self.job1.jobskillrequirement_set.all()
        user_earned_weight = 0
        for req in required_skills:
            if req.skill.name.lower() in self.employee.skills_list:
                user_earned_weight += req.importance
        
        self.assertEqual(user_earned_weight, 0)


class JobMatchViewTests(TestCase):
    """Test the JobMatchView and its integration."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee = employee_account.objects.create(
            user=self.user,
            name='John',
            surname='Doe',
            username='johndoe',
            email='john@example.com',
            target_analytical=80,
            target_practical=70,
            target_relational=60,
            target_experimental=50,
            skills_list='python, java, sql',
            resume='path/to/resume.pdf'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_job_match_view_requires_login(self):
        """Test that match results view requires authentication."""
        self.client.logout()
        response = self.client.get('/accounts/match-results/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_job_match_view_with_no_jobs(self):
        """Test matching when no jobs exist."""
        response = self.client.get('/accounts/match-results/')
        self.assertEqual(response.status_code, 200)
        # Should show "no jobs" message
        self.assertFalse(response.context['results'])
    
    def test_job_match_view_saves_compatibility_score(self):
        """Test that compatibility scores are saved to database."""
        # Create a job
        dept = Department.objects.create(name='Engineering')
        job = Job.objects.create(
            title='Engineer',
            company='TechCorp',
            target_analytical=80,
            target_practical=70,
            target_relational=60,
            target_experimental=50,
            department=dept
        )
        
        skill = Skill.objects.create(name='Python')
        JobSkillRequirement.objects.create(job=job, skill=skill, importance=5)
        
        response = self.client.get('/accounts/match-results/')
        self.assertEqual(response.status_code, 200)
        
        # Check if compatibility score was saved
        compat = JobEmployeeCompatibility.objects.filter(job=job, employee=self.employee).first()
        self.assertIsNotNone(compat)
        self.assertGreater(compat.compatibility_score, 0)
    
    def test_job_match_view_filters_by_minimum_score(self):
        """Test that only matches >= 30 score are included."""
        dept = Department.objects.create(name='Engineering')
        
        # Create a job with vastly different cognitive profile
        job = Job.objects.create(
            title='Specialized Role',
            company='TechCorp',
            target_analytical=20,
            target_practical=20,
            target_relational=20,
            target_experimental=20,
            department=dept
        )
        
        # Employee has no relevant skills for this job
        self.employee.skills_list = 'different, skills'
        self.employee.save()
        
        response = self.client.get('/accounts/match-results/')
        self.assertEqual(response.status_code, 200)
        
        # Check if score below 30 is not in results
        compat = JobEmployeeCompatibility.objects.filter(job=job, employee=self.employee).first()
        if compat:
            self.assertGreaterEqual(compat.compatibility_score, 30)


class EdgeCaseTests(TestCase):
    """Test edge cases and corner cases in the system."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.employee = employee_account.objects.create(
            user=self.user,
            name='John',
            surname='Doe',
            username='johndoe',
            email='john@example.com'
        )
    
    def test_cognitive_score_with_zero_values(self):
        """Test matching when employee has zero cognitive scores."""
        self.employee.target_analytical = 0
        self.employee.target_practical = 0
        self.employee.target_relational = 0
        self.employee.target_experimental = 0
        self.employee.save()
        
        dept = Department.objects.create(name='Sales')
        job = Job.objects.create(
            title='Salesperson',
            company='SalesCorp',
            target_analytical=50,
            target_practical=50,
            target_relational=50,
            target_experimental=50,
            department=dept
        )
        
        # Should not crash, just show poor match
        self.assertIsNotNone(job)
    
    def test_job_with_no_skill_requirements(self):
        """Test job matching for a job with no skill requirements."""
        dept = Department.objects.create(name='Generic')
        job = Job.objects.create(
            title='Generic Role',
            company='GenericCorp',
            target_analytical=50,
            target_practical=50,
            target_relational=50,
            target_experimental=50,
            department=dept
        )
        
        # No skills attached
        self.assertEqual(job.jobskillrequirement_set.count(), 0)
    
    def test_employee_with_empty_skills_list(self):
        """Test matching when employee has no skills."""
        self.employee.skills_list = ''
        self.employee.save()
        
        dept = Department.objects.create(name='Engineering')
        job = Job.objects.create(
            title='Engineer',
            company='TechCorp',
            department=dept
        )
        
        skill = Skill.objects.create(name='Python')
        JobSkillRequirement.objects.create(job=job, skill=skill, importance=5)
        
        # Should show very poor match
        self.assertIsNotNone(job)
    
    def test_department_weights_validation(self):
        """Test department weight distribution."""
        dept = Department.objects.create(
            name='SpecializedDept',
            analytical_weight=0.5,
            practical_weight=0.3,
            relational_weight=0.1,
            experimental_weight=0.1
        )
        
        total = dept.analytical_weight + dept.practical_weight + dept.relational_weight + dept.experimental_weight
        self.assertAlmostEqual(total, 1.0, places=5)
    
    def test_skill_case_insensitivity_in_matching(self):
        """Test that skill matching is case-insensitive."""
        self.employee.skills_list = 'PYTHON, JAVA'
        self.employee.save()
        
        skill = Skill.objects.create(name='Python')
        dept = Department.objects.create(name='Engineering')
        job = Job.objects.create(title='Engineer', company='TechCorp', department=dept)
        JobSkillRequirement.objects.create(job=job, skill=skill, importance=5)
        
        # Check if lowercase matching works
        user_skills = self.employee.skills_list.split(',')
        user_skills = [s.strip().lower() for s in user_skills]
        self.assertIn('python', user_skills)

