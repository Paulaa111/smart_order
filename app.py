import streamlit as st
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# --- WYSYŁKA MAILA ---
def send_email(order_data):
    if "EMAIL_PASSWORD" not in st.secrets:
        st.error("Brak klucza EMAIL_PASSWORD w Secrets!")
        return False

    sender_email = "letitcolor66@gmail.com"
    owner_email = "letitcolor66@gmail.com"  # ← zmień na maila właściciela cukierni
    password = st.secrets["EMAIL_PASSWORD"]
    receiver_email = order_data["email"]

    def build_message(to_addr, subject, body_text, body_html):
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        msg.attach(MIMEText(body_html, "html", "utf-8"))
        return msg

    # ── MAIL DO KLIENTA ───────────────────────────────────────────────────────
    client_text = f"""
Cześć {order_data['imie']}!

Dziękujemy za złożenie zamówienia w naszej cukierni 🎂

Numer zamówienia: {order_data['id']}
Data odbioru: {order_data['odbiór']}
Szacunkowa cena: {order_data['price']:.2f} zł

Cukiernik skontaktuje się z Tobą w ciągu 24h.

Pozdrawiamy, Zespół Sweet Order
    """

    client_html = f"""
<html><body style="font-family:Arial,sans-serif;color:#0A1E6E;background:#F5F0E8;padding:20px;">
  <div style="max-width:500px;margin:0 auto;background:white;border-radius:4px;padding:32px;box-shadow:0 4px 20px rgba(20,56,160,0.08);">
    <h2 style="color:#1438A0;">Sweet Order 🎂</h2>
    <p style="color:#4560A0;font-size:0.85rem;">Cukiernia Artystyczna</p>
    <p>Cześć <strong>{order_data['imie']}</strong>!</p>
    <p>Dziękujemy za złożenie zamówienia. Oto szczegóły:</p>
    <div style="background:#F5F0E8;border-radius:4px;padding:16px;margin:20px 0;">
      <p><strong>Nr zamówienia:</strong> {order_data['id']}</p>
      <p><strong>Data odbioru:</strong> {order_data['odbiór']}</p>
      <p><strong>Seria tortu:</strong> {order_data['tier']}</p>
      <p><strong>Porcje:</strong> {order_data['porcje']} szt. · {order_data['floors']} piętro/a</p>
      <p><strong>Biszkopt:</strong> {order_data['sponge']}</p>
      <p><strong>Nadzienie:</strong> {", ".join(order_data['fillings'])}</p>
      <p><strong>Dekoracja:</strong> {order_data['decoration']}</p>
      <p><strong>Dodatki:</strong> {", ".join(order_data['extras']) if order_data['extras'] else '—'}</p>
      <p><strong>Bez glutenu:</strong> {'Tak' if order_data['gluten_free'] else 'Nie'} · <strong>Wegańskie:</strong> {'Tak' if order_data['vegan'] else 'Nie'}</p>
      {'<p><strong>Uwagi:</strong> ' + order_data['inspiracje'] + '</p>' if order_data.get('inspiracje') else ''}
      <p><strong>Szacunkowa cena:</strong> <span style="color:#1438A0;font-weight:bold;">{order_data['price']:.2f} zł</span></p>
    </div>
    <p style="background:#EDE5D8;border-left:2px solid #1438A0;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.88rem;">
      💳 Skontaktujemy się z Tobą w ciągu <strong>24h</strong> w celu potwierdzenia i ustalenia zaliczki (40%).
    </p>
    <p style="margin-top:24px;color:#4560A0;font-size:0.85rem;">Pozdrawiamy,<br><strong>Zespół Sweet Order</strong></p>
  </div>
</body></html>
    """

    # ── MAIL DO WŁAŚCICIELA ───────────────────────────────────────────────────
    napis_info = f"<p><strong>Napis na torcie:</strong> {order_data['napis']}</p>" if order_data.get('napis') else ""
    inspiracje_info = f"<p><strong>Uwagi / inspiracje:</strong> {order_data['inspiracje']}</p>" if order_data.get('inspiracje') else ""

    owner_html = f"""
<html><body style="font-family:Arial,sans-serif;color:#0A1E6E;padding:20px;">
  <div style="max-width:560px;margin:0 auto;background:white;border-radius:4px;padding:32px;box-shadow:0 4px 20px rgba(20,56,160,0.08);">
    <div style="background:#0E2D8A;border-radius:4px;padding:16px 24px;margin-bottom:24px;">
      <h2 style="color:#DEC08A;margin:0;font-size:1.4rem;">🎂 Nowe zamówienie!</h2>
      <p style="color:rgba(245,240,232,0.6);margin:4px 0 0;font-size:0.85rem;">Sweet Order · Panel właściciela</p>
    </div>
    <h3 style="color:#1438A0;border-bottom:1px solid #EDE5D8;padding-bottom:8px;">📋 Dane klienta</h3>
    <p><strong>Imię i nazwisko:</strong> {order_data['imie']}</p>
    <p><strong>Telefon:</strong> {order_data['telefon']}</p>
    <p><strong>E-mail:</strong> {order_data['email']}</p>
    <p><strong>Data odbioru:</strong> {order_data['odbiór']}</p>
    <h3 style="color:#1438A0;border-bottom:1px solid #EDE5D8;padding-bottom:8px;margin-top:24px;">🎂 Szczegóły tortu</h3>
    <p><strong>Nr zamówienia:</strong> <span style="background:#F5F0E8;padding:2px 8px;border-radius:3px;font-weight:bold;">{order_data['id']}</span></p>
    <p><strong>Seria:</strong> {order_data['tier']}</p>
    <p><strong>Porcje:</strong> {order_data['porcje']} szt.</p>
    <p><strong>Piętra:</strong> {order_data['floors']}</p>
    <p><strong>Biszkopt:</strong> {order_data['sponge']}</p>
    <p><strong>Nadzienie:</strong> {", ".join(order_data['fillings'])}</p>
    <p><strong>Dekoracja:</strong> {order_data['decoration']}</p>
    <p><strong>Paleta kolorów:</strong> {order_data['kolor']}</p>
    <p><strong>Dodatki:</strong> {", ".join(order_data['extras']) if order_data['extras'] else '—'}</p>
    {napis_info}
    <p><strong>Bez glutenu:</strong> {'✅ Tak' if order_data['gluten_free'] else 'Nie'}</p>
    <p><strong>Wegańskie:</strong> {'✅ Tak' if order_data['vegan'] else 'Nie'}</p>
    {inspiracje_info}
    <div style="background:#0E2D8A;border-radius:4px;padding:16px 24px;margin-top:24px;text-align:center;">
      <p style="color:rgba(245,240,232,0.5);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.2em;margin:0 0 4px;">Szacunkowa cena</p>
      <p style="color:#DEC08A;font-size:2rem;margin:0;font-weight:300;">{order_data['price']:.2f} zł</p>
    </div>
  </div>
</body></html>
    """

    owner_text = f"Nowe zamówienie {order_data['id']} od {order_data['imie']}, tel: {order_data['telefon']}, odbiór: {order_data['odbiór']}, cena: {order_data['price']:.2f} zł"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            msg_client = build_message(receiver_email, f"✦ Potwierdzenie zamówienia {order_data['id']} – Sweet Order", client_text, client_html)
            server.sendmail(sender_email, receiver_email, msg_client.as_string())
            msg_owner = build_message(owner_email, f"🎂 Nowe zamówienie {order_data['id']} – {order_data['imie']}", owner_text, owner_html)
            server.sendmail(sender_email, owner_email, msg_owner.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("❌ Błąd logowania do Gmail. Sprawdź hasło aplikacji w Secrets.")
        return False
    except Exception as e:
        st.error(f"❌ Błąd wysyłki: {e}")
        return False


# --- POŁĄCZENIE Z ARKUSZEM ---
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict,
        ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(creds)


# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sweet Order · Cukiernia",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,500&family=Jost:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy: #1438A0;
  --navy-deep: #0E2D8A;
  --navy-mid: #1A46B8;
  --cream: #F5F0E8;
  --cream-warm: #EDE5D8;
  --cream-dark: #D6CABC;
  --accent: #C9A96E;
  --accent-light: #DEC08A;
  --text: #0A1E6E;
  --text-muted: #4560A0;
  --border: rgba(20,56,160,0.12);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--cream) !important;
    font-family: 'Jost', sans-serif;
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 1000px !important;
    padding: 0 2rem 4rem !important;
    margin: 0 auto !important;
}

