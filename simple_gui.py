import streamlit as st
from streamlit_chat import message
from v1.graph import WorkFlow

# Setting page title and header
st.set_page_config(page_title="AI Chat", page_icon=":robot_face:")
st.title("Chat with AI")


# Assume we have a 'model' object with an 'invoke' method
@st.cache_resource
def get_model():
    return WorkFlow()


model = get_model()

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display chat messages
message("Hello, How can I help you?", key='0_startup',avatar_style='lorelei-neutral', seed='Molly')

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = model.invoke(user_input)['messages'][-1].content
        st.session_state['messages'].append([user_input, "user"])
        st.session_state['messages'].append([output, "assistant"])

if st.session_state['messages']:
    with response_container:
        for index, msg in enumerate(st.session_state['messages']):
            if msg[1] == "user":
                message(msg[0], is_user=True, key=str(index) + "_user", avatar_style='lorelei', seed='Leo')
            elif msg[1] == "assistant":
                message(msg[0], key=str(index) + "_assistant", avatar_style='lorelei-neutral', seed='Molly')

# Add a button to clear the chat history
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
