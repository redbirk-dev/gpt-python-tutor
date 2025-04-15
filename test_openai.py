import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print environment information
print("Environment variables:")
print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
print(f"HTTPS_PROXY: {os.getenv('HTTPS_PROXY', 'Not set')}")
print(f"HTTP_PROXY: {os.getenv('HTTP_PROXY', 'Not set')}")

# Print the OpenAI version
print(f"OpenAI version: {openai.__version__}")

# Try to initialize the OpenAI client
try:
    # Set the API key directly
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Try a different approach - use the older API format
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )
    print("API call successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}") 