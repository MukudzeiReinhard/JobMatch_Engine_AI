# Job Recommendation System Architecture

## System Overview

This repository implements a Django-based job recommendation platform with two main apps:
- `accounts`: employee profile management, resume upload, survey input, skill extraction, and job matching
- `jobs`: job creation, listing, candidate recommendations, and applications

The system includes:
- Django web frontend using templates under `templates/`
- SQLite database stored at `db.sqlite3`
- Resume storage in `media/resumes/`
- Gemini API integration for resume skill extraction via `accounts/skills_extraction.py`
- Celery task support for asynchronous logging (`accounts/tasks.py`) with Redis broker / result backend
- Security and authentication using Django auth plus `django-axes` for login rate limiting

## Architecture Diagram

```mermaid
flowchart LR
    subgraph WebApp[Web Application]
        A[User Browser]
        B[django.contrib.auth]
        C[accounts app]
        D[jobs app]
        E[Templates]
    end

    subgraph Data[Persistence]
        DB[SQLite DB]
        Media[Resume Files / media/resumes/]
    end

    subgraph External[External Services]
        Gemini[Gemini API]
        Redis[Redis Broker/Backend]
    end

    A -->|HTTP Requests| WebApp
    WebApp -->|render pages| E
    C -->|profile, upload, survey, match, apply| DB
    D -->|job and application data| DB
    C -->|resume file save| Media
    C -->|skill extraction request| Gemini
    WebApp -->|login/auth| B
    C -->|async log_event.delay| Redis
    Redis -->|task queue| C

    style WebApp fill:#f5f5ff,stroke:#4444aa,stroke-width:1px
    style Data fill:#f5fff5,stroke:#44aa44,stroke-width:1px
    style External fill:#fff5f5,stroke:#aa4444,stroke-width:1px
```

## System Overview Diagram

```mermaid
flowchart TD
    subgraph UserFlows[User Flows]
        U1[Visitor / Candidate]
        U2[HR / Recruiter]
    end

    U1 -->|signup/login| SignUp[Signup / Login]
    SignUp --> Profile[Create / Edit Profile]
    Profile -->|upload resume| ResumeUpload[Resume Upload]
    Profile -->|take survey| Survey[Survey Form]
    ResumeUpload -->|extract skills| Gemini[Gemini API]
    Survey -->|save cognitive scores| DB[SQLite]
    Profile -->|view| EmployeeDashboard[Employee Profile]
    EmployeeDashboard -->|view best matches| MatchResults[Job Matching]
    MatchResults -->|apply| Apply[Submit Application]
    Apply -->|persist| Applications[JobApplications]

    U2 -->|login| HRDashboard[HR Dashboard]
    HRDashboard -->|create job| CreateJob[Job Creation]
    CreateJob -->|persist| Jobs[Job]
    HRDashboard -->|view candidates| PotentialCandidates[Potential Candidate List]
    PotentialCandidates -->|read scores| Compatibility[JobEmployeeCompatibility]
    HRDashboard -->|view applications| ApplicationReview[Job Applications]

    ResumeUpload -->|store file| Media[Resume Files]
    Gemini -->|return skills| Profile
    Jobs -->|requirements| MatchResults
    DB -->|stores| Profile
    DB -->|stores| Jobs
    DB -->|stores| Compatibility
    DB -->|stores| Applications
    DB -->|stores| Skills

    style UserFlows fill:#eeeeff,stroke:#9999ff,stroke-width:1px
    style DB fill:#f5fff5,stroke:#44aa44
    style Media fill:#fff7e6,stroke:#cc9900
    style Gemini fill:#ffeeee,stroke:#dd4444
```

## Key Components

- `accounts/models.py`
  - `employee_account`: stores candidate and HR profiles, resume metadata, extracted skills, cognitive scores
- `jobs/models.py`
  - `Job`: job postings with required skills and cognitive target scores
  - `JobSkillRequirement`: job-specific skill importance weights
  - `JobEmployeeCompatibility`: computed match score per employee-job pair
  - `JobApplications`: candidate applications for jobs
- `accounts/views.py`
  - handles signup, profile management, resume upload, skill extraction, survey input, job matching, apply-to-job, and secure resume download
- `jobs/views.py`
  - handles job listing, job creation, HR candidate recommendations, and application viewing
- `accounts/skills_extraction.py`
  - anonymizes resume text and calls Gemini API to extract structured skill lists
- `mysite/settings.py`
  - configures database, static/media, Celery/Redis, and login security

