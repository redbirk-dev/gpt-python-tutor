from flask import Flask, request, jsonify, render_template
import openai
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()  # Load .env file

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# Set your OpenAI API key from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route to serve the frontend HTML
@app.route('/')
def index():
    return render_template('index.html')

# GPT-powered API route
@app.route('/api/gpt-python', methods=['POST'])
def gpt_python():
    data = request.get_json()
    prompt = data.get('prompt', '')

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful Python tutor. Answer clearly and give examples."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        reply = completion.choices[0].message["content"]
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