/* LOGO */
.logo-bar {
  display: flex;
  justify-content: center;
  padding: 2.5rem 2rem 0;
}
.logo {
  display: flex;
  align-items: center;
  gap: 0;
}
.logo-mark {
  width: 52px; height: 52px;
  background: var(--navy-deep);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.logo-mark::before {
  content: '';
  position: absolute;
  bottom: -6px; left: 50%;
  transform: translateX(-50%);
  width: 36px; height: 36px;
  border-radius: 50%;
  background: rgba(201,169,110,0.15);
}
.logo-mark svg { position: relative; z-index: 1; }
.logo-text {
  padding-left: 0.9rem;
  border-left: 1.5px solid rgba(20,56,160,0.15);
  margin-left: 0.9rem;
}
.logo-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.45rem;
  font-weight: 600;
  color: var(--navy-deep);
  line-height: 1;
  letter-spacing: 0.02em;
}
.logo-tagline {
  font-family: 'Jost', sans-serif;
  font-size: 0.58rem;
  font-weight: 500;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--accent);
  margin-top: 0.25rem;
}

/* HERO */
.hero {
    text-align: center;
    padding: 3rem 2rem 3rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 1px; height: 40px;
    background: linear-gradient(to bottom, transparent, var(--navy));
}
.hero-tag {
    display: inline-block;
    font-family: 'Jost', sans-serif;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--navy);
    background: rgba(20,56,160,0.06);
    padding: 0.5rem 1.6rem;
    border-radius: 1px;
    margin-bottom: 2rem;
    border: 1px solid rgba(20,56,160,0.18);
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(3.5rem, 8vw, 6.5rem);
    font-weight: 300;
    color: var(--navy-deep);
    line-height: 1.0;
    letter-spacing: -0.02em;
}
.hero h1 em {
    font-style: italic;
    font-weight: 500;
    color: var(--accent);
}
.hero-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 400;
    margin-top: 1.4rem;
}
.ornament-divider {
    text-align: center;
    color: var(--accent);
    opacity: 0.5;
    font-size: 0.8rem;
    letter-spacing: 0.8em;
    margin: 0.5rem 0 3rem;
}

