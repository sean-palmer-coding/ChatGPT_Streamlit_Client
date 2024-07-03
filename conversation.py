import streamlit as st
from database import get_db, get_conversation, get_messages, add_message, add_summary
from openai_client import client
from summarizer import summarize_conversation


def run(conversation_id):
    if not conversation_id or conversation_id == "future":
        conversation_id = st.session_state.get("conversation_id", None)
        if not conversation_id:
            st.error("No conversation selected")
            return
    # Dropdown to select the model
    st.title("Conversation")

    model = 'gpt-4o'

    db = next(get_db())
    conversation = get_conversation(db, conversation_id)
    if conversation:
        st.session_state.conversation_id = conversation_id
        st.session_state.messages = [{"role": msg.role, "content": msg.content} for msg in
                                     get_messages(db, conversation_id)]
        st.session_state.description = conversation.title if conversation.title else None
        st.session_state.resuming = True

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                if model == "gpt-3.5-turbo":
                    # Send the entire conversation history
                    initial_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                else:
                    # Summarize the conversation history to reduce token usage
                    conversation_summary = summarize_conversation(st.session_state.messages)
                    initial_messages = [{"role": "system", "content": conversation_summary}]
                    initial_messages += [{"role": m["role"], "content": m["content"]} for m in
                                         st.session_state.messages[-5:]]  # Include only the last few messages

                stream = client.chat.completions.create(
                    model=model,
                    messages=initial_messages,
                    stream=True,
                )
                print(model)
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

            add_message(db, st.session_state.conversation_id, "user", prompt)
            add_message(db, st.session_state.conversation_id, "assistant", response)

            if model != "gpt-3.5-turbo":
                # Summarize the entire conversation
                conversation_summary = summarize_conversation(st.session_state.messages)
                st.session_state.description = conversation_summary
                add_summary(db, st.session_state.conversation_id, conversation_summary)
    else:
        st.error("Conversation not found.")


if __name__ == "__main__":
    conversation_id = st.session_state.get("conversation_id", None)
    run(conversation_id)
