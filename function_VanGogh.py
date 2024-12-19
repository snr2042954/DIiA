
import glob
from flask import request, jsonify
from time import sleep
import re

def get_or_create_personality_file(client, file_path):
    # Try to retrieve the uploaded file named 'personality.txt' personality.txt
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

def get_or_create_vector_store(client):
    # Try to find an existing vector store with the desired name
    desired_name = "history_data_binned"
    vector_stores = client.beta.vector_stores.list()
    for vs in vector_stores.data:
        if vs.name == desired_name:
            return vs
    # If not found, create a new vector store
    file_paths = glob.glob(r"C:\Users\Colli\OneDrive - Tilburg University\Msc Data science in entrepreneurship and business\Intrapreneurship in Action\MVP_Van_Gogh_Learning_Module\DIiA\RAG_data\*")
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

def get_or_create_assistant(client, vector_store, personality):
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
        model="gpt-4o-mini",
        tool_resources={"file_search":  {"vector_store_ids":[vector_store.id]}}
    )
    return assistant









# Step 5.6: Extract the assistant's reply from the messages
    reply = ["No response found."]
    for msg in messages:
        if msg.role == 'assistant' and msg.content:
            citations = []
            # Iterate over the annotations and add footnotes
            for index, annotation in enumerate(msg.content[0].text.annotations):
                # Replace the text with a footnote
                msg.content[0].text.value = msg.content[0].text.value.replace(annotation.text, f' [{index}]')
                # Gather citations based on annotation attributes
                for file_id in enumerate(annotation):
                    file_info = client.files.retrieve(file_id)
                    citations.append(file_info['filename']) 
            print(msg.content[0].text)
            print(citations)
            reply.append(msg.content[0].text.value)
    