## Notes

- Current task queue support is limited to `log_event` and demo logging, but the architecture already supports asynchronous Celery workflows.
- The matching engine in `accounts/views.py` combines skill coverage and cognitive score distance into a compound compatibility score.
- Resume files are stored under `media/resumes/` and served through `SecureResumeDownloadView` with owner/HR authorization.

---

# Simplified Operations & Workflows

## Candidate Operations Flow

This diagram shows the core candidate journey from signup through to receiving ranked job matches.

```mermaid
flowchart LR
    A[Candidate Sign Up] --> B[Upload CV/Resume]
    B -->|Gemini API| C[Extract Skills]
    C --> D[Skills Stored]
    D --> E[Complete Survey]
    E -->|Cognitive Scores| F[Scores Stored]
    F --> G[Trigger Matching Algorithm]
    G -->|Compute Score| H[Calculate Compatibility]
    H --> I[Ranked Job Results]
    I --> J[View Matches]
    J --> K{Apply?}
    K -->|Yes| L[Submit Application]
    K -->|No| J
    
    style A fill:#e1f5ff,stroke:#01579b
    style B fill:#e1f5ff,stroke:#01579b
    style C fill:#fff3e0,stroke:#e65100
    style D fill:#f5f5f5,stroke:#424242
    style E fill:#e1f5ff,stroke:#01579b
    style F fill:#f5f5f5,stroke:#424242
    style G fill:#fff3e0,stroke:#e65100
    style H fill:#fff3e0,stroke:#e65100
    style I fill:#c8e6c9,stroke:#2e7d32
    style J fill:#e1f5ff,stroke:#01579b
    style L fill:#f3e5f5,stroke:#512da8
```

## HR Recruiter Operations Flow

This diagram shows the HR recruiter workflow for job management and candidate review.

```mermaid
flowchart LR
    A[HR Login] --> B[Create Job Posting]
    B -->|Define Skills| C[Job Stored]
    C --> D{View Candidates?}
    D -->|Potential Candidates| E[See Top Ranked Candidates]
    D -->|Applications| F[View Job Applications]
    E --> G[Download Candidate Resume]
    F --> H[Review Applicant Profiles]
    E --> I[Filter by Match Score]
    F --> J[Accept or Reject]
    G --> K[End Recruitment Step]
    H --> K
    I --> K
    J --> K
    
    style A fill:#c8e6c9,stroke:#2e7d32
    style B fill:#c8e6c9,stroke:#2e7d32
    style C fill:#f5f5f5,stroke:#424242
    style D fill:#fff9c4,stroke:#f57f17
    style E fill:#f8bbd0,stroke:#c2185b
    style F fill:#f8bbd0,stroke:#c2185b
    style G fill:#e1f5ff,stroke:#01579b
    style H fill:#e1f5ff,stroke:#01579b
    style I fill:#e1f5ff,stroke:#01579b
    style J fill:#c8e6c9,stroke:#2e7d32
    style K fill:#bdbdbd,stroke:#424242
```

## Combined System Operations

This diagram shows both candidate and HR operations interacting through the recommendation system.

```mermaid
flowchart TD
    subgraph Candidate["CANDIDATE JOURNEY"]
        C1[Signup and Login]
        C2[Upload Resume]
        C3[System Extracts Skills via Gemini API]
        C4[Complete Survey Cognitive Scores]
        C5[System Computes Match]
        C6[View Ranked Jobs]
        C7[Apply for Job]
        
        C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> C7
    end
    
    subgraph System["MATCHING ENGINE"]
        M1["Candidate Profile"]
        M2["Job Requirements"]
        M3["Calculate Compatibility"]
        M4["Store in Database"]
        
        M1 --> M3
        M2 --> M3
        M3 --> M4
    end
    
    subgraph HR["HR RECRUITER JOURNEY"]
        H1[Login to Dashboard]
        H2[Create Job Posting]
        H3[View Potential Candidates]
        H4[Review Applications]
        H5[Download Resumes]
        H6[Make Hiring Decisions]
        
        H1 --> H2 --> H3 --> H4 --> H5 --> H6
    end
    
    C5 -.->|Stores Candidate Data| M1
    C2 -.->|Stores Job Requirements| M2
    M4 -.->|Ranked Results| C6
    M4 -.->|Top Candidates| H3
    C7 -.->|Application| H4
    
    style Candidate fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style HR fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style System fill:#fff3e0,stroke:#e65100,stroke-width:2px
