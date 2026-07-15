# ===== BSJP SCAN SORE - VERSI UPGRADE (DATA FRESH + BERITA) =====
# Fitur: Data Fresh Check, Sentimen Google News, Pengumuman IDX, Foreign Flow

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ========== 🔴 GANTI DENGAN DATA ASLI KAMU ==========
TOKEN = "8995282419:AAHGtJIb3oeJHtf0LmmeSIpMNpNwjXv1ZK4"   # Ganti dengan token baru dari @BotFather
CHAT_ID = "8467853860"      # ID Telegram kamu
# =====================================================

# DAFTAR SAHAM IDX (Top 15 likuid) - Bisa ditambah sesuai keinginan
LIST_SAHAM = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK',
    'UNVR.JK', 'GOTO.JK', 'BYAN.JK', 'ADRO.JK', 'MEDC.JK',
    'CUAN.JK', 'BREN.JK', 'DSSA.JK', 'AGII.JK', 'ENRG.JK'
]

def kirim_pesan(pesan):
    """Kirim pesan ke Telegram dalam mode HTML"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        resp = requests.get(url, params={
            'chat_id': CHAT_ID,
            'text': pesan,
            'parse_mode': 'HTML'
        }, timeout=15)
        if resp.status_code == 200:
            print("✅ Pesan berhasil terkirim!")
        else:
            print(f"❌ Error: {resp.status_code}")
            print(f"📝 Detail: {resp.text}")
    except Exception as e:
        print(f"❌ Gagal konek: {e}")

# ==================== FUNGSI TAMBAHAN (UPGRADE) ====================

def cek_data_fresh(df):
    """
    Cek apakah data Yahoo Finance adalah hari ini atau H-1
    """
    last_date = df.index[-1].date()
    today_date = datetime.now().date()
    
    if last_date == today_date:
        return "✅ Data Fresh (Hari Ini)", ""
    elif today_date.weekday() >= 5:  # Sabtu/Minggu
        return "🟡 Pasar Libur (Data Jumat)", ""
    else:
        warning = f"⚠️ PERINGATAN: Harga yang dipakai adalah harga {last_date}, BUKAN hari ini!"
        return f"⚠️ DATA TELAT! (H-1) - Data: {last_date}", warning

def scrape_berita_google(kode):
    """Ambil sentimen berita dari Google News"""
    try:
        saham = yf.Ticker(kode)
        nama = saham.info.get('shortName', kode.replace('.JK', ''))
        search_url = f"https://news.google.com/search?q={nama.replace(' ', '+')}+saham"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(search_url, headers=headers, timeout=8)
        
        if resp.status_code == 200:
            text = resp.text.lower()
            pos = ['naik', 'melesat', 'rekor', 'laba', 'dividen', 'ekspansi', 'akuisisi']
            neg = ['turun', 'anjlok', 'rugi', 'utang', 'krisis', 'skandal', 'warning']
            
            pos_count = sum(1 for kw in pos if kw in text)
            neg_count = sum(1 for kw in neg if kw in text)
            
            if pos_count > neg_count:
                return "📰 Sentimen: Positif (Buy on Rumor)"
            elif neg_count > pos_count:
                return "📰 Sentimen: Negatif (Sell on News)"
            else:
                return "📰 Sentimen: Netral"
        return "📰 Tidak ada berita"
    except:
        return "📰 Gagal scrape berita"

def cek_pengumuman_idx(kode):
    """Cek pengumuman emiten dari IDX"""
    try:
        ticker = kode.replace('.JK', '')
        url = f"https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            text = resp.text.lower()
            keywords = {
                'dividen': '💵 Dividen',
                'right issue': '📈 Right Issue',
                'akuisisi': '🤝 Akuisisi',
                'rugi': '⚠️ Rugi',
                'laba': '📊 Laba',
                'korporasi': '🏢 Aksi Korporasi'
            }
            found = [v for k, v in keywords.items() if k in text]
            return f"📢 IDX: {', '.join(found) if found else 'Tidak ada pengumuman baru'}"
        return "📢 IDX: Gagal akses"
    except:
        return "📢 IDX: Error"

def cek_foreign_flow():
    """Cek net foreign buy/sell dari berita CNBC Indonesia"""
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

# ==================== ANALISIS UTAMA ====================

def analisis_bsjp(kode):
    try:
        saham = yf.Ticker(kode)
        df = saham.history(period="120d")
        if df.empty or len(df) < 50:
            return None
        
        info = saham.info
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # === INDIKATOR TEKNIKAL ===
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        avg_vol_5 = df['Volume'].rolling(5).mean().iloc[-1]
        avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
        vol_hari_ini = last['Volume']
        
        harga = last['Close']
        perubahan = ((harga - prev['Close']) / prev['Close']) * 100
        
        # === KRITERIA BSJP ===
        kondisi_teknikal = (
            harga > last['MA20'] and
            50 < last['RSI'] < 75 and
            perubahan > 0
        )
        kondisi_volume = (vol_hari_ini > avg_vol_5 * 1.5) or (vol_hari_ini > avg_vol_20 * 2.0)
        is_bsjp = kondisi_teknikal and kondisi_volume
        
        # === DATA FRESH & BERITA ===
        data_status, data_warning = cek_data_fresh(df)
        sentimen = scrape_berita_google(kode)
        pengumuman = cek_pengumuman_idx(kode)
        foreign = cek_foreign_flow()
        
        # === FUNDAMENTAL ===
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        market_cap = info.get('marketCap', 0)
        if market_cap > 0:
            market_cap = f"Rp{market_cap/1e12:.2f}T"
        else:
            market_cap = "N/A"
        
        # === SL & TP ===
        if is_bsjp:
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
            # === FIELD BARU ===
            'data_status': data_status,
            'data_warning': data_warning,
            'sentimen': sentimen,
            'pengumuman': pengumuman,
            'foreign': foreign,
            'is_bsjp': is_bsjp
        }
    except Exception as e:
        print(f"Error baca {kode}: {e}")
        return None

# ========== MAIN PROGRAM ==========
waktu = datetime.now().strftime('%d-%m-%Y %H:%M')
print(f"🚀 BSJP SCAN SORE UPGRADE - {waktu}")

semua_hasil = []
for kode in LIST_SAHAM:
    res = analisis_bsjp(kode)
    if res:
        semua_hasil.append(res)

# Pisahkan sinyal
sinyal_hidup = [h for h in semua_hasil if h['is_bsjp']]
sinyal_mati = [h for h in semua_hasil if not h['is_bsjp']]

# === SUSUN PESAN TELEGRAM (FORMAT HTML) ===
pesan = f"<b>📊 BSJP SCAN SORE (UPGRADE)</b> - {waktu}\n"
pesan += f"📌 Total: {len(semua_hasil)} saham | 🔥 Sinyal: {len(sinyal_hidup)}\n"
pesan += "=" * 30 + "\n\n"

if sinyal_hidup:
    pesan += "<b>🔥 DAFTAR BSJP (ENTRY SORE)</b>\n\n"
    for h in sinyal_hidup:
        pesan += f"🏢 <b>{h['kode']}</b> - {h['nama']}\n"
        pesan += f"💰 Rp{h['harga']:.0f} | 📈 {h['perubahan']:+.2f}%\n"
        
        # 🔥 DATA FRESH
        pesan += f"📅 {h['data_status']}\n"
        if h['data_warning']:
            pesan += f"⚠️ {h['data_warning']}\n"
        
        pesan += f"📊 RSI: {h['rsi']} | MA20: Rp{h['ma20']:.0f}\n"
        pesan += f"📦 Vol: {h['volume']:,} (Rata2 5H: {h['avg_vol_5']:,})\n"
        pesan += f"💡 <b>Rekomendasi:</b> {h['rekom']}\n"
        pesan += f"🔴 <b>SL:</b> Rp{h['sl']} | 🟢 <b>TP1:</b> Rp{h['tp1']} | 🟢 <b>TP2:</b> Rp{h['tp2']}\n"
        pesan += f"📋 PE: {h['pe']} | PB: {h['pb']} | Kap: {h['market_cap']}\n"
        
        # 🔥 BERITA & INFORMASI TAMBAHAN
        pesan += h['sentimen'] + "\n"
        pesan += h['pengumuman'] + "\n"
        pesan += h['foreign'] + "\n"
        pesan += "-" * 25 + "\n"
else:
    pesan += "⏳ <b>Belum ada saham BSJP hari ini.</b>\n"
    pesan += "Tidak ada sinyal entry sore.\n\n"

# Tambahkan 3 saham dengan RSI tertinggi untuk pantauan
pesan += "<b>📈 Pantauan (RSI Tertinggi):</b>\n"
urut_rsi = sorted(sinyal_mati, key=lambda x: x['rsi'], reverse=True)[:3]
for h in urut_rsi:
    pesan += f"🔹 {h['kode']} (RSI: {h['rsi']}) - Rp{h['harga']:.0f}\n"

# Kirim ke Telegram
kirim_pesan(pesan)
print("✅ Selesai! Cek Telegram.")
