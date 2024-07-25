import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

class Question:
    def __init__(self, question, options, correct_answer, explanation=None):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation

class Quiz:
    def __init__(self):
        self.questions = self.load_or_generate_questions()
        self.initialize_session_state()

    def load_or_generate_questions(self):
        # Check if questions already exist in the session state
        if 'questions' not in st.session_state:
            # Predefined questions or load from a source
            st.session_state.questions = [
                Question("What is the capital of France?", ["London", "Paris", "Berlin", "Madrid"], "Paris",
                         "Paris is the capital and most populous city of France."),
                Question("Who developed the theory of relativity?",
                         ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Marie Curie"], "Albert Einstein",
                         "Albert Einstein is known for developing the theory of relativity, one of the two pillars of modern physics.")
            ]
            # Optionally, add a step here to generate new questions via GPT-3 and append them
        return st.session_state.questions

    def initialize_session_state(self):
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'answers_submitted' not in st.session_state:
            st.session_state.answers_submitted = 0  # Track the number of answers submitted

    def display_quiz(self):
        self.update_progress_bar()
        if st.session_state.answers_submitted >= len(self.questions):
            self.display_results()
        else:
            self.display_current_question()

    def display_current_question(self):
        question = self.questions[st.session_state.current_question_index]
        st.write(question.question)
        options = question.options
        # Use a unique key for the radio to avoid option persistence across questions
        answer = st.radio("Choose one:", options, key=f"question_{st.session_state.current_question_index}")
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
        if  st.session_state.score/len(self.questions) == 1.0:
            st.success("Congrats")
            st.balloons()
        else:
            st.error("You failed, try again!")
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




# Function to convert the GPT response into a Questions object and append each question to the questions list
# Function to generate questions via GPT-4 and append it to the session state questions
def generate_and_append_questions(user_prompt):
    """
    history = ""
    for q in st.session_state.questions:
        history += f"Question: {q.question} Answer: {q.correct_answer}\n"
    
    st.write(history)
    """
    gpt_prompt = '''Generate a JSON response containing 3 questions, each one of these questions should include the question itself, options, correct answer, and explanation. The format for each one question should be as follows:
    {
    "Question": "The actual question text goes here?",
    "Options": ["Option1", "Option2", "Option3", "Option4"],
    "CorrectAnswer": "TheCorrectAnswer",
    "Explanation": "A detailed explanation on why the correct answer is correct."
    }'''
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": gpt_prompt},
                {"role": "user", "content": f"Create questions about : {user_prompt}"} #that each one is different from those : {history}"}
            ]
        )
        gpt_response = json.loads(response.choices[0].message.content)  # Assuming this returns the correct JSON structure
        st.write(gpt_response)
        
        for q in gpt_response["Questions"]: 
            new_question = Question(
                question=q["Question"],
                options=q["Options"],
                correct_answer=q["CorrectAnswer"],
                explanation=q["Explanation"])
            #st.write(new_question.correct_answer)
            st.session_state.questions.append(new_question)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Main app logic
if 'quiz_initialized' not in st.session_state:
    st.session_state.quiz = Quiz()
    st.session_state.quiz_initialized = True

user_input = st.text_input("Add your preferences")

if st.button('Generate New Question'):
    generate_and_append_questions(user_input)

st.session_state.quiz.display_quiz()
