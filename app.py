from flask import Flask, request, jsonify, render_template
import re
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

# Initialize OpenAI client with API key from environment variable
client = OpenAI()

app = Flask(__name__)

# Read the system message from a text file
with open("personality.txt", "r") as file:
    personality = file.read()

# Create the assistant with the desired instructions and tools
assistant = client.beta.assistants.create(
    name="Vincent van Gogh",
    instructions=personality,
    tools=[{"type": "code_interpreter"}],
    model="gpt-3.5-turbo"
)

thread = client.beta.threads.create()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    # Retrieve the user message from the JSON request
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=personality
    )

    # Retrieve the latest messages in the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Find and print the assistant's response
    if messages:
        # Loop through messages to find the assistant's response
        for msg in messages:
            if msg.role == 'assistant':  # Use dot notation to access attributes
                reply = re.search(r"value='(.*?)'",str(msg.content[0].text)).group(1)
    else:
        reply = "No messages found."

    # Just send the message back as a response for now
    return jsonify({"response": f"{reply}"})

@app.route('/test')
def test():
    return "Flask is working!"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
