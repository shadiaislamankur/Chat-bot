from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import traceback
import openai




from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from any origin

# Enable Flask debug mode
app.config['DEBUG'] = True

# Check if nltk data is downloaded
if not os.path.exists('nltk_data'):
    nltk.download('punkt', download_dir='nltk_data')
    nltk.download('wordnet', download_dir='nltk_data')

# Set your OpenAI API key
openai.api_key = "API_KEY"

# For normal mode
def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)

def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data: dict = json.load(file)
        return data
    except FileNotFoundError:
        return {"questions": []}  # Returning an empty knowledge base structure

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match_tfidf(user_question, questions):
    if not questions:
        return None  # No questions in the knowledge base

    preprocessed_user_question = preprocess_text(user_question)

    # Check similarity only if there are questions in the knowledge base
    similarities = []
    for q in questions:
        preprocessed_question = preprocess_text(q["question"])
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([preprocessed_question, preprocessed_user_question])

        cosine_similarity_value = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        similarities.append(cosine_similarity_value)

    best_match_index = similarities.index(max(similarities))

    if similarities[best_match_index] < 0.3:
        return None

    return questions[best_match_index]["answer"]

# For turbo mode
def get_chatGPT_response(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Error in get_chatGPT_response:", e)
        return "Error in Turbo mode. Please check the logs."

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.route('/api/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data['question']
        mode = data.get('mode', 'turbo')

        knowledge_base = load_knowledge_base('load_knowledge_base.json')

        if mode == 'normal':
            if knowledge_base["questions"]:
                best_match = find_best_match_tfidf(question, knowledge_base["questions"])
                if best_match:
                    answer = best_match
                else:
                    answer = "I'm not sure how to answer that. Can you ask something else?"
            else:
                answer = "I don't have any knowledge base entries. Please add some questions and answers."
        elif mode == 'turbo':
            print("Hello")
            answer = get_chatGPT_response(question)
        else:
            return jsonify({"error": "Invalid mode"}), 400

        return jsonify({"answer": answer})

    except Exception as e:
        traceback.print_exc()  # Print traceback to console for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/api/update_knowledge_base', methods=['POST'])
def update_knowledge_base():
    try:
        data = request.json
        question = data['question']
        new_answer = data['answer']

        # Load the current knowledge base
        knowledge_base = load_knowledge_base('load_knowledge_base.json')
        existing_answer = find_best_match_tfidf(question, knowledge_base["questions"])

        if existing_answer:
            return jsonify({"message": "Similar question already exists in the knowledge base", "answer": existing_answer})
        else:
            knowledge_base["questions"].append({"question": question, "answer": new_answer})
            save_knowledge_base('load_knowledge_base.json', knowledge_base)
            return jsonify({"message": "Knowledge base updated successfully"})

    except Exception as e:
        traceback.print_exc()  # Print traceback to console for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
