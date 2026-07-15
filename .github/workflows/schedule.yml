# ===== BSJP SCAN SORE - VERSI DOWNLOAD MASSAL (PASTI DAPAT DATA) =====
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ========== GANTI DENGAN DATA ASLI KAMU ==========
TOKEN = "8995282419:AAHGtJIb3oeJHtf0LmmeSIpMNpNwjXv1ZK4"
CHAT_ID = "8467853860"
# =================================================

LIST_SAHAM = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK',
    'UNVR.JK', 'GOTO.JK', 'BYAN.JK', 'ADRO.JK', 'MEDC.JK',
    'CUAN.JK', 'BREN.JK', 'DSSA.JK', 'AGII.JK', 'ENRG.JK'
]

def kirim_pesan(pesan):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        resp = requests.get(url, params={
            'chat_id': CHAT_ID,
            'text': pesan,
            'parse_mode': 'HTML'
        }, timeout=15)
        if resp.status_code == 200:
            print("✅ Pesan terkirim!")
        else:
            print(f"❌ Error: {resp.status_code} | {resp.text}")
    except Exception as e:
        print(f"❌ Gagal kirim: {e}")

def cek_data_fresh(df):
    last_date = df.index[-1].date()
    today_date = datetime.now().date()
    if last_date == today_date:
        return "✅ Data Fresh (Hari Ini)", ""
    elif today_date.weekday() >= 5:
        return "🟡 Pasar Libur (Data Jumat)", ""
    else:
        return f"⚠️ DATA TELAT! (Data: {last_date})", f"⚠️ PERINGATAN: Harga yang dipakai adalah harga {last_date}!"

def scrape_berita_google(kode):
    try:
        saham = yf.Ticker(kode)
        nama = saham.info.get('shortName', kode.replace('.JK', ''))
        url = f"https://news.google.com/search?q={nama.replace(' ', '+')}+saham"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            text = resp.text.lower()
            pos = ['naik','melesat','rekor','laba','dividen','ekspansi','akuisisi']
            neg = ['turun','anjlok','rugi','utang','krisis','skandal','warning']
            p = sum(1 for k in pos if k in text)
            n = sum(1 for k in neg if k in text)
            if p > n: return "📰 Sentimen: Positif (Buy on Rumor)"
            if n > p: return "📰 Sentimen: Negatif (Sell on News)"
            return "📰 Sentimen: Netral"
        return "📰 Tidak ada berita"
    except:
        return "📰 Gagal scrape"

def cek_foreign_flow():
    try:
        url = "https://www.cnbcindonesia.com/market"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            text = resp.text.lower()
            if 'net foreign buy' in text or 'asing serok' in text:
                return "🌏 Asing: Net Buy (Positif)"
            elif 'net foreign sell' in text or 'asing obral' in text:
                return "🌏 Asing: Net Sell (Negatif)"
        return "🌏 Asing: Data tidak tersedia"
    except:
        return "🌏 Asing: Error"