/* SECTION CARDS */
.section-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1.8rem 2.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 16px rgba(20,56,160,0.04);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.section-card:hover {
    box-shadow: 0 8px 40px rgba(20,56,160,0.1);
    border-color: rgba(20,56,160,0.2);
}
.section-title {
    font-family: 'Jost', sans-serif;
    font-size: 0.63rem;
    font-weight: 600;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 0;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    letter-spacing: 0.22em;
    text-transform: uppercase;
}
.section-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px; height: 24px;
    background: var(--navy);
    color: var(--cream);
    border-radius: 2px;
    font-family: 'Jost', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    flex-shrink: 0;
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--cream) !important;
    border: 1.5px solid var(--cream-dark) !important;
    border-radius: 3px !important;
    color: var(--navy-deep) !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.92rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(20,56,160,0.08) !important;
    outline: none !important;
}
.stSelectbox > div > div {
    background: var(--cream) !important;
    border: 1.5px solid var(--cream-dark) !important;
    border-radius: 3px !important;
}
.stMultiSelect > div > div {
    background: var(--cream) !important;
    border: 1.5px solid var(--cream-dark) !important;
    border-radius: 3px !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(20,56,160,0.08) !important;
    border: 1px solid rgba(20,56,160,0.2) !important;
    border-radius: 2px !important;
    color: var(--navy) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
}
.stSlider > div > div > div > div { background: #6B2737 !important; }
.stSlider [data-testid="stThumbValue"] { color: #6B2737 !important; }
.stSlider [aria-valuenow] { accent-color: #6B2737 !important; }
.stSlider > div > div > div { background: var(--cream-dark) !important; }

/* LABELS */
label, [data-testid="stWidgetLabel"] p {
    font-family: 'Jost', sans-serif !important;
    font-size: 0.63rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* PRICE BOX */
.price-box {
    background: var(--navy-deep);
    border-radius: 3px;
    padding: 2.5rem 2.5rem;
    color: var(--cream);
    text-align: center;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(14,45,138,0.25);
}
.price-box::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(201,169,110,0.08);
    pointer-events: none;
}
.price-box::after {
    content: '';
    position: absolute;
    bottom: -80px; left: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(201,169,110,0.05);
    pointer-events: none;
}
.price-label {
    font-size: 0.6rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    font-weight: 600;
    color: rgba(245,240,232,0.4);
    margin-bottom: 0.5rem;
}
.price-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 5rem;
    font-weight: 300;
    line-height: 1;
    color: var(--accent-light);
    position: relative;
    z-index: 1;
}
.price-sub {
    font-size: 0.72rem;
    color: rgba(245,240,232,0.35);
    margin-top: 0.6rem;
    font-weight: 400;
    letter-spacing: 0.1em;
}

/* NADPISANIE CZERWONYCH OBRAMÓWEK STREAMLIT */
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within,
[data-baseweb="select"]:focus-within {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(20,56,160,0.08) !important;
}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color: var(--navy) !important;
    background-color: #fff !important;
}
*:focus-visible {
    outline: 2px solid var(--navy) !important;
    outline-offset: 1px !important;
    box-shadow: none !important;
}
.stTextInput [data-baseweb="input"]:focus-within,
.stTextArea [data-baseweb="textarea"]:focus-within {
    border-color: var(--navy) !important;
}

/* BUTTON */
.stButton > button {
    background: var(--navy) !important;
    color: var(--cream) !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 1rem 2.5rem !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.28em !important;
    text-transform: uppercase !important;
    transition: all 0.25s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: var(--navy-mid) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 36px rgba(20,56,160,0.3) !important;
}

/* SUCCESS */
.success-box {
    background: var(--navy-deep);
    border: 1px solid rgba(201,169,110,0.3);
    border-radius: 3px;
    padding: 2.5rem;
    text-align: center;
    color: var(--cream);
    box-shadow: 0 12px 40px rgba(14,45,138,0.2);
}
.success-box h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.5rem;
    font-weight: 300;
    color: var(--accent-light);
}

