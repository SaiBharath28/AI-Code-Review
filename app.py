from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from flask_cors import CORS

# Configure the Google Generative AI API key
genai.configure(api_key='AIzaSyChNg304VxhLoWXunDJr19ms5WL7j0DY5w')  # Replace with your actual API key

app = Flask(__name__)
CORS(app)

# HTML Template as a string
TEMPLATE_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Code Review</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/monokai.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1e1e2f;
            color: #ffffff;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 800px;
            background-color: #2a2a3c;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5rem;
            color: #007BFF;
        }

        .code-input, .review-output {
            margin-bottom: 20px;
        }

        textarea {
            width: 100%;
            height: 250px;
            padding: 10px;
            font-size: 16px;
            font-family: monospace;
            border: none;
            border-radius: 8px;
            background-color: #1e1e2f;
            color: #ffffff;
            resize: none;
            outline: none;
        }

        select, button {
            padding: 10px 15px;
            margin: 10px 0;
            font-size: 16px;
            border-radius: 8px;
            border: none;
            outline: none;
            cursor: pointer;
        }

        select {
            background-color: #2a2a3c;
            color: #ffffff;
        }

        button {
            background-color: #007BFF;
            color: #fff;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #0056b3;
        }

        .loading {
            display: none;
            text-align: center;
            font-size: 18px;
            color: #007BFF;
        }

        .highlighted-code, .review-result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 8px;
            background-color: #1e1e2f;
            color: #ffffff;
            overflow-x: auto;
            font-size: 14px;
        }

        .highlighted-code pre, .review-result pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Code Review</h1>
        <div class="code-input">
            <label for="language">Select Programming Language:</label>
            <select id="language">
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="c">C</option>
                <option value="cpp">C++</option>
            </select>
            <textarea id="code" placeholder="Paste your code here..."></textarea>
            <button onclick="submitCode()">Review Code</button>
            <div id="loading" class="loading">Analyzing code... Please wait...</div>
        </div>
        <div class="review-output">
            <h2>Review Results</h2>
            <div id="highlighted-code" class="highlighted-code"></div>
            <div id="review-result" class="review-result"></div>
        </div>
    </div>

    <script>
        async function submitCode() {
            const code = document.getElementById('code').value;
            const language = document.getElementById('language').value;
            const loading = document.getElementById('loading');
            const reviewResult = document.getElementById('review-result');
            const highlightedCode = document.getElementById('highlighted-code');

            if (!code.trim()) {
                alert('Please enter some code to review');
                return;
            }

            loading.style.display = 'block';
            reviewResult.innerHTML = '';
            highlightedCode.innerHTML = '';

            try {
                const response = await fetch('/review', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code, language }),
                });

                const data = await response.json();
                highlightedCode.innerHTML = data.highlighted_code;
                reviewResult.innerHTML = `<pre>${data.review}</pre>`;
            } catch (error) {
                reviewResult.innerHTML = `Error: ${error.message}`;
            } finally {
                loading.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

model = genai.GenerativeModel('gemini-pro')

def analyze_code(code, language):
    if not code.strip():
        return "Error: Empty code submitted"

    prompt = f"""
    As an expert code reviewer, analyze this {language} code:

    {code}

    Provide a detailed review including:
    1. Identify any errors (syntax, logical, or runtime)
    2. If there are errors, provide the corrected code

    Format the response in a structured way.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

def highlight_code(code, language):
    """
    Syntax highlight code for web display
    """
    try:
        lexer = get_lexer_by_name(language.lower())
        formatter = HtmlFormatter(style='monokai')
        return highlight(code, lexer, formatter)
    except Exception as e:
        return f"Error highlighting code: {str(e)}"

@app.route('/')
def index():
    return render_template_string(TEMPLATE_CONTENT)

@app.route('/review', methods=['POST'])
def review():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')

    review_result = analyze_code(code, language)
    highlighted_code = highlight_code(code, language)

    return jsonify({
        'review': review_result,
        'highlighted_code': highlighted_code
    })


if __name__ == "__main__":
    app.run(debug=True)

