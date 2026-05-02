import streamlit as st
import pdfplumber
import re
from groq import Groq

# -----------------------------
# API KEY
# -----------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide",
    page_icon="📄"
)

# -----------------------------
# CSS STYLING
# -----------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{
    background-color:white;
}
/* Main buttons */
.stButton > button {
    background-color: black !important;
    color: white !important;
    border: none !important;
}

.stButton > button * {
    color: white !important;
}

/* Link buttons (LinkedIn / Naukri) */
a[data-testid="stLinkButton"] {
    background-color: black !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 10px 18px !important;
    text-decoration: none !important;
    font-weight: 600 !important;
}

a[data-testid="stLinkButton"] * {
    color: white !important;
}

/* File uploader dark area text */
[data-testid="stFileUploader"] {
    background-color: #1e1e1e !important;
    color: white !important;
}

[data-testid="stFileUploader"] * {
    color: white !important;
}

/* Browse files button inside uploader */
[data-testid="stFileUploader"] button {
    background-color: black !important;
    color: white !important;
    border: none !important;
}

[data-testid="stFileUploader"] button * {
    color: white !important;
}
.main .block-container{
    max-width:1050px;
    padding-top:3rem;
    padding-bottom:3rem;
}
/* Force all normal text black */
html, body, [class*="css"] {
    color: black !important;
}

/* Main content text */
p, span, label, div, li, h1, h2, h3, h4, h5, h6 {
    color: black !important;
}

/* Inputs */
input, textarea {
    color: black !important;
    background-color: white !important;
}

/* Placeholder text */
input::placeholder,
textarea::placeholder {
    color: #666666 !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: black !important;
}
.main-title{
    font-size:42px;
    font-weight:700;
    text-align:center;
    color:black;
    margin-bottom:10px;
}

.subtitle{
    text-align:center;
    color:black;
    margin-bottom:40px;
    font-size:16px;
}

.section-title{
    font-size:22px;
    font-weight:600;
    color:black;
    margin-top:20px;
    margin-bottom:15px;
}

.input-label{
    font-weight:600;
    color:black;
    margin-bottom:6px;
}

.stTextInput input,
.stTextArea textarea{
    border-radius:6px;
    border:1px solid #cccccc;
    color:black;
    background:white;
}

.stButton > button{
    background:black !important;
    color:white !important;
    border:none;
    border-radius:6px;
    padding:10px 22px;
    font-weight:600;
}

.stButton > button:hover{
    background:#222 !important;
}

hr{
    border:none;
    border-top:1px solid #dddddd;
    margin:30px 0;
}

p,h1,h2,h3,h4,span,label{
    color:black !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">AI Resume & Job Matcher</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Professional ATS-based resume analysis and smart job recommendations</div>',
    unsafe_allow_html=True
)

