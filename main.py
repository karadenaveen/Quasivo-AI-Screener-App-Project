
import streamlit as st
from gemini_api import call_gemini
from utils import extract_text_from_pdf, save_to_json

st.set_page_config(page_title="AI Screener", layout="centered")
st.title("AI – Screener App")

st.header("Upload Inputs")

jd_text = ""
resume_text = ""

jd_input = st.text_area("Job Description or Upload File")
jd_file = st.file_uploader("Upload JD (.txt)", type=["txt"])
if jd_file:
    jd_text = jd_file.read().decode()
elif jd_input:
    jd_text = jd_input

resume_input = st.text_area("Resume or Upload PDF")
resume_file = st.file_uploader("Upload Resume (.pdf)", type=["pdf"])
if resume_file:
    resume_text = extract_text_from_pdf(resume_file)
elif resume_input:
    resume_text = resume_input

# Save state for questions and answers
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'show_answers' not in st.session_state:
    st.session_state.show_answers = False

if jd_text and resume_text and st.button("Generate Questions"):
    with st.spinner("Generating questions..."):
        prompt = f"""
You are an AI recruiter.

Given the following job description and candidate resume, generate ONLY THREE technical interview questions that help evaluate the candidate's suitability for the role.

Format your response as:
1. ...
2. ...
3. ...

Do NOT include any analysis or explanation.

Job Description:
{jd_text}

Resume:
{resume_text}
"""
        questions_text = call_gemini(prompt)

        # Keep only numbered lines (1., 2., 3.)
        questions = [line.strip() for line in questions_text.split('\n') if line.strip().startswith(('1.', '2.', '3.'))]

        if len(questions) != 3:
            st.error("Gemini did not return exactly 3 questions. Please try again or refine the prompt.")
        else:
            st.session_state.questions = questions
            st.session_state.show_answers = True

# Only show answer fields if questions are generated
if st.session_state.show_answers:
    st.subheader("Answer the Questions Below:")

    answers = []
    for i, q in enumerate(st.session_state.questions, 1):
        st.subheader(f"Question {i}: {q}")
        key = f"answer_{i}"
        if key not in st.session_state:
            st.session_state[key] = ""
        st.session_state[key] = st.text_area(f"Your Answer {i}", value=st.session_state[key])
        answers.append(st.session_state[key])

    if st.button("Submit Answers"):
        if all(a.strip() for a in answers):
            with st.spinner("Scoring answers..."):
                scores = []
                for q, a in zip(st.session_state.questions, answers):
                    score_prompt = f"""
Score the following answer on a scale of 1 to 10 based on its quality and relevance.

Question: {q}
Answer: {a}
Only return a number between 1 and 10.
"""
                    score = call_gemini(score_prompt)
                    scores.append(score.strip())

                results = {
                    "job_description": jd_text,
                    "resume": resume_text,
                    "questions": st.session_state.questions,
                    "answers": answers,
                    "scores": scores
                }

                save_to_json(results)
                st.success("Results saved locally!")

                st.header("Summary")
                for i in range(3):
                    st.markdown(f"**Q{i+1}:** {st.session_state.questions[i]}")
                    st.markdown(f"**A{i+1}:** {answers[i]}")
                    st.markdown(f"**Score:** {scores[i]}")
        else:
            st.warning("Please fill all answers before submitting.")
