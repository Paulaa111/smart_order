import streamlit as st
import random
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- FUNKCJA POŁĄCZENIA ---
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict, 
        ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(creds)

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sweet Order · Cukiernia", page_icon="🎂", layout="wide", initial_sidebar_state="collapsed")

# ─── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #FDF8F3 !important; font-family: 'DM Sans', sans-serif; color: #2C1A0E; }
.hero { text-align: center; padding: 4rem 2rem 3rem; }
.hero h1 { font-family: 'Cormorant Garamond', serif; font-size: 3.5rem; color: #2C1A0E; }
.section-card { background: rgba(255,255,255,0.65); border-radius: 20px; padding: 1.8rem; margin-bottom: 1.5rem; }
.price-box { background: #2C1A0E; border-radius: 20px; padding: 2rem; color: white; text-align: center; }
.summary-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #eee; }
.summary-key { color: #7A5C45; text-transform: uppercase; font-size: 0.7rem; }
.summary-val { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ────────────────────────────────────────────────────────────────
def fmt_price(val: float) -> str: return f"{val:.2f} zł"

def calc_price(tier, porcje, floors, fillings, decoration, extras, is_gluten, is_vegan):
    base = {"Klasyczny": 120, "Premium": 200, "Artystyczny": 320, "Weselny": 500}[tier]
    base += (porcje - 10) * 4 + (floors - 1) * 80 + len(fillings) * 12 + len(extras) * 15
    deco_prices = {"Prosty": 0, "Kwiatowy": 40, "Malowany": 80, "Figurki": 120, "Naked Cake": 30}
    base += deco_prices.get(decoration, 0)
    if is_gluten: base += 25
    if is_vegan: base += 30
    return float(base)

# ─── SESSION STATE ──────────────────────────────────────────────────────────
if "submitted" not in st.session_state: st.session_state.submitted = False
if "order_id" not in st.session_state: st.session_state.order_id = f"SO-{random.randint(10000, 99999)}"

# ─── FORM ──────────────────────────────────────────────────────────────────
if not st.session_state.submitted:
    imie = st.text_input("Imię i nazwisko")
    telefon = st.text_input("Telefon")
    email = st.text_input("E-mail")
    odbiór = st.date_input("Data odbioru", min_value=datetime.today() + timedelta(days=3))
    tier = st.selectbox("Seria tortu", ["Klasyczny", "Premium", "Artystyczny", "Weselny"])
    porcje = st.slider("Liczba porcji", 8, 120, 16)
    floors = st.radio("Liczba pięter", [1, 2, 3], horizontal=True)
    sponge = st.selectbox("Biszkopt", ["Waniliowy", "Czekoladowy", "Red Velvet"])
    fillings = st.multiselect("Nadzienie", ["Truskawkowe", "Malinowe", "Pistacjowe"], default=["Truskawkowe"])
    decoration = st.selectbox("Styl dekoracji", ["Prosty", "Kwiatowy", "Malowany", "Figurki", "Naked Cake"])
    kolor = st.selectbox("Kolor", ["Pastelowa", "Klasyczna", "Ciemna"])
    extras = st.multiselect("Dodatki", ["Złote detale", "Jadalne kwiaty", "Napis dedykacyjny"])
    napis = st.text_input("Treść napisu") if "Napis dedykacyjny" in extras else ""
    is_gluten = st.checkbox("Bez glutenu")
    is_vegan = st.checkbox("Wegańskie")
    inspiracje = st.text_area("Uwagi")
    price = calc_price(tier, porcje, floors, fillings, decoration, extras, is_gluten, is_vegan)

    if st.button("✦ Złóż zamówienie"):
        try:
            dane = [st.session_state.order_id, imie, telefon, email, str(odbiór), tier, porcje, floors, sponge, ", ".join(fillings), decoration, kolor, ", ".join(extras), napis, is_gluten, is_vegan, price]
            client = get_gspread_client()
            client.open("Baza_Zamowien").worksheet("Arkusz1").append_row(dane)
            
            st.session_state.order_data = {
                "id": st.session_state.order_id, "imie": imie, "telefon": telefon, "email": email, 
                "odbiór": str(odbiór), "tier": tier, "porcje": porcje, "floors": floors, 
                "sponge": sponge, "fillings": fillings, "decoration": decoration, "kolor": kolor, 
                "extras": extras, "napis": napis, "gluten_free": is_gluten, "vegan": is_vegan, 
                "price": price, "inspiracje": inspiracje
            }
            st.session_state.submitted = True
            st.rerun()
        except Exception as e:
            st.error(f"Błąd zapisu: {e}")

# ─── SUCCESS ────────────────────────────────────────────────────────────────
else:
    d = st.session_state.order_data
    st.success("Zamówienie złożone!")
    st.markdown(f"### Numer zamówienia: {d['id']}")
    
    rows = [
        ("Klient", d.get("imie")), ("Telefon", d.get("telefon")), ("Data", d.get("odbiór")),
        ("Seria", d.get("tier")), ("Porcje", d.get("porcje")), ("Dekoracja", d.get("decoration")),
        ("Napis", d.get("napis", "-")), ("Cena", fmt_price(d.get("price", 0)))
    ]
    for k, v in rows:
        st.markdown(f'<div class="summary-row"><span class="summary-key">{k}</span><span class="summary-val">{v}</span></div>', unsafe_allow_html=True)
    
    if st.button("↩ Złóż nowe"):
        st.session_state.clear()
        st.rerun()
