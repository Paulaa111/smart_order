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
    page_title="Sweet Order · Cukiernia",
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

/* Tło i Fonty */
.stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg-light) !important;
    font-family: 'Inter', sans-serif;
}

/* Naprawa ramek - koniec z czerwonym kliknięciem! */
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
    border: 1px solid var(--beige-dark) !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: var(--burgundy) !important;
    box-shadow: 0 0 0 2px rgba(99, 13, 22, 0.1) !important;
}

/* Nowoczesne karty sekcji */
.section-card {
    background: white;
    border-left: 5px solid var(--burgundy);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.section-title {
    font-family: 'Playfair Display', serif;
    color: var(--burgundy);
    font-size: 1.4rem;
}

/* Burgundowy przycisk */
.stButton > button {
    background: var(--burgundy) !important;
    color: white !important;
    border-radius: 0px !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Box z ceną */
.price-box {
    background: var(--burgundy);
    color: white;
    padding: 2rem;
    text-align: center;
}
.price-value {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem;
}
</style>


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
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False


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
        st.markdown("#### 📅 Zarządzaj niedostępnymi datami")

        blocked = load_blocked_dates()

        # Add new blocked date
        new_blocked = st.date_input(
            "Zablokuj datę",
            min_value=date.today(),
            key="admin_new_date"
        )
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("➕ Zablokuj", use_container_width=True):
                d_str = str(new_blocked)
                if d_str not in blocked:
                    blocked.append(d_str)
                    save_blocked_dates(blocked)
                    st.success(f"Zablokowano {d_str}")
                    st.rerun()
                else:
                    st.warning("Już zablokowana")

        # Show and remove blocked dates
        st.markdown("#### 🚫 Zablokowane daty")
        if not blocked:
            st.info("Brak zablokowanych dat")
        else:
            blocked_sorted = sorted(blocked)
            for d_str in blocked_sorted:
                c1, c2 = st.columns([3, 1])
                with c1:
                    # Format date nicely
                    try:
                        dt = datetime.strptime(d_str, "%Y-%m-%d")
                        label = dt.strftime("%d.%m.%Y")
                    except:
                        label = d_str
                    st.markdown(f"🔴 **{label}**")
                with c2:
                    if st.button("🗑", key=f"del_{d_str}", help="Odblokuj"):
                        blocked.remove(d_str)
                        save_blocked_dates(blocked)
                        st.rerun()

        st.markdown("---")
        if st.button("🚪 Wyloguj", use_container_width=True):
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
        # Find next available date (skip blocked)
        blocked_dates = load_blocked_dates()
        default_date = datetime.today().date() + timedelta(days=3)
        while str(default_date) in blocked_dates:
            default_date += timedelta(days=1)

        odbiór = st.date_input(
            "Data odbioru",
            min_value=datetime.today().date() + timedelta(days=3),
            value=default_date,
        )

        # Block validation
        if str(odbiór) in blocked_dates:
            st.error("❌ Ta data jest niedostępna — cukiernia jest w tym dniu zamknięta lub zajęta. Wybierz inną datę.")
            date_ok = False
        else:
            date_ok = True

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
        <div class="price-sub">{porcje} porcji | {floors} {fl_label} | cena orientacyjna</div>
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

        if not date_ok:
            errors.append("Wybierz dostępną datę odbioru.")
        if errors:
            for e in errors:
                st.error(f"⚠️ {e}")
        else:
            order = {
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
            st.session_state.order_data = order

            # ── INTEGRACJE ────────────────────────────────────────
            with st.spinner("Zapisujemy zamówienie..."):
                sheets_ok = save_to_sheets(order)
                email_ok  = send_confirmation_emails(order)

            st.session_state.submitted = True
            st.session_state.sheets_ok = sheets_ok
            st.session_state.email_ok  = email_ok
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

    # ── ANKIETA ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="section-card">
        <div class="section-title"><span class="section-num">💬</span> Chwila na feedback</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<p style="color:#7A5C45;font-size:0.9rem;margin-bottom:1rem">Bardzo zależy nam na Twojej opinii! Zajmie to dosłownie 30 sekund 🙏</p>', unsafe_allow_html=True)

    if "survey_sent" not in st.session_state:
        st.session_state.survey_sent = False

    if not st.session_state.survey_sent:
        col1, col2 = st.columns(2)
        with col1:
            czytelnosc = st.select_slider(
                "📋 Jak oceniasz czytelność konfiguratora?",
                options=["😕 Słabo", "😐 Ujdzie", "🙂 Dobrze", "😊 Bardzo dobrze", "🤩 Świetnie!"],
                value="😊 Bardzo dobrze",
            )
            latwos = st.select_slider(
                "🖱️ Jak łatwo było złożyć zamówienie?",
                options=["😕 Trudno", "😐 Średnio", "🙂 W porządku", "😊 Łatwo", "🤩 Super łatwo!"],
                value="😊 Łatwo",
            )
        with col2:
            przydatnosc = st.select_slider(
                "⭐ Czy konfiguratorjest przydatny?",
                options=["😕 Niezbyt", "😐 Może być", "🙂 Tak", "😊 Zdecydowanie tak", "🤩 Niezbędny!"],
                value="😊 Zdecydowanie tak",
            )
            polecenie = st.select_slider(
                "🗣️ Czy polecisz nas znajomym?",
                options=["😕 Raczej nie", "😐 Nie wiem", "🙂 Pewnie tak", "😊 Tak!", "🤩 Już polecam!"],
                value="😊 Tak!",
            )

        co_zmienic = st.text_area(
            "💡 Co moglibyśmy poprawić lub dodać?",
            placeholder="Twoja sugestia jest dla nas cenna...",
            height=80,
        )

        if st.button("✦ Wyślij opinię"):
            # Save survey to sheets
            survey_data = {
                "order_id": d["id"],
                "czytelnosc": czytelnosc,
                "latwos": latwos,
                "przydatnosc": przydatnosc,
                "polecenie": polecenie,
                "sugestie": co_zmienic,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            try:
                from integrations import get_sheets_client
                import streamlit as st
                gc = get_sheets_client()
                sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
                sh = gc.open_by_key(sheet_id)
                # Drugi arkusz na ankiety
                try:
                    ws = sh.worksheet("Ankiety")
                except:
                    ws = sh.add_worksheet(title="Ankiety", rows=1000, cols=10)
                    ws.insert_row(["ID zamówienia", "Czytelność", "Łatwość", "Przydatność", "Polecenie", "Sugestie", "Data"], 1)
                ws.append_row([
                    survey_data["order_id"],
                    survey_data["czytelnosc"],
                    survey_data["latwos"],
                    survey_data["przydatnosc"],
                    survey_data["polecenie"],
                    survey_data["sugestie"],
                    survey_data["data"],
                ])
            except Exception as e:
                pass  # Nie blokujemy jeśli błąd
            st.session_state.survey_sent = True
            st.rerun()
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#2C5A2E,#3A7A3C);border-radius:16px;
            padding:1.5rem 2rem;text-align:center;color:white;margin-bottom:1rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">🙏</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:300">
                Dziękujemy za opinię!</div>
            <div style="font-size:0.85rem;opacity:0.75;margin-top:0.4rem">
                Twój feedback pomaga nam się rozwijać</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↩ Złóż nowe zamówienie"):
        for key in ["submitted", "order_id", "order_data", "survey_sent"]:
            st.session_state.pop(key, None)
        st.rerun()
