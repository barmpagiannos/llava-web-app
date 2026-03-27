from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os
import base64
import io
from PIL import Image

app = Flask(__name__)

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Η ολοκαίνουργια βιβλιοθήκη βρίσκει το σωστό Router URL αυτόματα!
client = InferenceClient(api_key=HF_TOKEN)

# Επιστρέφουμε στο Llama 3.2 που είναι το επίσημο Vision μοντέλο
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    image_bytes = None
    
    if 'image_file' in request.files and request.files['image_file'].filename != '':
        image_bytes = request.files['image_file'].read()
    elif 'image_url' in request.form and request.form['image_url'].strip() != '':
        try:
            import requests
            # Προσθέτουμε "ταυτότητα" Browser για να μην μας μπλοκάρουν τα CDNs (π.χ. Shopify, Cloudflare)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            url = request.form['image_url'].strip()
            res = requests.get(url, headers=headers, timeout=10)
            
            # Αν το site μας έριξε "πόρτα" (π.χ. 403 Forbidden), σταματάμε εδώ
            res.raise_for_status() 
            
            image_bytes = res.content
        except Exception as e:
            return jsonify({'error': f'Το site της εικόνας μπλόκαρε τη λήψη: {str(e)}'}), 400

    if not image_bytes:
        return jsonify({'error': 'Δεν βρέθηκε εικόνα'}), 400

    try:
        # Resize & Base64
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((800, 800)) 
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Δημιουργία μηνύματος
        # Ζητάμε από το AI να μας δώσει και τις δύο γλώσσες με συγκεκριμένη δομή
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Describe this image in detail. You must output the response in two parts. First, write 'ENGLISH:' followed by the English description. Then, write 'GREEK:' followed by the exact translation in Greek."
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
        
        # Η μαγεία: Ο client κανονίζει πού και πώς θα πάει το αίτημα
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            max_tokens=800 # Το αυξήσαμε λίγο γιατί τώρα περιμένουμε διπλό κείμενο
        )
        
        full_description = response.choices[0].message.content
        
        # Διαχωρισμός των δύο γλωσσών στην Python
        desc_en = full_description
        desc_el = ""
        
        if "GREEK:" in full_description:
            parts = full_description.split("GREEK:")
            desc_en = parts[0].replace("ENGLISH:", "").strip()
            desc_el = parts[1].strip()
            
        return jsonify({'description_en': desc_en, 'description_el': desc_el})

    except Exception as e:
        return jsonify({'error': f"Σφάλμα AI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)