from openai import OpenAI
client = OpenAI()

# USE setx OPENAI_API_KEY

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-3.5-turbo",
)

