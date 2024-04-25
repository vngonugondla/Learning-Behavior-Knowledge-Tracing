import streamlit as st
import json
from priority_queue import PriorityQueue
import time
import random

def run():
    st.set_page_config(
        page_title="Streamlit quizz app",
        page_icon="❓",
    )

if __name__ == "__main__":
    run()

with open('content/quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

st.markdown("""
<style>
div.stButton > button:first-child {
    display: block;
    margin: 0 auto;
</style>
""", unsafe_allow_html=True)

# Define a default value for topic_q_no
topics = ["Frequency Analysis", "Filter Design", "Modulation Techniques"]
default_topic_q_no = {"Frequency Analysis": [3, [], 0], "Filter Design": [3, [], 0], "Modulation Techniques": [3, [], 0]}

# Set topic_q_no to session state, initializing it with the default value
topic_q_no = st.session_state.get('topic_q_no', default_topic_q_no)

# Define default values for other session state variables
default_values = {'current_index': 0, 'current_question': 0, 'score': 0, 'selected_option': None, 'answer_submitted': False, 'option_click_counters': [0] * len(quiz_data), 'start_time': time.time(), 'num_answered':0, 'curr_question':1}
for key, value in default_values.items():
    st.session_state.setdefault(key, value)

# Initialize priority queue from session state or create a new one if it doesn't exist
priority_queue = st.session_state.get('priority_queue', PriorityQueue(topics))

# Load quiz data
with open('content/quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

def restart_quiz():
    st.session_state.curr_question = 1
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.option_click_counters = [0] * len(quiz_data)
    st.session_state.start_time = time.time()
    st.session_state.num_answered = 0
    # Restart with newly initialized PQ and reset indice of each topic
    st.session_state.priority_queue = PriorityQueue(topics)
    st.session_state.topic_q_no = default_topic_q_no

# Move topic_q_no update logic to a function
def update_topic_q_no(topic, index):
    topic_q_no[topic][index] += 1
    st.session_state.topic_q_no = topic_q_no  # Save updated topic_q_no to session state

def submit_answer():
    global recommendation_updated
    global topic_q_no
    st.session_state.num_answered += 1
    
    st.session_state.recommendation_updated = False

    if st.session_state.selected_option is not None:
        st.session_state.answer_submitted = True
        time_taken_to_submit = int(time.time() - st.session_state.start_time)  # in seconds
        time_limit = 60
        speed = time_limit / time_taken_to_submit
        no_of_attempts = st.session_state.option_click_counters[st.session_state.current_index]

        topic = quiz_data[st.session_state.current_index]['topic']
        total_questions, answered_questions, correct_submissions = topic_q_no[topic]

        topic_q_no[topic][1].append(quiz_data[st.session_state.current_index]['ind'])
        st.session_state.topic_q_no = topic_q_no
        #update_topic_q_no(topic, 1)  # Increment answered_questions

        # Check if the selected option is correct
        if st.session_state.selected_option == quiz_data[st.session_state.current_index]['answer']:
            update_topic_q_no(topic, 2)  # Increment correct_submissions
            st.session_state.score += 10

        # Update the recommendation table only if not updated already in this interaction
        if not st.session_state.recommendation_updated:
            update_recommendation_table(speed, no_of_attempts, time_limit)
        print("Priority Queue Values:", priority_queue.heap)

def option_selected(option):
    st.session_state.selected_option = option
    st.session_state.option_click_counters[st.session_state.current_index] += 1

def next_question():
    st.session_state.curr_question += 1
    print(priority_queue)
    print("Heap:", priority_queue.heap)
    next_topic = priority_queue.heap[0][1]
    remainingQuestions = list({0,1,2} - set(st.session_state.topic_q_no[next_topic][1]))
    while len(remainingQuestions) == 0:
        priority_queue.pop()
        next_topic = priority_queue.heap[0][1]
        remainingQuestions = list({0,1,2} - set(st.session_state.topic_q_no[next_topic][1]))

    chosenInd = random.choice(remainingQuestions)
    st.session_state.current_index = topics.index(next_topic) * 3 + chosenInd #+=1
    st.session_state.topic_q_no[next_topic][1].append(chosenInd)
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.start_time = time.time()

def update_recommendation_table(speed, no_of_attempts, timeTaken):
        topic = quiz_data[st.session_state.current_index]['topic']

        accuracy = st.session_state.topic_q_no[topic][2] / len(st.session_state.topic_q_no[topic][1]) if len(st.session_state.topic_q_no[topic][1]) > 0 else 0
        print(accuracy, "accuracy")
        weighted_accuracy = 0

        if accuracy > 0:
            if st.session_state.topic_q_no[topic][0] > 1:
                prev_accuracy = 0
                for acc, tpc in priority_queue.heap:
                    if tpc == topic:
                        prev_accuracy = acc
                        break
                print(prev_accuracy, "prev_accuracy")
                print("topic question number", st.session_state.topic_q_no[topic][1])
                weighted_accuracy = (prev_accuracy + (1 / accuracy) * (speed / timeTaken) * no_of_attempts)
                weighted_accuracy = weighted_accuracy / len(st.session_state.topic_q_no[topic][1])
                print(weighted_accuracy, "weighted_accuracy")
                priority_queue.push(topic, weighted_accuracy)  
                st.session_state.priority_queue = priority_queue

            else:
                weighted_accuracy = accuracy            
                st.session_state.priority_queue = priority_queue
        else:
            #if topic not in priority_queue.topic_mapping:
            priority_queue.push(topic, 0)  


# Title and description
st.title("Learning Behavior Knowledge Tracing Quiz App")
question_counter = st.session_state.get('question_counter', 0)
progress_bar_value = (st.session_state.num_answered) / len(quiz_data)
st.metric(label="Score", value=f"{st.session_state.score} / {len(quiz_data) * 10}")
st.progress(progress_bar_value)

question_item = quiz_data[st.session_state.current_index]
# st.subheader(f"Question {st.session_state.current_index + 1}")
st.subheader(f"Question {st.session_state.curr_question}")

st.title(f"{question_item['question']}")
st.write(question_item['information'])

st.markdown(""" ___""")

st.write(f"Number of attempts: {st.session_state.option_click_counters[st.session_state.current_index]}")
st.write(priority_queue.heap)
st.write(priority_queue.topic_mapping)

options = question_item['options']
correct_answer = question_item['answer']

if st.session_state.answer_submitted:
    st.write(f"Time taken: {int(time.time() - st.session_state.start_time)}")
    for i, option in enumerate(options):
        label = option
        if option == correct_answer:
            st.success(f"{label} (Correct answer)")
        elif option == st.session_state.selected_option:
            st.error(f"{label} (Incorrect answer)")
        else:
            st.write(label)
else:
    for option in options:
        if st.button(option, key=option, on_click=option_selected, args=(option,), use_container_width=True):
            pass

st.markdown(""" ___""")

if st.session_state.answer_submitted:
    if st.session_state.num_answered < len(quiz_data):
        st.button('Next', on_click=next_question)
    else:
        st.write(f"Your score is: {st.session_state.score} / {len(quiz_data) * 10}")
        if st.button('Restart', on_click=restart_quiz):
            #topic_q_no = st.session_state.get('topic_q_no', default_topic_q_no)
            #priority_queue = st.session_state.get('priority_queue', PriorityQueue(topics))
            pass
else:
    if st.session_state.current_index < len(quiz_data):
        st.button('Submit', on_click=submit_answer)