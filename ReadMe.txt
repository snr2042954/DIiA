New OPENAI API implementation does not allow for API key sharing. To run app.py you will need to create a
permanent environment variable named OPENAI_API_KEY. To do so follow the steps below:

0. create an openai.com account
1. go to https://platform.openai.com/api-keys and click on create new key
2. note the key down as it will disappear afterward.
3. Open Command Prompt or PowerShell
4. Execute the following command: setx OPENAI_API_KEY "your_api_key_here"

This command creates a permanent environment variable named OPENAI_API_KEY with the specified value.