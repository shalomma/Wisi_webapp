import os
import base64
import openai
from io import BytesIO
import streamlit as st
from streamlit_chat import message
from elevenlabs import generate, set_api_key
import streamlit.components.v1 as components

set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# Setting page title and header
st.set_page_config(page_title="Wisi", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>Wisi - your social tutor 🦉</h1>", unsafe_allow_html=True)

# Initialise system instructions
with open('system.txt', 'r') as f:
    system_instruction = f.read()

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": system_instruction}
    ]


def update_system_instruction():
    st.session_state['messages'][0] = {"role": "system", "content": st.session_state.text}


st.sidebar.title('')
st.sidebar.text_area(label='System Instruction', value=system_instruction,
                     key='text', on_change=update_system_instruction)
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [{"role": "system", "content": system_instruction}]
    st.session_state['number_tokens'] = []


# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})
    return response


def audio_to_html(audio_bytes):
    audio_io = BytesIO(audio_bytes)
    audio_io.seek(0)
    audio_base64 = base64.b64encode(audio_io.read()).decode("utf-8")
    audio_html = f'<audio src="data:audio/mpeg;base64,{audio_base64}" controls autoplay></audio>'
    return audio_html


def text_to_speech_elevenlabs(response):
    audio_stream = generate(
        text=response,
        voice="Bella",
        model="eleven_monolingual_v1"
    )
    audio_html = audio_to_html(audio_stream)
    return audio_html


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        audio = text_to_speech_elevenlabs(output)
        components.html(audio, height=0)

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
