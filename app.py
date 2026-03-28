from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os
import base64
import io
from PIL import Image
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# ΝΕΟ: Εισαγωγή της βιβλιοθήκης για τη μετάφραση
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Ρύθμιση του Limiter: Συνδέει κάθε χρήστη με την IP του
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
    default_limits=["200 per day", "50 per hour"] # Γενικά όρια
)

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Η ολοκαίνουργια βιβλιοθήκη βρίσκει το σωστό Router URL αυτόματα!
client = InferenceClient(api_key=HF_TOKEN)

# Επιστρέφουμε στο Llama 3.2 που είναι το επίσημο Vision μοντέλο
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'], strict_slashes=False)
@limiter.limit("5 per minute") # Προστασία από σπαμ
def analyze():
    image_bytes = None
    
    # 1. Λήψη της εικόνας
    if 'image_file' in request.files and request.files['image_file'].filename != '':
        image_bytes = request.files['image_file'].read()
    elif 'image_url' in request.form and request.form['image_url'].strip() != '':
        try:
            url = request.form['image_url'].strip()
            
            # Πλήρη headers για να παρακάμψουμε το σφάλμα 415
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,el;q=0.8",
                "Referer": "https://www.google.com/" # Δείχνουμε ότι ήρθαμε από αναζήτηση
            }
            
            res = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            res.raise_for_status()
            image_bytes = res.content
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 415:
                return jsonify({'error': 'Το site της εικόνας αρνείται την πρόσβαση (415). Δοκίμασε να κατεβάσεις την εικόνα και να την ανεβάσεις χειροκίνητα.'}), 415
            return jsonify({'error': f'Σφάλμα λήψης (Status {e.response.status_code})'}), 400
        except Exception as e:
            return jsonify({'error': f'Αδυναμία λήψης εικόνας: {str(e)}'}), 400

    if not image_bytes:
        return jsonify({'error': 'Δεν βρέθηκε εικόνα'}), 400

    try:
        # 2. ΕΠΕΞΕΡΓΑΣΙΑ: Φιλτράρισμα μέσω Pillow για να αποφύγουμε το Error 500
        img = Image.open(io.BytesIO(image_bytes))
        
        # Μετατροπή σε RGB (αφαιρεί transparency/metadata που κρασάρουν το AI)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize: Αν η εικόνα είναι τεράστια (όπως της ΕΡΤ), την μικραίνουμε
        img.thumbnail((1024, 1024)) 
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85) # Σώζουμε ως "καθαρό" JPEG
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # 3. Αποστολή στο AI - Ζητάμε ΜΟΝΟ Αγγλικά
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Describe this image in detail. Output ONLY the English description."
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
        
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            max_tokens=600 # Μειωμένο επειδή ζητάμε μόνο μία γλώσσα
        )
        
        # Η αγγλική περιγραφή απευθείας από το AI
        desc_en = response.choices[0].message.content.strip()
        
        # 4. ΜΕΤΑΦΡΑΣΗ ΜΕ GOOGLE TRANSLATOR
        try:
            # Μεταφράζουμε το αγγλικό κείμενο σε ελληνικά
            desc_el = GoogleTranslator(source='en', target='el').translate(desc_en)
        except Exception as trans_err:
            desc_el = f"Η μετάφραση απέτυχε. Δοκίμασε ξανά. Σφάλμα: {str(trans_err)}"
            
        return jsonify({'description_en': desc_en, 'description_el': desc_el})

    except Exception as e:
        # Αν το AI συνεχίζει να βγάζει 500, σημαίνει ότι το συγκεκριμένο μοντέλο έχει θέμα τώρα
        error_msg = str(e)
        if "500" in error_msg:
            return jsonify({'error': "Ο server του AI είναι προσωρινά υπερφορτωμένος. Δοκίμασε ξανά σε λίγο!"}), 500
        return jsonify({'error': f"Σφάλμα AI: {error_msg}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)