from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from groq import Groq
import os
import urllib.parse

# load_dotenv reads .env file and loads GROQ_API_KEY into our program
load_dotenv()

app = Flask(__name__)

# Connect to Groq AI — it's like opening a phone line to their AI
# Groq uses Llama3 model which is super fast and completely free!
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

# ── Route 1: Simple Image Generation ──
# User types idea → Groq makes it detailed → Pollinations paints it
@app.route('/generate', methods=['POST'])
def generate():
    data   = request.json
    prompt = data.get('prompt', '')

    try:
        # Step 1: Send user's simple idea to Groq/Llama3
        # Llama3 will make it more artistic and detailed
        # Example: "cat" → "A majestic orange tabby cat sitting on moonlit rooftop..."
        enhanced = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Create a detailed, vivid, artistic image generation prompt based on: '{prompt}'. Make it descriptive and beautiful. Just the prompt, nothing else. Max 80 words."
            }]
        )
        enhanced_prompt = enhanced.choices[0].message.content.strip()

        # Step 2: Send enhanced prompt to Pollinations.ai
        # Pollinations is FREE — we just build a URL and it returns an image!
        # No API key needed — just call the URL directly
        encoded   = urllib.parse.quote(enhanced_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true&seed={abs(hash(prompt)) % 99999}"

        return jsonify({
            'success':         True,
            'image_url':       image_url,
            'enhanced_prompt': enhanced_prompt
        })

    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) })


# ── Route 2: Psychology Mind Analysis ──
# 5 answers → Groq analyses personality → creates mind image → Pollinations paints it
@app.route('/analyze', methods=['POST'])
def analyze():
    data      = request.json
    answers   = data.get('answers', [])
    questions = data.get('questions', [])

    try:
        # Build question-answer pairs for Groq to read
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])

        # Ask Groq/Llama3 to:
        # 1. Write a deep personality reading
        # 2. Create an artistic image prompt of their inner mind
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""You are a deep psychological analyst and artist.
Based on these answers, do exactly 2 things:

{qa_text}

1. Write a powerful personal personality reading (3-4 sentences). Make it feel like you truly know them. Start with "You are..."
2. Create a vivid poetic artistic image prompt that represents their inner mind and soul visually.

Respond in EXACTLY this format, nothing else:
PERSONALITY: [your personality reading]
IMAGE_PROMPT: [your artistic image prompt]"""
            }]
        )
        text = response.choices[0].message.content.strip()

        # Parse response into personality and image prompt
        if "PERSONALITY:" in text and "IMAGE_PROMPT:" in text:
            personality  = text.split("PERSONALITY:")[1].split("IMAGE_PROMPT:")[0].strip()
            image_prompt = text.split("IMAGE_PROMPT:")[1].strip()
        else:
            personality  = text[:400]
            image_prompt = f"Abstract surreal art of inner mind, {answers[0]}, soul visualization, digital art"

        # Generate mind image using Pollinations
        encoded   = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true"

        return jsonify({
            'success':      True,
            'personality':  personality,
            'image_url':    image_url,
            'image_prompt': image_prompt
        })

    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)