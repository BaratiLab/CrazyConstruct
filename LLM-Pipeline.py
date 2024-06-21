import openai
import os

# Set your OpenAI API key
openai.api_key = 'your-api-key'

# Make a test API call to ChatGPT
response = openai.ChatCompletion.create(
    model="gpt-4",  # Replace with the model you want to use
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! How can I use the OpenAI API?"}
    ]
)

print(response.choices[0].message['content'])