# -----------------------------
# INPUT SECTION
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Candidate Information</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-label">Full Name</div>', unsafe_allow_html=True)
    name = st.text_input("", key="name", label_visibility="collapsed")

    st.markdown('<div class="input-label">Email Address</div>', unsafe_allow_html=True)
    email = st.text_input("", key="email", label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-title">Resume Upload</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-label">Upload Resume (PDF)</div>', unsafe_allow_html=True)
    file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

st.markdown('<div class="section-title">Job Description</div>', unsafe_allow_html=True)

job_description = st.text_area(
    "",
    height=220,
    placeholder="Paste job description here...",
    label_visibility="collapsed"
)

analyze = st.button("Analyze Resume")

st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------
# MAIN LOGIC
# -----------------------------
if analyze:

    if not name or not email:
        st.warning("Please enter your name and email.")

    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.warning("Please enter a valid email address.")

    elif file is None:
        st.warning("Please upload your resume.")

    elif job_description.strip() == "":
        st.warning("Please paste a job description.")

    else:

        # -----------------------------
        # EXTRACT PDF TEXT
        # -----------------------------
        resume_text = ""

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    resume_text += text + "\n"

        # -----------------------------
        # AI PROMPT
        # -----------------------------
        prompt = f"""
You are an advanced ATS system and professional HR evaluator.

Analyze the resume against the job description fairly and realistically.

IMPORTANT RULES:
- Evaluate based on the candidate's likely experience level.
- If the resume belongs to a student or fresher, score fairly for entry-level opportunities.
- Do NOT compare freshers with senior professionals.
- Avoid unnecessarily harsh scoring.
- Strong fresher resumes can score 70+.
- Use realistic and balanced judgement.

Return output strictly in this format:

SUMMARY:
STRENGTHS:
WEAKNESSES:
RESUME_SCORE:
JOB_MATCH_PERCENTAGE:
MISSING_SKILLS:
IMPROVEMENT_SUGGESTIONS:

Resume:
{resume_text}

Job Description:
{job_description}
"""

        # -----------------------------
        # AI RESPONSE
        # -----------------------------
        with st.spinner("Analyzing resume..."):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result = response.choices[0].message.content

        # -----------------------------
        # SCORE EXTRACTION
        # -----------------------------
        resume_score = re.search(r"RESUME[\s_]*SCORE[^0-9]*(\d+)", result, re.IGNORECASE)
        match_score = re.search(r"JOB[\s_]*MATCH[\s_]*PERCENTAGE[^0-9]*(\d+)", result, re.IGNORECASE)

        st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)

        colA, colB = st.columns(2)

        if resume_score:
            with colA:
                val = int(resume_score.group(1))
                st.markdown("### Resume Score")
                st.progress(val / 100)
                st.write(f"{val}/100")

        if match_score:
            with colB:
                val = int(match_score.group(1))
                st.markdown("### Job Match")
                st.progress(val / 100)
                st.write(f"{val}%")

        st.markdown("<hr>", unsafe_allow_html=True)

        # -----------------------------
        # JOB RECOMMENDATIONS
        # -----------------------------
        combined_text = (resume_text + " " + job_description).lower()

        recommended_jobs = []

        if "python" in combined_text and ("machine learning" in combined_text or "ml" in combined_text):
            recommended_jobs.append("AI/ML Intern")

        if "python" in combined_text and "sql" in combined_text:
            recommended_jobs.append("Data Analyst Intern")

        if "python" in combined_text:
            recommended_jobs.append("Python Developer Intern")

        if "excel" in combined_text or "power bi" in combined_text:
            recommended_jobs.append("Business Analyst Intern")

        if "java" in combined_text:
            recommended_jobs.append("Software Engineer Intern")

        if "deep learning" in combined_text:
            recommended_jobs.append("Computer Vision / NLP Intern")

        if len(recommended_jobs) == 0:
            recommended_jobs.append("General Internship Opportunities")

        recommended_jobs = list(dict.fromkeys(recommended_jobs))

        st.markdown('<div class="section-title">💼 Recommended Jobs</div>', unsafe_allow_html=True)

        for job in recommended_jobs:

            st.success(job)

            linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={job.replace(' ', '%20')}"
            naukri_url = f"https://www.naukri.com/{job.replace(' ', '-').lower()}-jobs"

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <a href="{linkedin_url}" target="_blank">
                        <button style="
                            background:black;
                            color:white;
                            border:none;
                            padding:10px 18px;
                            border-radius:8px;
                            font-weight:600;
                            cursor:pointer;
                            width:100%;">
                            🔗 LinkedIn Jobs
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <a href="{naukri_url}" target="_blank">
                        <button style="
                            background:black;
                            color:white;
                            border:none;
                            padding:10px 18px;
                            border-radius:8px;
                            font-weight:600;
                            cursor:pointer;
                            width:100%;">
                            🔗 Naukri Jobs
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

            st.write("")
        st.markdown("<hr>", unsafe_allow_html=True)

        # -----------------------------
        # AI ANALYSIS
        # -----------------------------
        st.markdown('<div class="section-title">Detailed AI Analysis</div>', unsafe_allow_html=True)

        st.markdown(
    f"""
    <div style="color:black; background:white; padding:15px; border-radius:8px;">
        <pre style="white-space:pre-wrap; color:black;">{result}</pre>
    </div>
    """,
    unsafe_allow_html=True
)