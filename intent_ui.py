import streamlit as st
import json
from intent_agent import get_intent_from_prompt

st.set_page_config(page_title="AutoDataAgent - Chat Assistant")
st.title("🧠 AutoDataAgent - Intent Agent Chat")

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Tell me what data you need and why 😊"}]

if "task_spec" not in st.session_state:
    st.session_state.task_spec = {}

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input field
user_input = st.chat_input("What data are you looking for?")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Claude response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_intent_from_prompt(user_input, st.session_state.task_spec)
            try:
                updated_dict = json.loads(response)
                st.session_state.task_spec = updated_dict
                msg = "Here's the updated task specification:"
                st.markdown(msg)
                st.code(json.dumps(updated_dict, indent=2), language="json")
            except Exception as e:
                msg = "I couldn't parse the task properly. Please try again."
                st.markdown(msg)
                st.code(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{msg}\n```json\n{response}\n```"
    })

