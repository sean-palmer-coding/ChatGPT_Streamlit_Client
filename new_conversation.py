import streamlit as st
import uuid
from app import run_conversation, pages
from database import get_db, create_conversation, add_message, add_summary
from openai_client import client
from summarizer import summarize_text, summarize_conversation

def run():
    st.title("New Conversation")

    if prompt := st.chat_input("What is up?"):
        # Create initial summary
        initial_summary = summarize_text(prompt)
        conversation_id = str(uuid.uuid4())
        # Create new conversation with the initial summary as title
        db = next(get_db())
        create_conversation(db, conversation_id, "user_123", initial_summary)

        st.session_state.conversation_id = conversation_id
        st.session_state.messages = [{"role": "user", "content": prompt}]
        st.session_state.description = initial_summary

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            initial_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=initial_messages,
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})

        add_message(db, conversation_id, "user", prompt)
        add_message(db, conversation_id, "assistant", response)

        # Summarize the entire conversation
        conversation_summary = summarize_conversation(st.session_state.messages)
        st.session_state.description = conversation_summary

        add_summary(db, conversation_id, conversation_summary)

        # Update the page registry and switch to the new conversation page

        st.switch_page(st.Page(
            lambda conv_id=conversation_id: run_conversation(conv_id),
            title=initial_summary,
            icon="💬",
            url_path=f"conversation/{conversation_id}"
        ))

if __name__ == "__main__":
    run()
