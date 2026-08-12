import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ===========================
# Load Environment Variables
# ===========================
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ===========================
# Page Config
# ===========================
st.set_page_config(
    page_title="My Chatbot For Project",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 My Chatbot For Project")
st.caption("Powered by OpenRouter")

# ===========================
# Sidebar
# ===========================
st.sidebar.header("⚙️ Settings")

model = st.sidebar.selectbox(
    "AI Model",
    [
        "openai/gpt-4o-mini",
        "openai/gpt-4.1-mini",
        "deepseek/deepseek-chat",
        "meta-llama/llama-3.3-70b-instruct",
        "anthropic/claude-3.5-sonnet"
    ]
)

temperature = st.sidebar.slider(
    "Creativity",
    0.0, 2.0, 0.7, 0.1
)

max_tokens = st.sidebar.slider(
    "Max Tokens",
    100, 4000, 1000
)

system_prompt = st.sidebar.text_area(
    "System Prompt",
    "You are ChatGPT, a helpful, intelligent, friendly AI assistant."
)

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]
    st.rerun()

# ===========================
# Chat History
# ===========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

# ===========================
# Display Messages
# ===========================
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ===========================
# User Input
# ===========================
prompt = st.chat_input("Message ChatGPT...")

if prompt:

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        start = time.time()

        try:

            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta

                    if delta.content:
                        full_response += delta.content
                        placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"❌ {e}"
            placeholder.error(full_response)

        end = time.time()

        st.caption(f"⏱ Response Time: {end-start:.2f} sec")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )

# ===========================
# Sidebar Statistics
# ===========================
st.sidebar.divider()

st.sidebar.subheader("📊 Chat Statistics")

user_messages = len(
    [m for m in st.session_state.messages if m["role"] == "user"]
)

assistant_messages = len(
    [m for m in st.session_state.messages if m["role"] == "assistant"]
)

st.sidebar.metric("User Messages", user_messages)
st.sidebar.metric("Assistant Replies", assistant_messages)

# ===========================
# Download Chat
# ===========================
chat_json = json.dumps(
    st.session_state.messages,
    indent=4
)

st.sidebar.download_button(
    "📥 Download Chat",
    chat_json,
    file_name="chat_history.json",
    mime="application/json"
)

st.sidebar.markdown("---")
st.sidebar.success("✅ ChatGPT Clone Ready!")