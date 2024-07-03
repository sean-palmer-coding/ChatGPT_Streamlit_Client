import streamlit as st
import new_conversation
import conversation
from database import get_db, get_all_conversations

def run_new_conversation():
    new_conversation.run()

def run_conversation(conv_id):
    conversation.run(conv_id)

# Inject custom CSS for text wrapping


# Get all conversations from the database
db = next(get_db())
all_conversations = get_all_conversations(db)

# Sort conversations in descending order based on their creation date
all_conversations_sorted = sorted(all_conversations, key=lambda conv: conv.created_at, reverse=True)

# Create a list of Page objects for each conversation
pages = [
    st.Page(run_new_conversation, title="New Conversation", icon="➕"),  # Omit url_path for the new conversation page
]

for conv in all_conversations_sorted:
    pages.append(st.Page(
        lambda conv_id=conv.conversation_id: run_conversation(conv_id),  # Pass conversation ID
        title=conv.title if conv.title else conv.conversation_id,
        icon="💬",
        url_path=conv.conversation_id
    ))

# Create the navigation menu
pg = st.navigation({'New Conversation': [pages[0],], 'Previous Conversations': pages[1:]})
pg.run()
