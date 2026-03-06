import streamlit as st
from datetime import datetime, timedelta
import random

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sweet Order · Cukiernia",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #FDF8F3 !important;
    font-family: 'DM Sans', sans-serif;
    color: #2C1A0E;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #FDF8F3 0%, #FAF0E6 50%, #FDF8F3 100%) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 1100px !important;
    padding: 0 2rem 4rem !important;
    margin: 0 auto !important;
}

/* HERO */
.hero {
    text-align: center;
    padding: 4rem 2rem 3rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 1px; height: 60px;
    background: linear-gradient(to bottom, transparent, #C8956C);
}
.hero-tag {
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #C8956C;
    background: rgba(200, 149, 108, 0.1);
    padding: 0.4rem 1.2rem;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(200, 149, 108, 0.25);
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 300;
    color: #2C1A0E;
    line-height: 1.1;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}
.hero h1 em {
    font-style: italic;
    color: #C8956C;
}
.hero-sub {
    font-size: 1rem;
    color: #7A5C45;
    font-weight: 300;
    letter-spacing: 0.05em;
    margin-top: 0.8rem;
}
.ornament-divider {
    text-align: center;
    color: #C8956C;
    opacity: 0.5;
    font-size: 1.2rem;
    letter-spacing: 0.5em;
    margin: 0.5rem 0 2.5rem;
}

/* SECTION CARDS */
.section-card {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(200,149,108,0.15);
    border-radius: 20px;
    padding: 1.8rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 32px rgba(44, 26, 14, 0.06);
}
.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    font-weight: 400;
    color: #2C1A0E;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(200,149,108,0.2);
}
.section-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    background: #C8956C;
    color: white;
    border-radius: 50%;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    flex-shrink: 0;
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: rgba(253, 248, 243, 0.9) !important;
    border: 1.5px solid rgba(200, 149, 108, 0.3) !important;
    border-radius: 12px !important;
    color: #2C1A0E !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #C8956C !important;
    box-shadow: 0 0 0 3px rgba(200, 149, 108, 0.15) !important;
}
.stSelectbox > div > div {
    background: rgba(253, 248, 243, 0.9) !important;
    border: 1.5px solid rgba(200, 149, 108, 0.3) !important;
    border-radius: 12px !important;
}
.stMultiSelect > div > div {
    background: rgba(253, 248, 243, 0.9) !important;
    border: 1.5px solid rgba(200, 149, 108, 0.3) !important;
    border-radius: 12px !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(200, 149, 108, 0.15) !important;
    border: 1px solid rgba(200, 149, 108, 0.4) !important;
    border-radius: 8px !important;
    color: #2C1A0E !important;
}
.stSlider > div > div > div > div { background: #C8956C !important; }
.stSlider > div > div > div { background: rgba(200, 149, 108, 0.2) !important; }

/* LABELS */
label, [data-testid="stWidgetLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #7A5C45 !important;
}

/* PRICE BOX */
.price-box {
    background: linear-gradient(135deg, #2C1A0E 0%, #4A2E1C 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    color: white;
    text-align: center;
    margin: 1.5rem 0;
    box-shadow: 0 12px 40px rgba(44, 26, 14, 0.25);
}
.price-label {
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 0.4rem;
}
.price-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.5rem;
    font-weight: 300;
    line-height: 1;
    color: #F4C89A;
}
.price-sub {
    font-size: 0.78rem;
    opacity: 0.55;
    margin-top: 0.4rem;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, #C8956C 0%, #A8704A 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(200, 149, 108, 0.4) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(200, 149, 108, 0.5) !important;
}

/* SUCCESS */
.success-box {
    background: linear-gradient(135deg, #2C5A2E 0%, #3A7A3C 100%);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    color: white;
    box-shadow: 0 12px 40px rgba(44, 90, 46, 0.3);
}
.success-box h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.2rem;
    font-weight: 300;
}

/* SUMMARY */
.summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(200,149,108,0.1);
    font-size: 0.9rem;
}
.summary-row:last-child { border-bottom: none; }
.summary-key { color: #7A5C45; font-size: 0.78rem; letter-spacing: 0.05em; text-transform: uppercase; }
.summary-val { color: #2C1A0E; font-weight: 500; text-align: right; max-width: 60%; }

/* INFO BOX */
.info-box {
    background: rgba(200, 149, 108, 0.06);
    border-left: 3px solid #C8956C;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #7A5C45;
    margin: 0.5rem 0;
}

[data-testid="column"] { padding: 0 0.5rem !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #FDF8F3; }
::-webkit-scrollbar-thumb { background: rgba(200,149,108,0.4); border-radius: 3px; }
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
        if not imie.strip():
            errors.append("Podaj imię i nazwisko.")
        if not telefon.strip():
            errors.append("Podaj numer telefonu.")
        if not email.strip() or "@" not in email:
            errors.append("Podaj poprawny adres e-mail.")
        if not fillings:
            errors.append("Wybierz co najmniej jedno nadzienie.")

        if errors:
            for e in errors:
                st.error(f"⚠️ {e}")
        else:
            st.session_state.submitted = True
            st.session_state.order_data = {
                "id": st.session_state.order_id,
                "imie": imie,
                "telefon": telefon,
                "email": email,
                "odbiór": str(odbiór),
                "tier": tier,
                "porcje": porcje,
                "floors": floors,
                "sponge": sponge,
                "fillings": fillings,
                "decoration": decoration,
                "kolor": kolor.split(" (")[0],
                "extras": extras,
                "napis": napis,
                "gluten_free": is_gluten,
                "vegan": is_vegan,
                "inspiracje": inspiracje,
                "price": price,
            }
            st.rerun()

# ─── SUCCESS ──────────────────────────────────────────────────────────────────
else:
    d = st.session_state.order_data

    st.markdown(f"""
    <div class="success-box">
        <div style="font-size:3rem;margin-bottom:0.6rem">🎂</div>
        <h2>Zamówienie złożone!</h2>
        <p style="opacity:0.75;font-size:0.95rem;margin-top:0.5rem">
            Skontaktujemy się z Tobą w ciągu 24 godzin, aby potwierdzić szczegóły.
        </p>
        <div style="background:rgba(255,255,255,0.1);border-radius:10px;padding:0.7rem 1.5rem;display:inline-block;margin-top:1.2rem;">
            <div style="font-size:0.65rem;letter-spacing:0.25em;opacity:0.6;text-transform:uppercase;">Numer zamówienia</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:300;color:#A8F0AA;">{d["id"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""<div class="section-card">
        <div class="section-title"><span class="section-num">✓</span> Podsumowanie zamówienia</div>
    """, unsafe_allow_html=True)

    rows = [
        ("Klient", d["imie"]),
        ("Telefon", d["telefon"]),
        ("E-mail", d["email"]),
        ("Data odbioru", d["odbiór"]),
        ("Seria tortu", d["tier"]),
        ("Porcje", f'{d["porcje"]} szt.'),
        ("Piętra", str(d["floors"])),
        ("Biszkopt", d["sponge"]),
        ("Nadzienie", ", ".join(d["fillings"])),
        ("Dekoracja", d["decoration"]),
        ("Paleta kolorów", d["kolor"]),
        ("Dodatki", ", ".join(d["extras"]) if d["extras"] else "—"),
        ("Napis", d["napis"] if d["napis"] else "—"),
        ("Bez glutenu", "Tak" if d["gluten_free"] else "Nie"),
        ("Wegańskie", "Tak" if d["vegan"] else "Nie"),
    ]

    rows_html = "".join(
        f'<div class="summary-row"><span class="summary-key">{k}</span><span class="summary-val">{v}</span></div>'
        for k, v in rows
    )
    st.markdown(rows_html + "</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="price-box">
        <div class="price-label">Szacunkowa cena</div>
        <div class="price-value">{fmt_price(d["price"])}</div>
        <div class="price-sub">Ostateczna kwota zostanie potwierdzona telefonicznie</div>
    </div>
    """, unsafe_allow_html=True)

    if d.get("inspiracje"):
        st.markdown(f'<div class="info-box">💬 <strong>Uwagi klienta:</strong> {d["inspiracje"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("↩ Złóż nowe zamówienie"):
        for key in ["submitted", "order_id", "order_data"]:
            st.session_state.pop(key, None)
        st.rerun()
