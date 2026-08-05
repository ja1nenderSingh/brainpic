from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from groq import Groq
import os
import urllib.parse

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data   = request.json
    prompt = data.get('prompt', '')
    try:
        enhanced = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Create a detailed, vivid, artistic image generation prompt based on: '{prompt}'. Make it descriptive and beautiful. Just the prompt, nothing else. Max 80 words."
            }]
        )
        enhanced_prompt = enhanced.choices[0].message.content.strip()
        encoded   = urllib.parse.quote(enhanced_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true&seed={abs(hash(prompt)) % 99999}"
        return jsonify({
            'success':         True,
            'image_url':       image_url,
            'enhanced_prompt': enhanced_prompt
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze', methods=['POST'])
def analyze():
    data      = request.json
    answers   = data.get('answers', [])
    questions = data.get('questions', [])
    try:
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""You are the world's most insightful psychological profiler. You don't just read answers — you read what's BEHIND the answers. You find what people are hiding even from themselves.

Here are someone's answers:

{qa_text}

Your job:
1. Write a DEEP psychological personality reading (4-5 sentences). 
- DO NOT just repeat or paraphrase their answers
- Read BETWEEN the lines
- Be specific, surprising, and profound
- Start with "You are..." but go DEEP

2. Create a vivid, surreal, artistic image prompt that represents their SUBCONSCIOUS mind.

Respond in EXACTLY this format:
PERSONALITY: [your deep psychological reading]
IMAGE_PROMPT: [your surreal artistic image prompt]"""
            }]
        )
        text = response.choices[0].message.content.strip()
        if "PERSONALITY:" in text and "IMAGE_PROMPT:" in text:
            personality  = text.split("PERSONALITY:")[1].split("IMAGE_PROMPT:")[0].strip()
            image_prompt = text.split("IMAGE_PROMPT:")[1].strip()
        else:
            personality  = text[:400]
            image_prompt = f"Abstract surreal art of inner mind, {answers[0]}, soul visualization"

        encoded   = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true"
        return jsonify({
            'success':      True,
            'personality':  personality,
            'image_url':    image_url,
            'image_prompt': image_prompt
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)