# ========== FUNGSI ANALISIS DENGAN DOWNLOAD MASSAL ==========
def analisis_massal():
    hasil = []
    print("📥 Mengunduh data 15 saham sekaligus...")
    
    try:
        # DOWNLOAD MASSAL (1 kali panggil)
        data = yf.download(
            tickers=LIST_SAHAM,
            period="120d",
            group_by='ticker',
            threads=False,
            progress=False
        )
    except Exception as e:
        print(f"❌ Gagal download massal: {e}")
        return []
    
    for kode in LIST_SAHAM:
        try:
            if kode not in data or data[kode].empty:
                print(f"⚠️ Data kosong untuk {kode}")
                continue
            
            df = data[kode].copy()
            if len(df) < 50:
                print(f"⚠️ Data kurang untuk {kode} (hanya {len(df)} hari)")
                continue
            
            info = yf.Ticker(kode).info
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Hitung indikator
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['MA20'] = ta.sma(df['Close'], length=20)
            df['MA50'] = ta.sma(df['Close'], length=50)
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            # Ambil nilai terakhir
            rsi = df['RSI'].iloc[-1]
            ma20 = df['MA20'].iloc[-1]
            atr = df['ATR'].iloc[-1]
            harga = last['Close']
            perubahan = ((harga - prev['Close']) / prev['Close']) * 100
            
            # Volume
            vol_hari = last['Volume']
            avg_vol_5 = df['Volume'].rolling(5).mean().iloc[-1]
            avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
            
            # Kondisi BSJP
            kondisi_teknikal = (
                harga > ma20 and
                50 < rsi < 75 and
                perubahan > 0
            )
            kondisi_volume = (vol_hari > avg_vol_5 * 1.5) or (vol_hari > avg_vol_20 * 2.0)
            is_bsjp = kondisi_teknikal and kondisi_volume
            
            # Data Fresh
            data_status, data_warning = cek_data_fresh(df)
            
            # SL & TP
            if is_bsjp and atr:
                sl = round(harga - (1.5 * atr), 2)
                tp1 = round(harga + (2 * atr), 2)
                tp2 = round(harga + (3.5 * atr), 2)
            else:
                sl = tp1 = tp2 = None
            
            # Fundamental
            pe = info.get('trailingPE', 'N/A')
            pb = info.get('priceToBook', 'N/A')
            market_cap = info.get('marketCap', 0)
            kap_str = f"Rp{market_cap/1e12:.2f}T" if market_cap > 0 else "N/A"
            
            # Berita & Foreign
            sentimen = scrape_berita_google(kode)
            foreign = cek_foreign_flow()
            
            hasil.append({
                'kode': kode.replace('.JK', ''),
                'nama': info.get('shortName', kode)[:25],
                'harga': harga,
                'perubahan': perubahan,
                'rsi': round(rsi, 2),
                'ma20': round(ma20, 2),
                'volume': int(vol_hari),
                'avg_vol_5': int(avg_vol_5),
                'data_status': data_status,
                'data_warning': data_warning,
                'sentimen': sentimen,
                'foreign': foreign,
                'sl': sl,
                'tp1': tp1,
                'tp2': tp2,
                'pe': pe,
                'pb': pb,
                'kap': kap_str,
                'is_bsjp': is_bsjp
            })
            
            print(f"✅ {kode} -> RSI: {rsi:.1f}, BSJP: {is_bsjp}")
            
        except Exception as e:
            print(f"❌ Error proses {kode}: {e}")
    
    return hasil

# ========== MAIN ==========
waktu = datetime.now().strftime('%d-%m-%Y %H:%M')
print(f"🚀 BSJP SCAN SORE - {waktu}")

semua_hasil = analisis_massal()

sinyal_hidup = [h for h in semua_hasil if h['is_bsjp']]
sinyal_mati = [h for h in semua_hasil if not h['is_bsjp']]

# === SUSUN PESAN ===
pesan = f"<b>📊 BSJP SCAN SORE</b> - {waktu}\n"
pesan += f"📌 Total: {len(semua_hasil)} saham | 🔥 Sinyal: {len(sinyal_hidup)}\n"
pesan += "=" * 30 + "\n\n"

if sinyal_hidup:
    pesan += "<b>🔥 DAFTAR BSJP (ENTRY SORE)</b>\n\n"
    for h in sinyal_hidup[:5]:
        pesan += f"🏢 <b>{h['kode']}</b> - {h['nama']}\n"
        pesan += f"💰 Rp{h['harga']:.0f} | 📈 {h['perubahan']:+.2f}%\n"
        pesan += f"📅 {h['data_status']}\n"
        if h['data_warning']:
            pesan += f"⚠️ {h['data_warning']}\n"
        pesan += f"📊 RSI: {h['rsi']} | MA20: Rp{h['ma20']:.0f}\n"
        pesan += f"📦 Vol: {h['volume']:,} (Rata2 5H: {h['avg_vol_5']:,})\n"
        pesan += f"🔴 SL: Rp{h['sl']} | 🟢 TP1: Rp{h['tp1']} | 🟢 TP2: Rp{h['tp2']}\n"
        pesan += f"📋 PE: {h['pe']} | PB: {h['pb']} | Kap: {h['kap']}\n"
        pesan += h['sentimen'] + "\n"
        pesan += h['foreign'] + "\n"
        pesan += "-" * 25 + "\n"
else:
    pesan += "⏳ <b>Belum ada saham BSJP hari ini.</b>\n\n"

if sinyal_mati:
    pesan += "<b>📈 Pantauan (RSI Tertinggi):</b>\n"
    urut_rsi = sorted(sinyal_mati, key=lambda x: x['rsi'], reverse=True)[:3]
    for h in urut_rsi:
        pesan += f"🔹 {h['kode']} (RSI: {h['rsi']}) - Rp{h['harga']:.0f}\n"

# Kirim ke Telegram
kirim_pesan(pesan)
print("✅ Selesai! Cek Telegram.")
