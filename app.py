from flask import Flask, Response
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
    return "Ardaspor Proxy Aktif! (Guncel)"

@app.route('/liste.m3u')
def generate_m3u():
    m3u = "#EXTM3U\n"
    try:
        res = curl_cffi.get(BASE_URL, impersonate="chrome", verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        
        added = 0
        # Sayfadaki tüm linkleri tara
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Kanal yayın linki barındıran href'leri ara
            if '/channel/' in href:
                name_el = a.find('div', class_='match-title') or a.find('h3') or a.find('span')
                name = name_el.get_text(strip=True) if name_el else "Ardaspor Kanal"
                if len(name) < 3: continue
                
                kanal_id = href.split('/')[-1]
                m3u += f'#EXTINF:-1 group-title="Ardaspor", {name}\n'
                m3u += f"https://arda-proxy.vercel.app/play/{kanal_id}\n"
                added += 1
                
        if added == 0:
            m3u += f'#EXTINF:-1, HATA: Site JavaScript ile yuklendigi icin liste cekilemedi\nhttp://hata\n'
            
        return Response(m3u, mimetype='application/x-mpegurl')
    except Exception as e:
        m3u += f'#EXTINF:-1, HATA: {str(e)}\nhttp://hata\n'
        return Response(m3u, mimetype='application/x-mpegurl')

@app.route('/play/<kanal_id>')
def play_channel(kanal_id):
    try:
        page_url = f"{BASE_URL}/channel/watch/{kanal_id}"
        page_res = curl_cffi.get(page_url, impersonate="chrome", verify=False, timeout=10)
        soup = BeautifulSoup(page_res.text, "html.parser")
        iframe = soup.find('iframe')
        
        if not iframe:
            return "Iframe bulunamadi.", 404
            
        iframe_src = iframe.get('src')
        iframe_url = BASE_URL + iframe_src if iframe_src.startswith('/') else iframe_src

        iframe_res = curl_cffi.get(iframe_url, impersonate="chrome", verify=False, timeout=10)
        m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', iframe_res.text)
        
        if m3u8_match:
            from flask import redirect
            return redirect(m3u8_match.group(1), code=302)
            
        return "Iframe icinde m3u8 bulunamadi.", 404
    except Exception as e:
        return f"Hata: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
