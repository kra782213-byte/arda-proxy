from flask import Flask, Response
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/')
def home():
    return "Ardaspor Sabit CDN Proxy Aktif!"

@app.route('/liste.m3u')
def generate_m3u():
    # Senin verdiğin CDN adresi
    CDN_BASE = "https://css.d6e3eds5e065t5.help//"
    
    # Kanallar ve o CDN'deki kısa kodları
    KANALLAR = {
        "Bein Sports 1": "b1",
        "Bein Sports 2": "b2",
        "Bein Sports 3": "b3",
        "Bein Sports 4": "b4",
        "Bein Sports 5": "b5",
        "Bein Sports Max 1": "bm1",
        "Bein Sports Max 2": "bm2",
        "S Sport 1": "s1",
        "S Sport 2": "s2",
        "S Sport Plus 1": "sp1",
        "S Sport Plus 2": "sp2",
        "TRT 1": "trt1",
        "TRT Spor": "trtspor",
        "ATV": "atv",
        "A Spor": "aspor",
        "A Haber": "ahaber",
        "TV8": "tv8",
        "Exxen Spor 1": "e1",
        "Exxen Spor 2": "e2",
        "Tabii Spor 1": "tab1",
        "Tivibu Spor 1": "tiv1",
        "Smart Spor 1": "sm1",
        "UFC": "ufc",
        "DAZN": "dazn"
    }

    m3u = "#EXTM3U\n"
    
    for isim, kod in KANALLAR.items():
        # URL'yi senin verdiğin formata birebir uyduruyoruz (çift slash dahil)
        yayin_url = f"{CDN_BASE}{kod}/tracks-v1a1/mono.m3u8"
        
        m3u += f'#EXTINF:-1 group-title="Ardaspor TV", {isim}\n'
        m3u += f'#EXTVLCOPT:http-referrer=https://ardaspor39.top/\n'
        m3u += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n'
        m3u += f'{yayin_url}\n\n'

    return Response(m3u, mimetype='application/x-mpegurl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
