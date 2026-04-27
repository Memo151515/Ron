from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Ron'un Yüzü (HTML + JS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ron B-Bot AI</title>
    <style>
        body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; cursor: pointer; }
        .eye { width: 80px; height: 120px; background: #fff; border-radius: 12px; display: inline-block; margin: 30px; box-shadow: 0 0 40px #fff; }
        .mouth { width: 180px; height: 20px; background: #fff; border-radius: 6px; margin: 0 auto; box-shadow: 0 0 25px #fff; }
        .talking { animation: speak 0.1s infinite alternate; }
        @keyframes speak { from { height: 20px; } to { height: 75px; border-radius: 30px; } }
        .blink { transform: scaleY(0.05); }
    </style>
</head>
<body onclick="startRon()">
    <div style="text-align: center;">
        <div class="eye" id="eL"></div>
        <div class="eye" id="eR"></div>
        <div id="mouth" class="mouth"></div>
    </div>
    <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'tr-TR';
        
        function startRon() { recognition.start(); }

        recognition.onresult = async (event) => {
            const query = event.results[0][0].transcript;
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
            utter.pitch = 0.8; // Erkek sesi
            utter.rate = 1.3;
            utter.onstart = () => document.getElementById('mouth').classList.add('talking');
            utter.onend = () => {
                document.getElementById('mouth').classList.remove('talking');
                recognition.start();
            };
            window.speechSynthesis.speak(utter);
        }

        setInterval(() => {
            document.getElementById('eL').classList.add('blink');
            document.getElementById('eR').classList.add('blink');
            setTimeout(() => {
                document.getElementById('eL').classList.remove('blink');
                document.getElementById('eR').classList.remove('blink');
            }, 150);
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
    try:
        # Wikipedia'dan veri çekme
        r = requests.get(f"https://tr.wikipedia.org/api/rest_v1/page/summary/{query}", timeout=5)
        if r.status_code == 200:
            return jsonify({"answer": r.json().get("extract", "Bunu biliyorum ama anlatması uzun sürer!")})
    except:
        pass
    return jsonify({"answer": f"{query} hakkında internette çok garip şeyler var, tam Ron'luk bir durum!"})

# BU SATIR ÖNEMLİ: Vercel'in Flask'ı görmesini sağlar
if __name__ == "__main__":
    app.run()
