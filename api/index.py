from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Ron'un Yüzü ve Arayüzü (HTML + JS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ron B-Bot AI</title>
    <style>
        body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; cursor: pointer; }
        .ron-face { text-align: center; }
        .eye { width: 80px; height: 120px; background: #fff; border-radius: 12px; display: inline-block; margin: 30px; box-shadow: 0 0 40px #fff; transition: transform 0.1s; }
        .mouth { width: 180px; height: 20px; background: #fff; border-radius: 6px; margin: 0 auto; box-shadow: 0 0 25px #fff; }
        .talking { animation: speak 0.1s infinite alternate; }
        @keyframes speak { from { height: 20px; } to { height: 75px; border-radius: 30px; } }
        .blink { transform: scaleY(0.05); }
        #status { position: fixed; bottom: 20px; color: #1a1a1a; font-family: monospace; }
    </style>
</head>
<body onclick="startRon()">
    <div class="ron-face">
        <div id="eyeL" class="eye"></div>
        <div id="eyeR" class="eye"></div>
        <div id="mouth" class="mouth"></div>
    </div>
    <div id="status">Ron Hazır - Dokun ve Konuş</div>

    <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'tr-TR';
        const mouth = document.getElementById('mouth');

        function startRon() {
            try { recognition.start(); document.getElementById('status').innerText = "Dinliyorum..."; } catch(e) {}
        }

        recognition.onresult = async (event) => {
            const query = event.results[0][0].transcript;
            document.getElementById('status').innerText = "Araştırıyorum: " + query;
            
            const res = await fetch('/api/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            });
            const data = await res.json();
            speak(data.answer);
        };

        function speak(text) {
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'tr-TR';
            utter.pitch = 0.8; // Erkek sesi (Kalınlaştırılmış)
            utter.rate = 1.3;  // Ron Gevezeliği
            
            utter.onstart = () => mouth.classList.add('talking');
            utter.onend = () => {
                mouth.classList.remove('talking');
                document.getElementById('status').innerText = "Seni Dinliyorum...";
                recognition.start();
            };
            window.speechSynthesis.speak(utter);
        }

        setInterval(() => {
            document.querySelectorAll('.eye').forEach(e => e.classList.add('blink'));
            setTimeout(() => document.querySelectorAll('.eye').forEach(e => e.classList.remove('blink')), 150);
        }, 4000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get("query", "").lower()
    
    # GERÇEK ARAŞTIRMA: Wikipedia API
    try:
        wiki_res = requests.get(f"https://tr.wikipedia.org/api/rest_v1/page/summary/{query}", timeout=5)
        wiki_data = wiki_res.json()
        if "extract" in wiki_data:
            return jsonify({"answer": wiki_data["extract"]})
    except:
        pass
    
    return jsonify({"answer": f"{query} hakkında çok gizli verilere ulaştım ama arkadaşlığımız daha önemli!"})

# Vercel için handler
def handler(event, context):
    return app(event, context)
