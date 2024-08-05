import streamlit as st
from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

# Define Question class
class Question:
    def __init__(self, question, options, correct_answer, explanation=None):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation

# Define Quiz class
class Quiz:
    def __init__(self):
        self.questions = self.initialize_questions()
        self.initialize_session_state()

    def initialize_questions(self):
        if 'questions' not in st.session_state:
            st.session_state.questions = []
        return st.session_state.questions

    def initialize_session_state(self):
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'answers_submitted' not in st.session_state:
            st.session_state.answers_submitted = 0

    def display_quiz(self):
        self.update_progress_bar()
        if st.session_state.answers_submitted >= len(self.questions):
            self.display_results()
        else:
            self.display_current_question()

    def display_current_question(self):
        question = self.questions[st.session_state.current_question_index]
        st.write(question.question)
        answer = st.radio("Choose one:", question.options, key=f"question_{st.session_state.current_question_index}")
        if st.button("Submit Answer", key=f"submit_{st.session_state.current_question_index}"):
            self.check_answer(answer)
            st.session_state.answers_submitted += 1
            if st.session_state.current_question_index < len(self.questions) - 1:
                st.session_state.current_question_index += 1
            st.rerun()

    def check_answer(self, user_answer):
        correct_answer = self.questions[st.session_state.current_question_index].correct_answer
        if user_answer == correct_answer:
            st.session_state.score += 1
        else:
            st.error("Wrong answer!")
        if self.questions[st.session_state.current_question_index].explanation:
            st.info(self.questions[st.session_state.current_question_index].explanation)

    def display_results(self):
        st.write(f"Quiz completed! Your score: {st.session_state.score}/{len(self.questions)}")
        if st.session_state.score == len(self.questions):
            st.success("Congrats! You got all answers correct!")
            st.balloons()
        else:
            st.error("You didn't get all answers correct. Try again!")
        if st.button("Restart Quiz"):
            self.restart_quiz()

    def update_progress_bar(self):
        total_questions = len(self.questions)
        progress = st.session_state.answers_submitted / total_questions
        st.progress(progress)

    def restart_quiz(self):
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.answers_submitted = 0
        st.rerun()

# Generate and append questions via GPT-4
def generate_and_append_questions(user_prompt):
    gpt_prompt = '''Generate a JSON response containing 3 Questions. Each question should include the question text, options, correct answer, and explanation. The format for each question should be as follows:
    {
    "Question": "The actual question text goes here?",
    "Options": ["Option1", "Option2", "Option3", "Option4"],
    "CorrectAnswer": "TheCorrectAnswer",
    "Explanation": "A detailed explanation of why the correct answer is correct."
    }'''
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": gpt_prompt},
                {"role": "user", "content": f"Create questions about: {user_prompt}"}
            ]
        )
        gpt_response = json.loads(response.choices[0].message.content)
        for q in gpt_response["Questions"]:
            new_question = Question(
                question=q["Question"],
                options=q["Options"],
                correct_answer=q["CorrectAnswer"],
                explanation=q["Explanation"]
            )
            st.session_state.questions.append(new_question)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Main app logic
if 'quiz_initialized' not in st.session_state:
    st.header("Create your quiz")
    user_input = st.text_input("Add your topic of interest")
    if st.button('Generate New Questions'):
        st.session_state.quiz = Quiz()
        generate_and_append_questions(user_input)
        st.session_state.quiz_initialized = True
        st.session_state.quiz.display_quiz()
else:
    st.session_state.quiz.display_quiz()
