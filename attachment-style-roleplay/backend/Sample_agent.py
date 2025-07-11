import os
from dotenv import load_dotenv
from openai import OpenAI
from load_prompts import load_agent_prompts

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Load your prompts JSON however you do it
prompts = load_agent_prompts()

partner_style = "secure"
prompt_template = prompts[partner_style]

# Conversation history (list of messages in chat format)
conversation = [
    {"role": "system", "content": prompt_template.template.split("\\n")[0]}
]

print("Start chatting with your partner! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "stop"]:
        print("Conversation ended.")
        break
    
    user_message = prompt_template.format(input=user_input)
    # Append user's message
    conversation.append({"role": "user", "content": user_message})

    # Call OpenAI with conversation history to keep context
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.7,
        max_tokens=60,
        frequency_penalty=0.3,
        presence_penalty=0.1
    )

    reply = response.choices[0].message.content.strip()
    print("Partner:", reply)

    # Append partner's reply to conversation to keep context
    conversation.append({"role": "assistant", "content": reply})

    # Optional: keep conversation history length limited to save tokens
    if len(conversation) > 12:  # ~6 user/partner exchanges
        # Keep system prompt + last 10 messages
        conversation = [conversation[0]] + conversation[-10:]
