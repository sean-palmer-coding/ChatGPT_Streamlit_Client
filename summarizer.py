from openai_client import client

def get_max_tokens(messages):
    length = len(messages)
    if length <= 10:
        return 150
    elif length <= 50:
        return 300
    else:
        return 600

def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Summarize the following text concisely:"}, {"role": "user", "content": text}],
        max_tokens=15
    )
    print(response)
    summary = response.choices[0].message.content.strip()
    return summary

def summarize_conversation(messages):
    full_conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    max_tokens = get_max_tokens(messages)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following conversation concisely, highlighting the key points and important details. This summary will be used to help resume the conversation later, so please ensure it captures the essence of the dialogue accurately."},
            {"role": "user", "content": full_conversation}
        ],
        max_tokens=max_tokens
    )
    summary = response.choices[0].message.content.strip()
    return summary

