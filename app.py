import streamlit as st
import pdfplumber
import re
from groq import Groq
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# -----------------------------
# PAGE CONFIG
# -----------------------------

# -----------------------------
# CLEAN PROFESSIONAL STYLING
# -----------------------------
st.markdown("""
<style>

/* White background */
[data-testid="stAppViewContainer"] {
    background-color: white;
}

/* Center content */
.main .block-container {
    max-width: 1050px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    color: black;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: black;
    margin-bottom: 45px;
    font-size: 16px;
}

/* Section Titles */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 20px;
    color: black;
}

/* Input label */
.input-label {
    font-weight: 600;
    margin-bottom: 6px;
    color: black;
}

/* Buttons */
.stButton > button {
    background-color: black !important;
    color: white !important;
    border-radius: 6px;
    padding: 10px 22px;
    font-weight: 600;
    border: none;
}

/* Force text inside button to white */
.stButton > button * {
    color: white !important;
}

.stButton>button:hover {
    background-color: #222222;
}

/* Remove blue focus */
button:focus,
input:focus,
textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* Inputs */
.stTextInput>div>div>input,
.stTextArea textarea {
    border-radius: 6px;
    border: 1px solid #cccccc;
    background-color: white;
    padding: 10px;
    color: black;
}

/* Clean file uploader */
[data-testid="stFileUploader"] {
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 12px;
    background-color: white;
}

[data-testid="stFileUploader"] section {
    background-color: white !important;
    border: none !important;
}
/* Spinner text color */
[data-testid="stSpinner"] * {
    color: black !important;
}
/* Upload box text black */
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] p {
    color: black !important;
}
/* File name text black */
[data-testid="stFileUploader"] div[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] div[data-testid="stFileUploaderFileSize"],
[data-testid="stFileUploader"] span[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] span[data-testid="stFileUploaderFileSize"] {
    color: black !important;
}
/* Specifically drag text */
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] p {
    color: black !important;
}
/* Remove hover blink from file uploader button */
[data-testid="stFileUploader"] button {
    background-color: black !important;
    color: white !important;
    transition: none !important;
}

[data-testid="stFileUploader"] button:hover {
    background-color: black !important;
    color: white !important;
}
/* Divider */
hr {
    border: none;
    border-top: 1px solid #e5e5e5;
    margin: 35px 0;
}
/* Force only normal text to black */
.stMarkdown p,
.stMarkdown span,
.stMarkdown li,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">AI Resume & Job Matcher</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Professional ATS-based resume analysis and job compatibility scoring</div>', unsafe_allow_html=True)

# -----------------------------
# INPUT SECTION
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Candidate Information</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-label">Full Name</div>', unsafe_allow_html=True)
    name = st.text_input("Full Name", key="full_name", label_visibility="collapsed")

    st.markdown('<div class="input-label">Email Address</div>', unsafe_allow_html=True)
    email = st.text_input("Email Address", key="email_address", label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-title">Resume Upload</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-label">Upload PDF Resume</div>', unsafe_allow_html=True)
    file = st.file_uploader("Upload Resume", type="pdf", key="resume_upload", label_visibility="collapsed")

st.markdown('<div class="section-title">Job Description</div>', unsafe_allow_html=True)
job_description = st.text_area("Job Description", key="job_desc", label_visibility="collapsed")
analyze = st.button("Analyze Resume")

st.markdown("<hr>", unsafe_allow_html=True)
# -----------------------------
# ANALYSIS SECTION
# -----------------------------
if analyze:

    if not name or not email:
        st.warning("Please enter your name and email.")
    elif file is None:
        st.warning("Please upload a resume first.")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.warning("Please enter a valid email address.")
    else:

        resume_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    resume_text += text

        prompt = f"""
You are an advanced Applicant Tracking System (ATS) and professional HR evaluator.

Evaluate the resume against the job description.

Provide output strictly in this format:

SUMMARY:
STRENGTHS:
WEAKNESSES:
RESUME_SCORE:
JOB_MATCH_PERCENTAGE:
MISSING_SKILLS:
IMPROVEMENT_SUGGESTIONS:

Do not exaggerate scores.
Do not modify the candidate's name formatting.

Resume:
{resume_text}

Job Description:
{job_description}
"""

        # 🔥 Correct indentation here
        with st.spinner("Analyzing resume and calculating job match..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            result = response.choices[0].message.content

        # 🔥 Strong regex extraction
        resume_score = re.search(r"RESUME[\s_]*SCORE[^0-9]*(\d+)", result, re.IGNORECASE)
        match_score = re.search(r"JOB[\s_]*MATCH[\s_]*PERCENTAGE[^0-9]*(\d+)", result, re.IGNORECASE)

        st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)

        colA, colB = st.columns(2)

        if resume_score:
            with colA:
                val = int(resume_score.group(1))
                st.markdown("<h3 style='color:black;'>Resume Score</h3>", unsafe_allow_html=True)
                st.progress(val / 100)
                st.write(f"{val}/100")

        if match_score:
            with colB:
                val = int(match_score.group(1))
                st.markdown("<h3 style='color:black;'>Job Match</h3>", unsafe_allow_html=True)
                st.progress(val / 100)
                st.write(f"{val}%")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="color: black; line-height: 1.4; font-size: 15px;">
                <h3 style="color: black; margin-bottom:10px;">Detailed AI Analysis</h3>
                <div style="white-space: pre-wrap;">
                    {result}
                </div>
            </div>
            """,
            unsafe_allow_html=True

        )



