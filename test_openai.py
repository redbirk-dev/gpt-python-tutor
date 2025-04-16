import openai
import os
import httpx
from dotenv import load_dotenv
from openai import OpenAI

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
    # Clear any proxy environment variables that might be causing issues
    if 'HTTP_PROXY' in os.environ:
        del os.environ['HTTP_PROXY']
    if 'HTTPS_PROXY' in os.environ:
        del os.environ['HTTPS_PROXY']

    # Create a custom httpx client without proxies
    http_client = httpx.Client(
        base_url="https://api.openai.com/v1",
        follow_redirects=True,
        timeout=30.0,
    )

    # Initialize OpenAI client with the custom http client
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        http_client=http_client
    )
    
    # Use the new API format
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )
    print("API call successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}") 