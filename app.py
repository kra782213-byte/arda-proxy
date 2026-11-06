from flask import Flask, Response
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/')
def home():
    return "Ardaspor Sabit Bein Sports Proxy Aktif!"

@app.route('/liste.m3u')
def generate_m3u():
    # Senin bulduğun ve Bein Sports'ların çalıştığını KESİN olarak bildiğimiz CDN
    CDN_BASE = "https://css.d6e3eds5e065t5.help//"
    
    # Sadece çalıştığını bildiğimiz kodlar
    KANALLAR = {
        "Bein Sports 1": "b1",
        "Bein Sports 2": "b2",
        "Bein Sports 3": "b3",
        "Bein Sports 4": "b4",
        "Bein Sports 5": "b5",
        "Bein Sports Max 1": "bm1",
        "Bein Sports Max 2": "bm2"
    }

    m3u = "#EXTM3U\n"
    
    for isim, kod in KANALLAR.items():
        yayin_url = f"{CDN_BASE}{kod}/tracks-v1a1/mono.m3u8"
        
        m3u += f'#EXTINF:-1 group-title="Ardaspor TV", {isim}\n'
        m3u += f'#EXTVLCOPT:http-referrer=https://ardaspor39.top/\n'
        m3u += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n'
        m3u += f'{yayin_url}\n\n'

    return Response(m3u, mimetype='application/x-mpegurl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
