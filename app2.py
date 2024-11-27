from flask import Flask, request, jsonify, render_template
from time import sleep
from openai import OpenAI
import logging
import os
import glob

logging.basicConfig(level=logging.INFO)
# Initialize OpenAI client with API key from environment variable
client = OpenAI()

app = Flask(__name__)

# Load personality instructions from a file
with open("DIiA/personality.txt", "r") as file:
    personality = file.read()

# Step 1: Upload a file with an "assistants" purpose
file_path = "DIiA/personality.txt"  # Replace with your file
uploaded_file = client.files.create(
    file=open(file_path, "rb"),
    purpose='assistants'
)
#step 2: Create or retrieve the personality file
def get_or_create_personality_file():
    # Try to retrieve the uploaded file named 'personality.txt'
    try:
        files = client.files.list()
        for file in files.data:
            if file.filename == 'personality.txt':
                return file
    except Exception as e:
        print(f"Error retrieving files: {e}")
    # If not found, upload the file
    uploaded_file = client.files.create(
        file=open(file_path, "rb"),
        purpose='assistants'
    )
    return uploaded_file

uploaded_file = get_or_create_personality_file()

def get_or_create_vector_store():
    # Try to find an existing vector store with the desired name
    desired_name = "history_data_binned"
    vector_stores = client.beta.vector_stores.list()
    for vs in vector_stores.data:
        if vs.name == desired_name:
            return vs
    # If not found, create a new vector store
    file_paths = glob.glob("DIiA/RAG_data/*")
    file_ids = []
    for path in file_paths:
        with open(path, "rb") as f:
            uploaded_file = client.files.create(
                file=f,
                purpose='assistants'
            )
            file_ids.append(uploaded_file.id)
    vector_store = client.beta.vector_stores.create(
        name=desired_name,
        file_ids=file_ids
    )
    return vector_store

vector_store = get_or_create_vector_store()

def get_or_create_assistant(vector_store):
    assistant_name = "Vincent van Gogh"
    # Get list of assistants
    assistants = client.beta.assistants.list().data
    # Check if assistant with the name exists
    for assistant in assistants:
        if assistant.name == assistant_name:
            return assistant
    # If not found, create a new assistant
    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=personality,
        tools=[{"type": "file_search"}],
        model="gpt-3.5-turbo",
        tool_resources={"file_search":  {"vector_store_ids":[vector_store.id]}}
    )
    return assistant

assistant = get_or_create_assistant(vector_store)

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
        instructions=personality
    )

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
    sources = []
    for msg in messages:
        if msg.role == 'assistant' and msg.content:
            # Assuming msg.content is a list of TextContentBlock objects
            reply.append(msg.content[0].text.value)  # Extract the value from the response
    #reply.append(cleaned_text)
    #sources.extend(re.findall(r'【\d+:\d+†source】', text))
    #cleaned_text = re.sub(r'【\d+:\d+†source】', '', text)
    # Remove source references and collect them
    #text = msg.content[0].text.value
    # Assuming msg.content is a list of TextContentBlock objects

    # Step 5.7: Format the assistant's reply as a JSON response
    output = jsonify({"response": reply[1], "sources": sources})

    return output


# Step 6: Run if __main__
if __name__ == '__main__':
    app.run(debug=True, port=5001)


 
    # Step 5.7: Format the assistant's reply and sources as a JSON response
      