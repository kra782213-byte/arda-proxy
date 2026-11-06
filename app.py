from flask import Flask, Response, redirect
import curl_cffi
import urllib3
from bs4 import BeautifulSoup
import re
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

BASE_URL = "https://ardaspor39.top"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.route('/')
def home():
    return "Ardaspor Dinamik Proxy Aktif!"

@app.route('/liste.m3u')
def generate_m3u():
    try:
        # Siteye git ve maç/kanal listesini çek
        res = curl_cffi.get(BASE_URL, impersonate="chrome", verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        
        m3u = "#EXTM3U\n"
        added = 0
        
        # Sayfadaki tüm "channel" linklerini bul (Maç listesi burada)
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/channel/' in href:
                # Maçın/kanalın adını al
                name_el = a.find('div', class_='match-title') or a.find('h3') or a.find('span')
                name = name_el.get_text(strip=True) if name_el else "Maç / Kanal"
                
                # Eğer isim çok kısaysa veya boşsa atla
                if len(name) < 3: continue
                
                # Kanal ID'sini linkten al (örn: /channel/watch/bein-sports-1 -> bein-sports-1)
                kanal_id = href.split('/')[-1]
                
                m3u += f'#EXTINF:-1 group-title="Ardaspor", {name}\n'
                # Vercel'in kendi linkini veriyoruz
                m3u += f"https://ardaspor-proxy.vercel.app/play/{kanal_id}\n"
                added += 1
                
        return Response(m3u, mimetype='application/x-mpegurl')
    except Exception as e:
        return f"Liste hatasi: {e}", 500

@app.route('/play/<kanal_id>')
def play_channel(kanal_id):
    try:
        # 1. Kanal sayfasına git (/channel/watch/...)
        page_url = f"{BASE_URL}/channel/watch/{kanal_id}"
        page_res = curl_cffi.get(page_url, impersonate="chrome", verify=False, timeout=10)
        
        # 2. Sayfa içindeki iframe'i bul (Oynatıcı linki)
        soup = BeautifulSoup(page_res.text, "html.parser")
        iframe = soup.find('iframe')
        
        if not iframe:
            return "Iframe bulunamadi.", 404
            
        iframe_src = iframe.get('src')
        # Eğer iframe linki göreceliyse tam link yap
        if iframe_src.startswith('/'):
            iframe_url = BASE_URL + iframe_src
        else:
            iframe_url = iframe_src

        # 3. Iframe'in içine gir (loadstream.php)
        iframe_res = curl_cffi.get(iframe_url, impersonate="chrome", verify=False, timeout=10)
        
        # 4. Iframe içinde m3u8 ara (veya oynatıcının linkini)
        # Bazen link direkt gelir, bazen JS içinde gizlidir
        m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', iframe_res.text)
        
        if m3u8_match:
            stream_url = m3u8_match.group(1)
            return redirect(stream_url, code=302)
            
        # Eğer m3u8 bulunamazsa, belki oynatıcı linki bir değişkendedir
        # Site "Volestream" kullanıyorsa, oynatıcı linkini çekmeye çalışalım
        # (Örnek: https://css.d6e3eds5e065t5.help//b1/tracks-v1a1/mono.m3u8)
        # Bu tür durumlarda iframe sayfasındaki gizli ID'yi bulup yönlendirebiliriz.
        # Şimdilik en basit haliyle iframe'in kaynağını döndürelim, IPTV açmazsa geliştiririz.
        
        return f"Iframe bulundu ama m3u8 yok. Iframe URL: {iframe_url}", 404
        
    except Exception as e:
        return f"Hata: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