/* SUMMARY */
.summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
}
.summary-row:last-child { border-bottom: none; }
.summary-key {
    color: var(--text-muted);
    font-size: 0.63rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 600;
}
.summary-val { color: var(--navy-deep); font-weight: 500; text-align: right; max-width: 60%; }

/* INFO BOX */
.info-box {
    background: rgba(20,56,160,0.04);
    border-left: 2px solid var(--navy);
    border-radius: 0 3px 3px 0;
    padding: 0.8rem 1.1rem;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin: 0.5rem 0;
    line-height: 1.55;
}

[data-testid="column"] { padding: 0 0.5rem !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: rgba(20,56,160,0.2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def fmt_price(val: float) -> str:
    return f"{val:.2f} zł"


def calc_price(tier, porcje, floors, fillings, decoration, extras, is_gluten, is_vegan):
    base = {"Klasyczny": 120, "Premium": 200, "Artystyczny": 320, "Weselny": 500}[tier]
    base += (porcje - 10) * 4
    base += (floors - 1) * 80
    base += len(fillings) * 12
    deco_prices = {"Prosty": 0, "Kwiatowy": 40, "Malowany": 80, "Figurki": 120, "Naked Cake": 30}
    base += deco_prices.get(decoration, 0)
    base += len(extras) * 15
    if is_gluten: base += 25
    if is_vegan: base += 30
    return float(base)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "order_id" not in st.session_state:
    st.session_state.order_id = f"SO-{random.randint(10000, 99999)}"


# ─── LOGO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="logo-bar">
  <div class="logo">
    <div class="logo-mark">
      <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="13" cy="17" rx="9" ry="4" fill="#DEC08A" opacity="0.9"/>
        <rect x="4" y="13" width="18" height="4" rx="1" fill="#DEC08A" opacity="0.7"/>
        <ellipse cx="13" cy="13" rx="9" ry="3" fill="#F5F0E8" opacity="0.9"/>
        <rect x="9" y="7" width="2" height="5" rx="1" fill="#F5F0E8" opacity="0.8"/>
        <rect x="15" y="8" width="2" height="4" rx="1" fill="#F5F0E8" opacity="0.8"/>
        <ellipse cx="10" cy="6.5" rx="1" ry="1.5" fill="#C9A96E"/>
        <ellipse cx="16" cy="7.5" rx="1" ry="1.5" fill="#C9A96E"/>
      </svg>
    </div>
    <div class="logo-text">
      <div class="logo-name">Sweet Order</div>
      <div class="logo-tagline">Cukiernia Artystyczna</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ Zamówienie Online ✦</div>
    <h1>Twój wymarzony<br><em>tort</em></h1>
    <p class="hero-sub">Konfigurator zamówień · Cukiernia Artystyczna</p>
</div>
<div class="ornament-divider">· · · ✦ · · ·</div>
""", unsafe_allow_html=True)


# ─── FORM ─────────────────────────────────────────────────────────────────────
if not st.session_state.submitted:

    # ── 1. DANE KONTAKTOWE ────────────────────────────────────────────────────
    st.markdown("""<div class="section-card">
        <div class="section-title"><span class="section-num">1</span> Dane kontaktowe</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        imie = st.text_input("Imię i nazwisko", placeholder="np. Anna Kowalska")
        telefon = st.text_input("Telefon", placeholder="+48 000 000 000")
    with col2:
        email = st.text_input("E-mail", placeholder="anna@example.com")
        odbiór = st.date_input(
            "Data odbioru",
            min_value=datetime.today() + timedelta(days=3),
            value=datetime.today() + timedelta(days=7),
        )

    st.markdown('<div class="info-box">⏱ Zamówienia przyjmujemy z minimum 3-dniowym wyprzedzeniem. Torty weselne — prosimy o kontakt co najmniej 2 tygodnie wcześniej.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. RODZAJ & ROZMIAR ───────────────────────────────────────────────────
    st.markdown("""<div class="section-card">
        <div class="section-title"><span class="section-num">2</span> Rodzaj & rozmiar tortu</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        tier = st.selectbox(
            "Seria tortu",
            ["Klasyczny", "Premium", "Artystyczny", "Weselny"],
        )
        tier_desc = {
            "Klasyczny": "🎂 Elegancki, prosty tort — idealny na urodziny lub mały jubileusz. Od 120 zł.",
            "Premium": "✨ Wyrafinowane wykończenie, piękne detale, wyraziste smaki. Od 200 zł.",
            "Artystyczny": "🎨 Tort jak dzieło sztuki — ręcznie malowany lub zdobiony figurkami. Od 320 zł.",
            "Weselny": "💍 Wielopiętrowe arcydzieło na Twój wyjątkowy dzień. Od 500 zł.",
        }
        st.markdown(f'<div class="info-box">{tier_desc[tier]}</div>', unsafe_allow_html=True)
    with col2:
        porcje = st.slider("Liczba porcji", min_value=8, max_value=120, value=16, step=2)
        floors = st.radio("Liczba pięter", [1, 2, 3], horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. SMAK ───────────────────────────────────────────────────────────────
    st.markdown("""<div class="section-card">
        <div class="section-title"><span class="section-num">3</span> Biszkopt & nadzienie</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sponge = st.selectbox(
            "Biszkopt",
            ["Klasyczny waniliowy", "Czekoladowy", "Red Velvet", "Cytrynowy", "Matcha", "Kakaowy z espresso"],
        )
    with col2:
        fillings = st.multiselect(
            "Nadzienie (możliwy wybór wielu, +12 zł / szt.)",
            ["Truskawkowe", "Malinowe", "Lemon curd", "Czekoladowe", "Karmelowe",
             "Pistacjowe", "Tiramisu", "Kokosowe", "Wiśniowe", "Mango-passionfruit"],
            default=["Truskawkowe"],
        )

    col1, col2 = st.columns(2)
    with col1:
        is_gluten = st.checkbox("🌾 Bez glutenu (+25 zł)")
    with col2:
        is_vegan = st.checkbox("🌱 Wersja wegańska (+30 zł)")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4. DEKORACJA ──────────────────────────────────────────────────────────
    st.markdown("""<div class="section-card">
        <div class="section-title"><span class="section-num">4</span> Dekoracja & wykończenie</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        decoration_raw = st.selectbox(
            "Styl dekoracji",
            ["Prosty", "Kwiatowy (+40 zł)", "Malowany (+80 zł)", "Figurki (+120 zł)", "Naked Cake (+30 zł)"],
        )
        decoration = decoration_raw.split(" (")[0]
    with col2:
        kolor = st.selectbox(
            "Paleta kolorów",
            ["Pastelowa (różowy, miętowy, kremowy)", "Klasyczna (biel i złoto)",
             "Ciemna (granat, bordo, czerń)", "Kolorowa (tęczowa)", "Niestandardowa (opis poniżej)"],
        )

    extras = st.multiselect(
        "Dodatki (+15 zł / szt.)",
        ["Złote detale", "Jadalne kwiaty", "Perły cukrowe", "Błyszczące opłatki",
         "Napis dedykacyjny", "Świeczki urodzinowe", "Topper weselny", "Figurki cukrowe", "Owoce świeże"],
    )

    napis = ""
    if "Napis dedykacyjny" in extras:
        napis = st.text_input("Treść napisu na torcie", placeholder='np. „Wszystkiego najlepszego, Mario!"')

    inspiracje = st.text_area(
        "Dodatkowe wskazówki / inspiracje",
        placeholder="Opisz swoje wyobrażenie tortu, temat przewodni, ulubione kolory, lub wklej link do inspiracji...",
        height=90,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CENA ──────────────────────────────────────────────────────────────────
    price = calc_price(tier, porcje, floors, fillings, decoration, extras, is_gluten, is_vegan)
    fl_label = "piętro" if floors == 1 else ("piętra" if floors < 5 else "pięter")

    st.markdown(f"""
    <div class="price-box">
        <div class="price-label">Szacunkowa cena zamówienia</div>
        <div class="price-value">{fmt_price(price)}</div>
        <div class="price-sub">{porcje} porcji · {floors} {fl_label} · cena orientacyjna</div>
    </div>
    <div class="info-box">💳 Ostateczna wycena po potwierdzeniu przez cukiernika. Zaliczka 40% przy złożeniu zamówienia.</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SUBMIT ────────────────────────────────────────────────────────────────
    if st.button("✦ Złóż zamówienie"):
        errors = []
        if not imie.strip(): errors.append("Podaj imię i nazwisko.")
        if not telefon.strip(): errors.append("Podaj numer telefonu.")
        if not email.strip() or "@" not in email: errors.append("Podaj poprawny adres e-mail.")
        if not fillings: errors.append("Wybierz co najmniej jedno nadzienie.")

        if errors:
            for e in errors: st.error(f"⚠️ {e}")
        else:
            dane_do_zapisu = [
                st.session_state.order_id, imie, telefon, email, str(odbiór),
                tier, porcje, floors, sponge, ", ".join(fillings),
                decoration, kolor.split(" (")[0], ", ".join(extras),
                napis, is_gluten, is_vegan, price, inspiracje
            ]

            order_data = {
                "id": st.session_state.order_id,
                "imie": imie, "telefon": telefon, "email": email,
                "odbiór": str(odbiór), "tier": tier, "porcje": porcje,
                "floors": floors, "sponge": sponge, "fillings": fillings,
                "decoration": decoration, "kolor": kolor.split(" (")[0],
                "extras": extras, "napis": napis, "gluten_free": is_gluten,
                "vegan": is_vegan, "price": price, "inspiracje": inspiracje
            }

            try:
                client = get_gspread_client()
                sheet = client.open("Baza_Zamowien").worksheet("Arkusz1")
                wszystkie_dane = sheet.get_all_values()
                nastepny_wiersz = len(wszystkie_dane) + 1
                sheet.insert_row(dane_do_zapisu, nastepny_wiersz, value_input_option='USER_ENTERED')

                send_email(order_data)

                st.session_state.order_data = order_data
                st.session_state.submitted = True
                st.rerun()

            except Exception as e:
                st.error(f"❌ Błąd podczas zapisu lub wysyłki: {e}")

# ─── SUCCESS ──────────────────────────────────────────────────────────────────
else:
    d = st.session_state.order_data

    st.markdown(f"""
    <div class="success-box">
        <div style="font-size:3rem;margin-bottom:0.6rem">🎂</div>
        <h2>Zamówienie złożone!</h2>
        <div style="background:rgba(255,255,255,0.07);border-radius:3px;padding:0.7rem 1.5rem;display:inline-block;margin-top:1.2rem;">
            <div style="font-size:0.6rem;letter-spacing:0.28em;opacity:0.5;text-transform:uppercase;">Numer zamówienia</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:300;color:#DEC08A;">{d.get("id")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="section-card"><div class="section-title"><span class="section-num">✓</span> Podsumowanie</div>""", unsafe_allow_html=True)

    rows = [
        ("Klient", d.get("imie")), ("Telefon", d.get("telefon")), ("E-mail", d.get("email")),
        ("Data odbioru", d.get("odbiór")), ("Seria tortu", d.get("tier")),
        ("Porcje", f'{d.get("porcje")} szt.'), ("Piętra", str(d.get("floors"))),
        ("Biszkopt", d.get("sponge")), ("Nadzienie", ", ".join(d.get("fillings", []))),
        ("Dekoracja", d.get("decoration")), ("Paleta kolorów", d.get("kolor")),
        ("Dodatki", ", ".join(d.get("extras", [])) if d.get("extras") else "—"),
        ("Napis", d.get("napis") if d.get("napis") else "—"),
        ("Bez glutenu", "Tak" if d.get("gluten_free") else "Nie"),
        ("Wegańskie", "Tak" if d.get("vegan") else "Nie"),
    ]

    for k, v in rows:
        st.markdown(f'<div class="summary-row"><span class="summary-key">{k}</span><span class="summary-val">{v}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="price-box">
        <div class="price-label">Szacunkowa cena</div>
        <div class="price-value">{fmt_price(d.get("price", 0.0))}</div>
    </div>
    """, unsafe_allow_html=True)

    if d.get("inspiracje"):
        st.markdown(f'<div class="info-box">💬 <strong>Uwagi:</strong> {d.get("inspiracje")}</div>', unsafe_allow_html=True)

    if st.button("↩ Złóż nowe zamówienie"):
        for key in ["submitted", "order_id", "order_data"]: st.session_state.pop(key, None)
        st.rerun()
