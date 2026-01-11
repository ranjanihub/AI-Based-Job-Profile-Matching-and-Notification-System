# AI-Based Job Profile Matching and Notification System

## Project Description

The AI-Based Job Profile Matching and Notification System is a web-based application developed to assist job seekers in identifying suitable employment opportunities by intelligently matching their professional profiles with job descriptions. The system aims to reduce the inefficiency of manual job searching by evaluating the relevance of a candidate’s resume to job requirements using Natural Language Processing (NLP) techniques.

Users upload their resumes in PDF format and provide profile information such as skills, educational qualifications, and work experience. The backend of the system is implemented using Python with FastAPI, which handles resume parsing, text preprocessing, and similarity computation. Resume and job description texts are processed using NLP techniques such as tokenization, stop-word removal, and normalization. The processed texts are transformed into numerical vectors using the Term Frequency–Inverse Document Frequency (TF-IDF) algorithm.

To determine how closely a user’s profile matches a job description, Cosine Similarity is applied to the TF-IDF vectors, generating a similarity score that represents the match percentage. A weighted scoring mechanism is used to consider multiple factors, including skill relevance, experience alignment, and educational background. When the computed match percentage exceeds a predefined threshold (for example, 70%), the system automatically generates a notification for the user.

The frontend of the application is developed using Streamlit, providing an interactive dashboard where users can upload resumes, view matched job listings, analyze match scores, and receive notifications. Supabase, a Backend-as-a-Service platform built on PostgreSQL, is used for database management, user authentication, and secure storage of resume files. Supabase Authentication handles user login using JWT-based security, while Supabase Storage is utilized for managing uploaded documents.

For ethical and compliance purposes, the system does not automate job applications. Instead, users are redirected to official company career pages or authorized job portals to complete the application process manually. The application also includes a scheduled background process that periodically evaluates new job descriptions and notifies users when high-matching opportunities are identified.

This project demonstrates the effective use of TF-IDF and Cosine Similarity for text-based matching and showcases how modern web technologies and cloud-based backend services can be integrated to build an intelligent and scalable recruitment support system.

## Product Specification (Step 1)

### User Stories
- As a job seeker, I want to upload my resume (PDF) so that the system can analyze my profile.
- As a job seeker, I want to view a list of job matches with scores so that I can see relevant opportunities.
- As a job seeker, I want to receive email notifications when a new job matches my profile above 70% so that I don't miss opportunities.
- As a job seeker, I want to see an in-app notification feed of recent matches so that I can quickly access them.
- As an admin, I want to add new job descriptions manually so that the system has jobs to match against.

### Matching Inputs and Outputs
- **Inputs**: Resume text (extracted from PDF), Job description text (provided by admin).
- **Outputs**: Similarity score (0-100%), Top 5 matching terms/skills, Weighted breakdown (skills, experience, education).

### Scoring Formula
- Weighted composite score:
  - Skills relevance: 50% (based on TF-IDF cosine similarity on skills section)
  - Experience alignment: 30% (based on years of experience match)
  - Education background: 20% (based on degree level match)
- Overall score = (skills_score * 0.5) + (experience_score * 0.3) + (education_score * 0.2)

### Notification Threshold and Rules
- Threshold: 70% match score triggers notification.
- Rules:
  - Email notification sent immediately when match > 70%.
  - In-app notification added to user's feed.
  - No duplicates: Only notify once per user-job pair.
  - User can unsubscribe from emails in settings.

### Acceptance Criteria for Step 1
- README.md updated with above spec.
- Spec reviewed and approved before proceeding to Step 2.

## Supabase Setup (Step 2)

