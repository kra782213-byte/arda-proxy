from flask import Flask, Response, redirect
import curl_cffi
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

BASE_URL = "https://ardaspor39.top"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.route('/')
def home():
    return "Ardaspor Proxy Aktif! (Div Modu)"

@app.route('/liste.m3u')
def generate_m3u():
    m3u = "#EXTM3U\n"
    added = 0
    
    try:
        # Siteye git
        res = curl_cffi.get(BASE_URL, impersonate="chrome", verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Sitedeki maç/kanal kutularını bul (data-id ve data-title içeren div'ler)
        # Sitenin yapısına göre genel bir arama yapıyoruz
        items = soup.find_all('div', attrs={'data-id': True})
        
        if not items:
            # Eğer data-id yoksa, maç listesi class'larını arayalım
            items = soup.find_all('div', class_=re.compile(r'(match|channel|canli|item)', re.IGNORECASE))

        for item in items:
            # ID'yi al
            kanal_id = item.get('data-id') or item.get('data-match-id')
            if not kanal_id:
                # Eğer onclick içinde varsa oradan çek (örn: onclick="watch(12345)")
                onclick = item.get('onclick', '')
                id_match = re.search(r'(\d+)', onclick)
                if id_match:
                    kanal_id = id_match.group(1)
            
            if not kanal_id:
                continue

            # Kanal/Maç ismini al
            title_el = item.find('h3') or item.find('div', class_=re.compile(r'title', re.IGNORECASE))
            name = title_el.get_text(strip=True) if title_el else item.get_text(strip=True)[:30]
            
            if not name or len(name) < 3:
                name = f"Kanal {kanal_id}"

            m3u += f'#EXTINF:-1 group-title="Ardaspor", {name}\n'
            m3u += f"https://arda-proxy.vercel.app/play/{kanal_id}\n"
            added += 1
            
        if added == 0:
             m3u += f'#EXTINF:-1, HATA: Div yapisi bulundu ama kanal yok\nhttp://hata\n'
             
        return Response(m3u, mimetype='application/x-mpegurl')
        
    except Exception as e:
        m3u += f'#EXTINF:-1, HATA: {str(e)}\nhttp://hata\n'
        return Response(m3u, mimetype='application/x-mpegurl')

@app.route('/play/<kanal_id>')
def play_channel(kanal_id):
    try:
        # Sitenin yayın izleme linki formatı
        page_url = f"{BASE_URL}/channel/watch/{kanal_id}"
        page_res = curl_cffi.get(page_url, impersonate="chrome", verify=False, timeout=10)
        
        # 1. Iframe'i bul
        soup = BeautifulSoup(page_res.text, "html.parser")
        iframe = soup.find('iframe')
        
        if iframe:
            iframe_src = iframe.get('src')
            iframe_url = BASE_URL + iframe_src if iframe_src.startswith('/') else iframe_src
            
            # 2. Iframe içine gir (loadstream.php)
            iframe_res = curl_cffi.get(iframe_url, impersonate="chrome", verify=False, timeout=10)
            
            # 3. m3u8 ara
            m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', iframe_res.text)
            if m3u8_match:
                return redirect(m3u8_match.group(1), code=302)

        return "Iframe icinde m3u8 bulunamadi.", 404
    except Exception as e:
        return f"Hata: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
