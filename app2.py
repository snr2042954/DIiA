from flask import Flask, request, jsonify, render_template
import os
from time import sleep
from openai import OpenAI

# Initialize OpenAI client with API key from environment variable
client = OpenAI()

app = Flask(__name__)

# Load personality instructions from a file
with open("personality.txt", "r") as file:
    personality = file.read()

# Step 1: Upload a file with an "assistants" purpose
file_path = "personality.txt"  # Replace with your file
uploaded_file = client.files.create(
    file=open(file_path, "rb"),
    purpose='assistants'
)

# Create the assistant with the desired instructions and tools
# Implement https://platform.openai.com/docs/assistants/tools/file-search
assistant = client.beta.assistants.create(
    name="Vincent van Gogh",
    instructions=personality,
    tools=[{"type": "file_search"}],
    model="gpt-3.5-turbo"
)

# Step 3: Create a new conversation thread
# It's good practice to create a new thread per user interaction session.
thread = client.beta.threads.create()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Step 4: Add the user message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )

    # Step 5: Run the Assistant on the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=personality
    )

    # Step 6: Poll until the run is complete
    while run.status != "completed":
        sleep(1)

        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    # Step 7: Retrieve the assistant's response messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Extract the assistant's reply from the messages
    reply = ["No response found."]
    for msg in messages:
        if msg.role == 'assistant' and msg.content:
            # Assuming msg.content is a list of TextContentBlock objects
            reply.append(msg.content[0].text.value)  # Extract the value from the response

    # Return the assistant's reply as a JSON response
    return jsonify({"response": reply[1]})


@app.route('/test')
def test():
    return "Flask is working!"


if __name__ == '__main__':
    app.run(debug=True, port=8080)