### Prerequisites
- Supabase project created at [supabase.com](https://supabase.com).
- Project URL: https://yxzktdpivgxcfeghhqsv.supabase.co
- Authentication: Email/password enabled in Dashboard > Authentication > Settings.

### Environment Variables
Create a `.env` file in the backend/ directory with:
```
SUPABASE_URL=https://yxzktdpivgxcfeghhqsv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4emt0ZHBpdmd4Y2ZlZ2hocXN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxMjg3NzEsImV4cCI6MjA4MzcwNDc3MX0.LtFK19MYCqtlEti4kjDHZHslaBkd_7eTeX_U4Q4rmd0
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4emt0ZHBpdmd4Y2ZlZ2hocXN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxMjg3NzEsImV4cCI6MjA4MzcwNDc3MX0.LtFK19MYCqtlEti4kjDHZHslaBkd_7eTeX_U4Q4rmd0
```

**Security Note**: Never commit `.env` to git. Add it to `.gitignore`.

### Database Schema
Run the following SQL in Supabase Dashboard > SQL Editor:

```sql
-- Enable UUID extension if not already
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    text_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    skills TEXT[], -- Array of skills
    experience_years INTEGER,
    education_level TEXT, -- e.g., 'Bachelor', 'Master'
    location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Matches table
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    top_terms TEXT[], -- Top matching terms
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, resume_id, job_id) -- Prevent duplicate matches
);

-- Notifications table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('email', 'in_app')),
    sent_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Row Level Security (RLS) Policies
Enable RLS on all tables and add policies:

```sql
-- Enable RLS
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Resumes: Users can only access their own
CREATE POLICY "Users can view own resumes" ON resumes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own resumes" ON resumes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own resumes" ON resumes FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own resumes" ON resumes FOR DELETE USING (auth.uid() = user_id);

-- Jobs: Public read, authenticated insert/update/delete (for admins)
CREATE POLICY "Anyone can view jobs" ON jobs FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert jobs" ON jobs FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can update jobs" ON jobs FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can delete jobs" ON jobs FOR DELETE USING (auth.role() = 'authenticated');

-- Matches: Users can only access their own
CREATE POLICY "Users can view own matches" ON matches FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own matches" ON matches FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Notifications: Users can only access their own
CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own notifications" ON notifications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);
```

### Storage Buckets
In Supabase Dashboard > Storage:
- Create bucket "resumes": Public read, authenticated write.
- Create bucket "jobs": Public read, authenticated write.

### Local Development
- Install Supabase CLI: `npm install -g supabase`
- Link project: `supabase link --project-ref yxzktdpivgxcfeghhqsv`
- Start local: `supabase start`

### Acceptance Criteria for Step 2
- Supabase project configured with schema, RLS, and storage.
- .env file created with provided keys.
- Local Supabase setup tested.

## Backend Setup (Step 3)

### Prerequisites
- Python 3.9+
- Install dependencies: `cd backend && pip install -e .`

### Running the Application
- Backend: `cd backend && uvicorn app.main:app --reload` (http://localhost:8000)
- Frontend: `cd backend && streamlit run streamlit_app.py` (http://localhost:8501)

### Streamlit Frontend Setup (Step 3)

### Prerequisites
- Python 3.9+
- Install dependencies: `cd backend && pip install -e .`

### Running the Frontend
- `cd backend && streamlit run streamlit_app.py`
- Open the provided URL (usually http://localhost:8501)

### Acceptance Criteria for Step 3
- Backend API running with health, resume upload, jobs CRUD.
- Streamlit app with login and basic dashboard.
- Resume upload extracts text and saves to Supabase.

## Step 4: Core Data Ingestion + NLP Matching v1

### Prerequisites
- Supabase schema created and RLS policies applied.
- Backend and Streamlit app running.

### Features Implemented
- PDF text extraction with preprocessing (lowercase, punctuation removal, stopword removal).
- TF-IDF vectorization fitted on job descriptions.
- Cosine similarity computation between resume and job vectors.
- Weighted scoring: Skills (50%), Experience (30%), Education (20%).
- Match endpoint: POST /api/v1/matches computes and saves matches above 70% threshold.
- Streamlit app: Upload resume, compute matches, display results.

### Testing
- Upload a PDF resume.
- Create jobs via API or manually.
- Compute matches and view scores.

### Acceptance Criteria for Step 4
- Resume preprocessing works.
- TF-IDF and cosine similarity compute scores.
- Weighted scoring applied.
- Matches saved to DB and displayed in Streamlit app.

## Step 5: Notifications + Scheduling

### Prerequisites
- Steps 1-4 completed.
- Supabase notifications table created.

### Features Implemented
- In-app notifications: Stored in DB when match > 70%, displayed in dashboard.
- Email notifications: Mock send function (integrate with Resend/SendGrid in production).
- Periodic re-scoring: APScheduler runs daily to check new jobs against all resumes.
- Background scheduler: Starts on app startup, runs async tasks.

### Testing
- Upload resume and compute matches to trigger notifications.
- Check dashboard for in-app notifications.
- Scheduler runs periodically (or trigger manually for testing).

### Acceptance Criteria for Step 5
- Notifications created on matches.
- In-app feed shows notifications.
- Email mock logs sent messages.
- Scheduler runs periodic tasks.

## Step 6: Security/Quality Hardening

### Prerequisites
- Steps 1-5 completed.

### Features Implemented
- Input validation: File type and size checks for uploads.
- Rate limiting: 5 uploads per minute using SlowAPI.
- Logging: Basic logging for match scores.
- Error handling: Try-catch in Streamlit app for better UX.
- Basic tests: Health and jobs endpoints tested with pytest.

### Testing
- Run `pytest` in backend/ to execute tests.
- Try uploading invalid files or exceeding rate limits.
- Check logs for match computations.

### Acceptance Criteria for Step 6
- Input validation prevents bad uploads.
- Rate limiting enforced.
- Tests pass.
- Errors handled gracefully.
