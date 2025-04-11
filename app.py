from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gpt-python', methods=['POST'])
def ask_gpt():
    data = request.get_json()
    prompt = (
        "You are a Python tutor. Generate an intermediate to advanced multiple-choice question "
        "that includes a working Python code snippet, and has only one correct answer. "
        "Make sure the question is valid, the code runs, and the correct answer is accurate. "
        "Respond ONLY with raw JSON in this format:\n\n"
        "{"
        "\"question\": \"<Insert question that includes the code>\", "
        "\"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], "
        "\"answer\": \"A. ...\""
        "}\n\n"
        "DO NOT explain or include anything else — just JSON with the code question and options. "
        "The code should be Python 3 and focus on logic, scope, functions, or expressions. "
        "Avoid trick questions or ambiguous output. Double-check your answer."
    )

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    content = response.choices[0].message.content.strip()

    # If it's not a quiz-style prompt, return raw GPT response
    if not "options" in content or not "answer" in content:
        return jsonify({'response': content})

    # Try to parse as JSON
    try:
        question_data = json.loads(content)
        question_text = question_data["question"]
        options = question_data["options"]
        correct_answer = question_data["answer"]

        # Try to extract Python code from question
        code_match = re.search(r"`(.*?)`", question_text)
        if code_match:
            code = code_match.group(1)
            # Run the code in a safe environment
            try:
                local_vars = {}
                exec(f"output = str({code})", {}, local_vars)
                actual_output = local_vars["output"]

                # Find option that contains actual_output
                corrected_answer = None
                for opt in options:
                    if actual_output in opt:
                        corrected_answer = opt
                        break

                if corrected_answer and corrected_answer != correct_answer:
                    print(f"✅ Corrected GPT's answer from '{correct_answer}' to '{corrected_answer}'")
                    question_data["answer"] = corrected_answer

            except Exception as e:
                print(f"⚠️ Error running code: {e}")

        return jsonify({'response': json.dumps(question_data)})

    except Exception as e:
        print(f"⚠️ JSON parse error or unexpected format: {e}")
        return jsonify({'response': content})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
