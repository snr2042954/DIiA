from flask import Flask, request, jsonify, render_template
from time import sleep
from openai import OpenAI
import logging
import os
import re
import function_VanGogh as fvg
from openai.types.beta.threads import FileCitationAnnotation

logging.basicConfig(level=logging.INFO)
# Initialize OpenAI client with API key from environment variable
client = OpenAI()

app = Flask(__name__)

# Load personality instructions from a file
with open("personality.txt", "r") as file:
    personality = file.read()
# Step 1: Upload a file with an "assistants" purpose
file_path ="personality.txt"  # Replace with your file path
#step 2: Create or retrieve the personality file

uploaded_file = fvg.get_or_create_personality_file(client, file_path)

vector_store = fvg.get_or_create_vector_store(client)

assistant = fvg.get_or_create_assistant(client, vector_store, personality)
# Step 3: Create a new conversation thread
thread = client.beta.threads.create()  

# Step 4: Outline the html template
@app.route('/')
def index():
    return render_template('startscreen.html')
@app.route('/startscreen.html')
def startscreen():
    return render_template('startscreen.html')
@app.route('/early-life.html')
def early_life():
    return render_template('early-life.html')
# Step 5: Implement POST Method
@app.route('/chat', methods=['POST'])
def chat():
    # Step 5.1: Retrieve the message
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Step 5.2: Add the user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )

    # Step 5.3: Run the Assistant on the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=personality,
        include=["step_details.tool_calls[*].file_search.results[*].content"]
    )
    print(f"Run output: {run}")

    # Step 5.4: Poll until the run is complete
    while run.status != "completed":
        print(f"run status: {run.status}")
        sleep(1)

        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"run status: {run.status}")

    # Step 5.5: Retrieve the assistant's messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Step 5.6: Extract the assistant's reply from the messages
    reply = ["No response found."]
    citations = []
    for msg in messages:
        if msg.role == 'assistant' and msg.content:
            # Iterate over the annotations and add footnotes
            for index, annotation in enumerate(msg.content[0].text.annotations):
                # Replace the text with a footnote
                msg.content[0].text.value = msg.content[0].text.value.replace(annotation.text, f' [{index}]')
                print(annotation.type)
                # Gather citations based on annotation attributes
                file_id = annotation.file_citation.file_id
                file = client.files.retrieve(file_id)
                citations.append(f'[{index}] sourced from: {file.filename}')
            reply.append(msg.content[0].text.value)
    
    
    # Step 5.7: Format the assistant's reply as a JSON response
    output = jsonify({"response": reply[1], "sources": citations})

    return output


# Step 6: Run if __main__
if __name__ == '__main__':
    app.run(debug=True, port=5001)

      