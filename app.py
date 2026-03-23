import streamlit as st
from datetime import datetime, timedelta, date
import random
import json
from pathlib import Path
from integrations import save_to_sheets, send_confirmation_emails

# ─── BLOCKED DATES STORAGE ───────────────────────────────────────────────────
BLOCKED_DATES_FILE = Path(__file__).parent / "blocked_dates.json"

def load_blocked_dates() -> list:
    if BLOCKED_DATES_FILE.exists():
        with open(BLOCKED_DATES_FILE) as f:
            return json.load(f)
    return []

def save_blocked_dates(dates: list):
    with open(BLOCKED_DATES_FILE, "w") as f:
        json.dump(dates, f)

def is_date_blocked(d) -> bool:
    blocked = load_blocked_dates()
    return str(d) in blocked

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sweet Order | Cukiernia",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');

:root {
    --bg-light: #F9F6F2;
    --burgundy: #630D16;
    --text-dark: #2D2424;
    --beige-dark: #E6DED5;
}

/* 1. CAŁOŚĆ I TŁO */
.stApp {
    background: var(--bg-light) !important;
    font-family: 'Inter', sans-serif !important;
}

/* 2. KONIEC Z CZERWONĄ RAMKĄ (HARD RESET) */
/* To celuje we wszystkie stany inputa: spoczynek, najechanie i kliknięcie */
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"], .stSelectbox {
    border: 1px solid var(--beige-dark) !important;
    border-radius: 4px !important;
    transition: all 0.3s ease !important;
}

/* Stan po kliknięciu (Focus) - wymuszamy Burgund zamiast czerwonego/niebieskiego */
div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
    border-color: var(--burgundy) !important;
    box-shadow: 0 0 0 2px rgba(99, 13, 22, 0.2) !important;
}

/* Usuwamy domyślne czerwone obramowanie Streamlita przy błędach walidacji */
.st-ae { border-color: var(--beige-dark) !important; }

/* 3. NOWOCZESNE KARTY (Luxury Look) */
.section-card {
    background: white !important;
    border-left: 6px solid var(--burgundy) !important;
    padding: 25px !important;
    margin-bottom: 20px !important;
    border-radius: 0 8px 8px 0 !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
}

.section-title {
    font-family: 'Playfair Display', serif !important;
    color: var(--burgundy) !important;
    font-size: 1.6rem !important;
    margin-bottom: 15px !important;
    font-weight: 700 !important;
}

/* 4. PRZYCISKI */
.stButton > button {
    background-color: var(--burgundy) !important;
    color: white !important;
    border: none !important;
    padding: 15px 30px !important;
    border-radius: 0px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #4a0a10 !important;
    color: white !important;
}

/* 5. BOX CENY */
.price-box {
    background: var(--burgundy) !important;
    color: white !important;
    padding: 40px !important;
    text-align: center !important;
    margin: 30px 0 !important;
}

.price-value {
    font-family: 'Playfair Display', serif !important;
    font-size: 4rem !important;
    margin: 10px 0 !important;
}
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
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────
ADMIN_PASSWORD = st.secrets.get("admin", {}).get("password", "cukiernia2024")

with st.sidebar:
    st.markdown("### 🔐 Panel Cukiernika")
    if not st.session_state.admin_logged_in:
        pwd = st.text_input("Hasło", type="password", placeholder="Wpisz hasło...")
        if st.button("Zaloguj", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Błędne hasło")
    else:
        st.success("✅ Zalogowano")
        st.markdown("---")
        st.markdown("#### 📅 Zarządzaj datami")
        blocked = load_blocked_dates()
        new_blocked = st.date_input("Zablokuj datę", min_value=date.today())
        if st.button("➕ Zablokuj"):
            d_str = str(new_blocked)
            if d_str not in blocked:
                blocked.append(d_str)
                save_blocked_dates(blocked)
                st.rerun()
        
        for d_str in sorted(blocked):
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"🚫 {d_str}")
            with c2: 
                if st.button("🗑", key=f"del_{d_str}"):
                    blocked.remove(d_str)
                    save_blocked_dates(blocked)
                    st.rerun()
        if st.button("🚪 Wyloguj"):
            st.session_state.admin_logged_in = False
            st.rerun()

# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <div style="width: 60px; height: 60px; background: #630D16; color: white; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 1rem; border: 2px solid #E6DED5;">S</div>
    <h1 style="font-family: 'Playfair Display', serif; color: #630D16; font-size: 3rem; margin: 0;">Sweet Order</h1>
    <p style="text-transform: uppercase; letter-spacing: 3px; font-size: 0.7rem; color: #8C7E7E;">Premium Cake Experience</p>
