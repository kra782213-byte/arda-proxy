from flask import Flask, Response
import urllib3
import requests
import concurrent.futures

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/')
def home():
    return "Ardaspor Akilli Test Motoru Aktif!"

def test_kanal(kod, isim):
    # Senin bulduğun CDN sunucusu
    url = f"https://css.d6e3eds5e065t5.help//{kod}/tracks-v1a1/mono.m3u8"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        # Sadece başlığı kontrol et (videoyu indirme)
        res = requests.head(url, headers=headers, timeout=3, verify=False)
        if res.status_code == 200:
            return (isim, url)
    except:
        pass
    return None

@app.route('/liste.m3u')
def generate_m3u():
    m3u = "#EXTM3U\n"
    
    # Olası tüm kanal isimleri ve tahmini kodları
    KANAL_LISTESI = {
        "Bein Sports 1": ["b1"],
        "Bein Sports 2": ["b2"],
        "Bein Sports 3": ["b3"],
        "Bein Sports 4": ["b4"],
        "Bein Sports 5": ["b5"],
        "Bein Sports Max 1": ["bm1", "bmax1"],
        "Bein Sports Max 2": ["bm2", "bmax2"],
        "S Sport 1": ["ss"],
        "S Sport 2": ["ss2"],
        "S Sport Plus 1": ["sp1", "splus1"],
        "S Sport Plus 2": ["sp2", "splus2"],
        "TRT 1": ["trt1", "trt", "t1"],
        "TRT Spor": ["trtspor", "tspor"],
        "ATV": ["atv", "a1"],
        "A Spor": ["aspor", "as1"],
        "A Haber": ["ahaber", "ah1"],
        "TV8": ["tv8"],
        "TV 8.5": ["tv85", "tv8.5"],
        "Exxen Spor 1": ["exxen1", "e1", "exxen"],
        "Exxen Spor 2": ["exxen2", "e2"],
        "Tabii Spor 1": ["tabii1", "tab1"],
        "Tivibu Spor 1": ["tivibu1", "tiv1"],
        "UFC": ["ufc", "u1"],
        "DAZN": ["dazn", "d1"]
    }

    # Test edilecek görevleri hazırla
    tasks = []
    for isim, kodlar in KANAL_LISTESI.items():
        for kod in kodlar:
            tasks.append((kod, isim))

    # Aynı anda 10 kanalı test et (Hız için)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_kanal, kod, isim) for kod, isim in tasks]
        
        bulunanlar = {}
        for future in concurrent.futures.as_completed(futures):
            sonuc = future.result()
            if sonuc:
                isim, url = sonuc
                if isim not in bulunanlar:
                    bulunanlar[isim] = url

    # Bulunanları listeye ekle
    for isim, url in bulunanlar.items():
        m3u += f'#EXTINF:-1 group-title="Ardaspor TV", {isim}\n'
        m3u += f'#EXTVLCOPT:http-referrer=https://ardaspor39.top/\n'
        m3u += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n'
        m3u += f'{url}\n\n'

    if not bulunanlar:
        m3u += f'#EXTINF:-1, HATA: Hicbir kanal kodu tutmadi\nhttp://hata\n'

    return Response(m3u, mimetype='application/x-mpegurl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
