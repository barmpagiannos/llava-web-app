# VisualSense AI
**VisualSense AI** is a professional-grade web application that leverages state-of-the-art Vision Language Models (VLM) to analyze images and provide detailed descriptions in both **English** and **Greek**. 
By combining the reasoning power of **Qwen 2.5 VL** with the accuracy of **Google Translation**, this tool offers a seamless experience for understanding visual content with native-level linguistic support.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow?style=for-the-badge)
![Render](https://img.shields.io/badge/Render-%2346E3B7.svg?style=for-the-badge&logo=render&logoColor=white)

---

## Key Features

- **Advanced Image Analysis**: Powered by `Qwen/Qwen2.5-VL-7B-Instruct` for high-fidelity descriptions and scene understanding.
- **Native Greek Support**: Integrated `deep-translator` (Google Engine) ensures natural and accurate Greek translations.
- **Dual Input Methods**: Seamlessly handles local image uploads and direct image URLs.
- **Smart Preprocessing**: Automatic image sanitization (RGB conversion and intelligent resizing) using `Pillow` to prevent server errors (500) from large or corrupted metadata.
- **Rate Limiting & Security**: Built-in protection against automated spam using `Flask-Limiter` (IP-based rules).
- **Modern UI/UX**: Clean, responsive interface with pulse-animated loading states and instant image previews.

---

## Technical Architecture

1. **Frontend**: HTML5/CSS3 with a focus on usability. Includes client-side image preview and dynamic error handling.
2. **Backend**: Flask (Python) manages API routing, environment security, and image processing.
3. **AI Layer**: Communicates with the **Hugging Face Inference API** using the modern `InferenceClient` (OpenAI-compatible routing).
4. **Resilience**: Implements custom request headers (User-Agent/Referer) to bypass 415/403 errors when fetching images from protected CDNs (Shopify, WordPress, etc.).

---

## Local Installation & Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/barmpagiannos/llava-web-app.git
   cd llava-web-app
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Set up Environment Variables:**

   Create a `.env` file in the root directory and add your Hugging Face Token:
```
   HF_TOKEN=your_hugging_face_token_here
```

4. **Run the application:**
```bash
   python app.py
```
   Open `http://localhost:5000` in your browser.

---

## Deployment on Render

This project is optimized for deployment on the [Render](https://render.com) platform as a **Web Service**.

| Setting | Value |
|---|---|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

**Required Environment Variables:**

| Variable | Description |
|---|---|
| `HF_TOKEN` | Your Hugging Face API Key |
| `PYTHON_VERSION` | `3.12.8` *(Recommended for library compatibility)* |

---

## License

Distributed under the **Apache 2.0 License**. This project is intended for portfolio demonstration and educational purposes.

---

*Developed as a high-performance AI Portfolio Project.*
