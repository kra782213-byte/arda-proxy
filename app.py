from flask import Flask, Response
import curl_cffi
import urllib3
from bs4 import BeautifulSoup
import re
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

BASE_URL = "https://ardaspor39.top"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.route('/')
def home():
    return "Ardaspor Proxy Aktif! (WordPress API Modu)"

@app.route('/liste.m3u')
def generate_m3u():
    m3u = "#EXTM3U\n"
    added = 0
    
    try:
        # WordPress'in gizli JSON API'sini sorguluyoruz
        # Site maç listesini veya kanalları buradan çekiyor olabilir
        api_url = f"{BASE_URL}/wp-json/wp/v2/pages?per_page=10"
        res = curl_cffi.get(api_url, impersonate="chrome", verify=False, timeout=15)
        
        if res.status_code == 200:
            # Eğer API çalışıyorsa, dönen veriyi tarayalım
            data = res.json()
            # JSON içeriğini string'e çevirip maç/kanal isimlerini arayalım
            data_str = json.dumps(data, ensure_ascii=False)
            
            # Sitedeki kanalların isimlerini veya id'lerini yakalamaya çalışalım
            # Regex ile id veya channel linklerini ayıkla
            matches = re.findall(r'(/channel/watch/[^"\']+)', data_str)
            
            for href in set(matches):
                kanal_id = href.split('/')[-1]
                m3u += f'#EXTINF:-1 group-title="Ardaspor", {kanal_id}\n'
                m3u += f"https://arda-proxy.vercel.app/play/{kanal_id}\n"
                added += 1

        # Eğer API'den bulamadıysak, siteye normal gidip bakalım
        if added == 0:
            res = curl_cffi.get(BASE_URL, impersonate="chrome", verify=False, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/channel/watch/' in href:
                    kanal_id = href.split('/')[-1]
                    name = a.get_text(strip=True)
                    if not name: name = kanal_id
                    
                    m3u += f'#EXTINF:-1 group-title="Ardaspor", {name}\n'
                    m3u += f"https://arda-proxy.vercel.app/play/{kanal_id}\n"
                    added += 1
                    
        if added == 0:
             m3u += f'#EXTINF:-1, HATA: API ve HTML tarandi ama kanal bulunamadi\nhttp://hata\n'
             
        return Response(m3u, mimetype='application/x-mpegurl')
        
    except Exception as e:
        m3u += f'#EXTINF:-1, HATA: {str(e)}\nhttp://hata\n'
        return Response(m3u, mimetype='application/x-mpegurl')

@app.route('/play/<kanal_id>')
def play_channel(kanal_id):
    try:
        page_url = f"{BASE_URL}/channel/watch/{kanal_id}"
        page_res = curl_cffi.get(page_url, impersonate="chrome", verify=False, timeout=10)
        
        # 1. Iframe'i bul
        soup = BeautifulSoup(page_res.text, "html.parser")
        iframe = soup.find('iframe')
        
        if iframe:
            iframe_src = iframe.get('src')
            iframe_url = BASE_URL + iframe_src if iframe_src.startswith('/') else iframe_src
            
            # 2. Iframe içine gir
            iframe_res = curl_cffi.get(iframe_url, impersonate="chrome", verify=False, timeout=10)
            
            # 3. m3u8 ara
            m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', iframe_res.text)
            if m3u8_match:
                from flask import redirect
                return redirect(m3u8_match.group(1), code=302)

        return "Iframe icinde m3u8 bulunamadi.", 404
    except Exception as e:
        return f"Hata: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