</div>
""", unsafe_allow_html=True)

# ─── FORM ─────────────────────────────────────────────────────────────────────
if not st.session_state.submitted:
    # ── 1. DANE KONTAKTOWE
    st.markdown("""<div class="section-card"><div class="section-title"><span class="section-num">1</span> Dane kontaktowe</div></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        imie = st.text_input("Imię i nazwisko", placeholder="np. Anna Kowalska")
        telefon = st.text_input("Telefon", placeholder="+48 000 000 000")
    with col2:
        email = st.text_input("E-mail", placeholder="anna@example.com")
        blocked_dates = load_blocked_dates()
        default_date = datetime.today().date() + timedelta(days=3)
        while str(default_date) in blocked_dates: default_date += timedelta(days=1)
        odbiór = st.date_input("Data odbioru", min_value=datetime.today().date() + timedelta(days=3), value=default_date)

    date_ok = str(odbiór) not in blocked_dates
    if not date_ok: st.error("❌ Ta data jest niedostępna.")

    st.markdown('<div class="info-box">INFO: Zamówienia przyjmujemy z min. 3-dniowym wyprzedzeniem.</div>', unsafe_allow_html=True)

    # ── 2. RODZAJ & ROZMIAR
    st.markdown("""<div class="section-card"><div class="section-title"><span class="section-num">2</span> Rodzaj i rozmiar</div></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        tier = st.selectbox("Seria tortu", ["Klasyczny", "Premium", "Artystyczny", "Weselny"])
    with col2:
        porcje = st.slider("Liczba porcji", 8, 120, 16, 2)
        floors = st.radio("Liczba pięter", [1, 2, 3], horizontal=True)

    # ── 3. SMAK
    st.markdown("""<div class="section-card"><div class="section-title"><span class="section-num">3</span> Biszkopt i nadzienie</div></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: sponge = st.selectbox("Biszkopt", ["Waniliowy", "Czekoladowy", "Red Velvet"])
    with col2: fillings = st.multiselect("Nadzienie (+12 zł)", ["Truskawka", "Malina", "Pistacja", "Karmel"], default=["Truskawka"])
    
    c1, c2 = st.columns(2)
    is_gluten = c1.checkbox("🌾 Bez glutenu (+25 zł)")
    is_vegan = c2.checkbox("🌱 Wegański (+30 zł)")

    # ── 4. DEKORACJA
    st.markdown("""<div class="section-card"><div class="section-title"><span class="section-num">4</span> Dekoracja</div></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        decoration_raw = st.selectbox("Styl", ["Prosty", "Kwiatowy (+40 zł)", "Malowany (+80 zł)", "Figurki (+120 zł)"])
        decoration = decoration_raw.split(" (")[0]
    with col2:
        kolor = st.selectbox("Kolory", ["Pastelowa", "Biel i Złoto", "Ciemna", "Kolorowa"])

    extras = st.multiselect("Dodatki (+15 zł)", ["Złoto", "Kwiaty", "Perły", "Napis", "Świeczki"])
    napis = st.text_input("Napis") if "Napis" in extras else ""
    inspiracje = st.text_area("Inspiracje", height=90)

    # ── CENA
    price = calc_price(tier, porcje, floors, fillings, decoration, extras, is_gluten, is_vegan)
    
    st.markdown(f"""
    <div class="price-box">
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; opacity: 0.8;">Szacowany koszt</div>
        <div class="price-value">{price:.2f} zł</div>
        <div style="font-size: 0.8rem; margin-top: 10px; opacity: 0.7;">
            {porcje} porcji | {floors} piętra | wycena orientacyjna
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SUBMIT
    if st.button("✦ Złóż zamówienie"):
        if imie and email and telefon and date_ok:
            order = {
                "id": st.session_state.order_id, "imie": imie, "telefon": telefon, "email": email,
                "odbiór": str(odbiór), "tier": tier, "porcje": porcje, "floors": floors,
                "sponge": sponge, "fillings": fillings, "decoration": decoration, "kolor": kolor,
                "extras": extras, "napis": napis, "gluten_free": is_gluten, "vegan": is_vegan,
                "inspiracje": inspiracje, "price": price
            }
            st.session_state.order_data = order
            with st.spinner("Przetwarzanie..."):
                save_to_sheets(order)
                send_confirmation_emails(order)
            st.session_state.submitted = True
            st.rerun()
        else:
            st.error("⚠️ Wypełnij wszystkie dane i sprawdź datę.")

# ─── SUCCESS SCREEN ───────────────────────────────────────────────────────────
else:
    d = st.session_state.order_data
    st.balloons()
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 1rem;">
        <div style="font-size:3rem; margin-bottom:0.6rem;">&#127824;</div>
        <h2 style="font-family: 'Playfair Display', serif; color: #630D16;">Dziękujemy, {d['imie']}!</h2>
        <p style="color: #8C7E7E;">TWOJE ZAMÓWIENIE {d['id']} ZOSTAŁO PRZYJĘTE</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="section-card"><div class="section-title"><span class="section-num">&#10003;</span> Podsumowanie</div>""", unsafe_allow_html=True)
    for k, v in [("Klient", d["imie"]), ("Data", d["odbiór"]), ("Cena", fmt_price(d["price"]))]:
        st.markdown(f'<div class="summary-row"><span class="summary-key">{k}</span><span>{v}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("↩ Nowe zamówienie"):
        st.session_state.submitted = False
        st.rerun()
