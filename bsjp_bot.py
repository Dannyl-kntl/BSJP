# ===== BSJP SCAN SORE - OTOMATIS KIRIM KE TELEGRAM =====
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# --- 🔴 GANTI DENGAN TOKEN BARU KAMU (JANGAN SHARE!) ---
TOKEN = "8995282419:AAFwTHBBsboWgKBb2B83RwTcrJVyovZQKV8"   # Ganti dengan Token baru dari BotFather
CHAT_ID = "8995282419"      # ID kamu (ini aman, tapi tetap ganti kalau mau)
# ---------------------------------------------------------

# DAFTAR SAHAM IDX (Top 15 likuid)
LIST_SAHAM = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK',
    'UNVR.JK', 'GOTO.JK', 'BYAN.JK', 'ADRO.JK', 'MEDC.JK',
    'CUAN.JK', 'BREN.JK', 'DSSA.JK', 'AGII.JK', 'ENRG.JK'
]

def kirim_pesan(pesan):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={'chat_id': CHAT_ID, 'text': pesan, 'parse_mode': 'Markdown'}, timeout=10)
    except Exception as e:
        print(f"Error kirim: {e}")

def ambil_sentimen_sederhana(kode):
    """Cek sentimen dari nama saham (backup jika gagal scrap)"""
    try:
        saham = yf.Ticker(kode)
        nama = saham.info.get('longName', '')
        keyword_positif = ['naik', 'rekor', 'laba', 'dividen', 'ekspansi']
        keyword_negatif = ['turun', 'rugi', 'utang', 'krisis', 'delisting']
        
        # Cek deskripsi singkat
        desc = str(saham.info.get('longBusinessSummary', '')).lower()
        pos = sum(1 for k in keyword_positif if k in desc)
        neg = sum(1 for k in keyword_negatif if k in desc)
        if pos > neg: return "📰 Sentimen: Cenderung Positif"
        if neg > pos: return "📰 Sentimen: Cenderung Negatif"
        return "📰 Sentimen: Netral"
    except:
        return "📰 Sentimen: - (tidak tersedia)"

def analisis_bsjp(kode):
    try:
        saham = yf.Ticker(kode)
        df = saham.history(period="120d")
        if df.empty or len(df) < 50:
            return None
        
        info = saham.info
        
        # Hitung indikator
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Volume
        avg_vol_5 = df['Volume'].rolling(5).mean().iloc[-1]
        avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
        vol_hari_ini = last['Volume']
        
        # Persyaratan BSJP
        harga = last['Close']
        perubahan = ((harga - prev['Close']) / prev['Close']) * 100
        
        kondisi_teknikal = (
            harga > last['MA20'] and
            50 < last['RSI'] < 75 and
            perubahan > 0
        )
        
        kondisi_volume = (vol_hari_ini > avg_vol_5 * 1.5) or (vol_hari_ini > avg_vol_20 * 2.0)
        
        # Fundamental
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        market_cap = info.get('marketCap', 0)
        if market_cap > 0:
            market_cap = f"Rp{market_cap/1e12:.2f}T"
        else:
            market_cap = "N/A"
        
        # === LOGIKA BSJP ===
        if kondisi_teknikal and kondisi_volume:
            atr = last['ATR']
            sl = round(harga - (1.5 * atr), 2)
            tp1 = round(harga + (2 * atr), 2)
            tp2 = round(harga + (3.5 * atr), 2)
            signal = "🚀 ENTRY SORE"
            rekom = "Beli sore ini, jual besok pagi"
        else:
            sl = tp1 = tp2 = None
            signal = "⏳ Tahan Diri"
            rekom = "Belum memenuhi syarat"
        
        # Sentimen
        sentimen = ambil_sentimen_sederhana(kode)
        
        return {
            'kode': kode.replace('.JK', ''),
            'nama': info.get('shortName', kode)[:25],
            'harga': harga,
            'perubahan': perubahan,
            'volume': int(vol_hari_ini),
            'avg_vol_5': int(avg_vol_5),
            'rsi': round(last['RSI'], 2),
            'ma20': round(last['MA20'], 2),
            'signal': signal,
            'rekom': rekom,
            'sl': sl,
            'tp1': tp1,
            'tp2': tp2,
            'pe': pe,
            'pb': pb,
            'market_cap': market_cap,
            'sentimen': sentimen,
            'is_bsjp': kondisi_teknikal and kondisi_volume
        }
    except Exception as e:
        return None

# ===== JALANKAN SCAN =====
waktu = datetime.now().strftime('%d-%m-%Y %H:%M')
print(f"Scan sore dimulai: {waktu}")

semua_hasil = []
for kode in LIST_SAHAM:
    res = analisis_bsjp(kode)
    if res:
        semua_hasil.append(res)

# Pisahkan sinyal
sinyal_hidup = [h for h in semua_hasil if h['is_bsjp']]
sinyal_mati = [h for h in semua_hasil if not h['is_bsjp']]

# === BUAT PESAN TELEGRAM ===
pesan = f"📊 *BSJP SCAN SORE - {waktu}*\n"
pesan += f"📌 Total: {len(semua_hasil)} saham | 🔥 Sinyal: {len(sinyal_hidup)}\n"
pesan += "=" * 30 + "\n\n"

if sinyal_hidup:
    pesan += "🔥 *DAFTAR BSJP (ENTRY SORE)* 🔥\n\n"
    for h in sinyal_hidup:
        pesan += f"🏢 *{h['kode']}* - {h['nama']}\n"
        pesan += f"💰 Rp{h['harga']:.0f} | 📈 {h['perubahan']:+.2f}%\n"
        pesan += f"📊 RSI: {h['rsi']} | MA20: Rp{h['ma20']:.0f}\n"
        pesan += f"📦 Vol: {h['volume']:,} (Rata2 5H: {h['avg_vol_5']:,})\n"
        pesan += f"💡 *Rekomendasi:* {h['rekom']}\n"
        pesan += f"🔴 *SL:* Rp{h['sl']} | 🟢 *TP1:* Rp{h['tp1']} | 🟢 *TP2:* Rp{h['tp2']}\n"
        pesan += f"📋 PE: {h['pe']} | PB: {h['pb']} | Kap: {h['market_cap']}\n"
        pesan += f"{h['sentimen']}\n"
        pesan += "-" * 25 + "\n"
else:
    pesan += "⏳ *Belum ada saham BSJP hari ini.*\n"
    pesan += "Tidak ada sinyal entry sore.\n\n"

# Tambahkan 3 saham dengan RSI tertinggi untuk pantauan
pesan += "📈 *Pantauan (RSI Tertinggi):*\n"
urut_rsi = sorted(sinyal_mati, key=lambda x: x['rsi'], reverse=True)[:3]
for h in urut_rsi:
    pesan += f"🔹 {h['kode']} (RSI: {h['rsi']}) - Rp{h['harga']:.0f}\n"

# Kirim ke Telegram
kirim_pesan(pesan)
print("✅ Selesai! Cek Telegram.")
