"""
integrations.py — Google Sheets + Gmail dla Smart Order
"""

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


# ─────────────────────────────────────────────
# GOOGLE SHEETS
# ─────────────────────────────────────────────

def get_sheets_client():
    """Zwraca autoryzowanego klienta gspread."""
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


# ── NAGŁÓWKI (jedna definicja — używana w save i przy szukaniu kolumn) ────────
HEADERS = [
    "ID zamówienia", "Data złożenia", "Imię i nazwisko",
    "Telefon", "E-mail", "Data odbioru",
    "Seria tortu", "Porcje", "Piętra",
    "Biszkopt", "Nadzienie", "Dekoracja",
    "Paleta kolorów", "Dodatki", "Napis",
    "Bez glutenu", "Wegańskie", "Uwagi",
    "Cena (zł)", "Status",          # ← nowa kolumna
]


def save_to_sheets(order: dict) -> bool:
    """
    Dopisuje wiersz z zamówieniem do Google Sheets.
    Zwraca True przy sukcesie, False przy błędzie.
    """
    try:
        gc = get_sheets_client()
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1

        if ws.row_count < 2 or ws.cell(1, 1).value != "ID zamówienia":
            ws.insert_row(HEADERS, 1)

        row = [
            order.get("id", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            order.get("imie", ""),
            order.get("telefon", ""),
            order.get("email", ""),
            order.get("odbiór", ""),
            order.get("tier", ""),
            order.get("porcje", ""),
            order.get("floors", ""),
            order.get("sponge", ""),
            ", ".join(order.get("fillings", [])),
            order.get("decoration", ""),
            order.get("kolor", ""),
            ", ".join(order.get("extras", [])),
            order.get("napis", ""),
            "Tak" if order.get("gluten_free") else "Nie",
            "Tak" if order.get("vegan") else "Nie",
            order.get("inspiracje", ""),
            order.get("price", ""),
            "Nowe",                  # ← domyślny status
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True

    except Exception as e:
        st.warning(f"⚠️ Błąd zapisu do Google Sheets: {e}")
        return False


def mark_order_ready(order_id: str) -> bool:
    """
    Ustawia Status = 'Zrealizowane' dla wiersza o podanym ID zamówienia.
    Zwraca True przy sukcesie.
    """
    try:
        gc = get_sheets_client()
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        ws = gc.open_by_key(sheet_id).sheet1

        # Znajdź kolumnę Status
        header_row = ws.row_values(1)
        try:
            status_col = header_row.index("Status") + 1  # gspread liczy od 1
        except ValueError:
            # Kolumna jeszcze nie istnieje — dodaj nagłówek na końcu
            status_col = len(header_row) + 1
            ws.update_cell(1, status_col, "Status")

        # Znajdź wiersz z tym ID
        id_col_values = ws.col_values(1)  # kolumna A = ID zamówienia
        try:
            row_idx = id_col_values.index(order_id) + 1  # +1 bo gspread od 1
        except ValueError:
            return False  # nie znaleziono

        ws.update_cell(row_idx, status_col, "Zrealizowane")
        return True

    except Exception as e:
        st.warning(f"⚠️ Błąd aktualizacji statusu: {e}")
        return False


def get_order_row_by_id(order_id: str) -> dict | None:
    """
    Zwraca słownik z danymi wiersza (get_all_records) dla podanego ID.
    Potrzebne do wysyłki maila — mamy tylko ID z sidebara.
    """
    try:
        gc = get_sheets_client()
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        ws = gc.open_by_key(sheet_id).sheet1
        records = ws.get_all_records()
        for r in records:
            if str(r.get("ID zamówienia", "")) == order_id:
                return r
        return None
    except Exception:
        return None


# ─────────────────────────────────────────────
# GMAIL
# ─────────────────────────────────────────────

def send_confirmation_emails(order: dict) -> bool:
    """
    Wysyła dwa maile:
      1. Potwierdzenie do klienta
      2. Powiadomienie do cukierni
    """
    try:
        gmail_user = st.secrets["gmail"]["sender_email"]
        gmail_pass = st.secrets["gmail"]["app_password"]
        bakery_email = st.secrets["gmail"]["bakery_email"]

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)

            msg_client = _build_client_email(order, gmail_user)
            server.sendmail(gmail_user, order["email"], msg_client.as_string())

            msg_bakery = _build_bakery_email(order, gmail_user)
            server.sendmail(gmail_user, bakery_email, msg_bakery.as_string())

        return True

    except Exception as e:
        st.warning(f"⚠️ Błąd wysyłki e-mail: {e}")
        return False


def send_ready_email(order_row: dict) -> bool:
    """
    Wysyła klientowi powiadomienie, że tort jest gotowy do odbioru.
    Przyjmuje wiersz ze Sheets (dict z kluczami jak w HEADERS).
    """
    try:
        gmail_user = st.secrets["gmail"]["sender_email"]
        gmail_pass = st.secrets["gmail"]["app_password"]
        client_email = order_row.get("E-mail", "")

        if not client_email:
            return False

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            msg = _build_ready_email(order_row, gmail_user)
            server.sendmail(gmail_user, client_email, msg.as_string())

        return True

    except Exception as e:
        st.warning(f"⚠️ Błąd wysyłki maila 'gotowe': {e}")
        return False


# ─────────────────────────────────────────────
# SZABLONY HTML
# ─────────────────────────────────────────────

def _html_table(order: dict) -> str:
    """Generuje tabelę HTML ze szczegółami zamówienia (z dict zamówienia)."""
    rows = [
        ("Numer zamówienia", order.get("id", "")),
        ("Imię i nazwisko", order.get("imie", "")),
        ("Telefon", order.get("telefon", "")),
        ("E-mail", order.get("email", "")),
        ("Data odbioru", order.get("odbiór", "")),
        ("Seria tortu", order.get("tier", "")),
        ("Porcje", str(order.get("porcje", ""))),
        ("Piętra", str(order.get("floors", ""))),
        ("Biszkopt", order.get("sponge", "")),
        ("Nadzienie", ", ".join(order.get("fillings", []))),
        ("Dekoracja", order.get("decoration", "")),
        ("Paleta kolorów", order.get("kolor", "")),
        ("Dodatki", ", ".join(order.get("extras", [])) or "—"),
        ("Napis na torcie", order.get("napis", "") or "—"),
        ("Bez glutenu", "Tak" if order.get("gluten_free") else "Nie"),
        ("Wegańskie", "Tak" if order.get("vegan") else "Nie"),
        ("Uwagi", order.get("inspiracje", "") or "—"),
        ("Cena szacunkowa", f"{order.get('price', 0)} zł"),
    ]
    return _render_table(rows)


def _html_table_from_row(row: dict) -> str:
    """Generuje tabelę HTML ze szczegółami zamówienia (z wiersza Sheets)."""
    rows = [
        ("Numer zamówienia", row.get("ID zamówienia", "")),
        ("Data odbioru", row.get("Data odbioru", "")),
        ("Seria tortu", row.get("Seria tortu", "")),
        ("Porcje", str(row.get("Porcje", ""))),
        ("Piętra", str(row.get("Piętra", ""))),
        ("Biszkopt", row.get("Biszkopt", "")),
        ("Nadzienie", row.get("Nadzienie", "")),
        ("Dekoracja", row.get("Dekoracja", "")),
        ("Dodatki", row.get("Dodatki", "") or "—"),
        ("Napis na torcie", row.get("Napis", "") or "—"),
        ("Cena", f"{row.get('Cena (zł)', '')} zł"),
    ]
    return _render_table(rows)


def _render_table(rows: list[tuple]) -> str:
    trs = "".join(
        f"""<tr>
          <td style="padding:8px 16px;color:#7A5C45;font-size:13px;width:40%">{k}</td>
          <td style="padding:8px 16px;color:#2C1A0E;font-size:13px;font-weight:500">{v}</td>
        </tr>"""
        for k, v in rows
    )
    return f"""<table style="width:100%;border-collapse:collapse;background:#FFFCF8;
        border-radius:12px;overflow:hidden;border:1px solid #EAD9C8">{trs}</table>"""


def _base_template(title: str, body_html: str) -> str:
    return f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#F5EFE8;font-family:'DM Sans',Arial,sans-serif;">
      <div style="max-width:600px;margin:40px auto;background:#FFFFFF;
          border-radius:20px;overflow:hidden;box-shadow:0 4px 30px rgba(44,26,14,0.1)">

        <div style="background:linear-gradient(135deg,#2C1A0E,#4A2E1C);
            padding:40px 40px 30px;text-align:center">
          <div style="font-size:2.5rem;margin-bottom:8px">🎂</div>
          <div style="font-family:Georgia,serif;font-size:1.6rem;color:#F4C89A;
              font-weight:300;letter-spacing:-0.01em">Smart<strong>Order</strong></div>
          <div style="font-size:0.7rem;letter-spacing:0.2em;color:rgba(255,255,255,0.4);
              text-transform:uppercase;margin-top:4px">Cukiernia Artystyczna</div>
        </div>

        <div style="padding:32px 40px 8px">
          <h1 style="font-family:Georgia,serif;font-size:1.6rem;font-weight:400;
              color:#2C1A0E;margin:0 0 8px">{title}</h1>
        </div>

        <div style="padding:0 40px 32px">
          {body_html}
        </div>

        <div style="background:#FDF8F3;border-top:1px solid #EAD9C8;
            padding:24px 40px;text-align:center">
          <p style="font-size:12px;color:#A07855;margin:0">
            Cukiernia Artystyczna · ul. Słodka 12 · Warszawa<br>
            Tel: +48 22 123 45 67 · Pon–Pt: 9:00–18:00 · Sob: 9:00–14:00
          </p>
        </div>
      </div>
    </body></html>
    """


def _build_client_email(order: dict, sender: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎂 Potwierdzenie zamówienia {order['id']} — Cukiernia Artystyczna"
    msg["From"] = f"Cukiernia Artystyczna <{sender}>"
    msg["To"] = order["email"]

    body_html = f"""
    <p style="color:#2C1A0E;font-size:15px;line-height:1.7;margin-bottom:24px">
      Droga/i <strong>{order['imie'].split()[0]}</strong>,<br><br>
      Dziękujemy za złożenie zamówienia w naszej cukierni! 🎉<br>
      Poniżej znajdziesz szczegóły Twojego zamówienia.
      Skontaktujemy się z Tobą w ciągu <strong>24 godzin</strong>, aby potwierdzić szczegóły i ustalić zaliczkę.
    </p>
    {_html_table(order)}
    <div style="background:#FDF8F3;border-radius:12px;padding:16px 20px;
        margin-top:20px;border-left:3px solid #C8956C">
      <p style="font-size:13px;color:#7A5C45;margin:0">
        💳 Zaliczka 40% wymagana przy potwierdzeniu zamówienia.<br>
        Pozostała kwota płatna przy odbiorze (gotówka lub karta).
      </p>
    </div>
    """
    html = _base_template("Twoje zamówienie zostało złożone!", body_html)
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def _build_bakery_email(order: dict, sender: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🆕 Nowe zamówienie {order['id']} — {order['imie']} · {order['odbiór']}"
    msg["From"] = f"Smart Order System <{sender}>"
    msg["To"] = sender

    body_html = f"""
    <p style="color:#2C1A0E;font-size:15px;line-height:1.7;margin-bottom:24px">
      Wpłynęło nowe zamówienie przez aplikację Smart Order.<br>
      <strong>Data złożenia:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </p>
    {_html_table(order)}
    <div style="background:#FFF3CD;border-radius:12px;padding:16px 20px;
        margin-top:20px;border-left:3px solid #FFC107">
      <p style="font-size:13px;color:#856404;margin:0">
        ⚡ Prosimy o kontakt z klientem w ciągu 24 godzin w celu potwierdzenia zamówienia.
      </p>
    </div>
    """
    html = _base_template(f"Nowe zamówienie #{order['id']}", body_html)
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def _build_ready_email(order_row: dict, sender: str) -> MIMEMultipart:
    """Mail do klienta — tort gotowy do odbioru."""
    client_name = order_row.get("Imię i nazwisko", "")
    first_name = client_name.split()[0] if client_name else "Kliencie"
    order_id = order_row.get("ID zamówienia", "")
    pickup_date = order_row.get("Data odbioru", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎂 Twój tort jest gotowy! Zamówienie {order_id}"
    msg["From"] = f"Cukiernia Artystyczna <{sender}>"
    msg["To"] = order_row.get("E-mail", "")

    body_html = f"""
    <p style="color:#2C1A0E;font-size:15px;line-height:1.7;margin-bottom:24px">
      Droga/i <strong>{first_name}</strong>,<br><br>
      Mamy wspaniałą wiadomość — <strong>Twój tort jest gotowy do odbioru!</strong> 🎉<br><br>
      Czeka na Ciebie w naszej cukierni. Przypominamy, że zadeklarowana data odbioru to
      <strong>{pickup_date}</strong>.
    </p>

    {_html_table_from_row(order_row)}

    <div style="background:#E8F5E9;border-radius:12px;padding:20px 24px;
        margin-top:24px;border-left:4px solid #4CAF50">
      <p style="font-size:14px;color:#2E7D32;margin:0;font-weight:500">
        ✅ Zapraszamy do odbioru!
      </p>
      <p style="font-size:13px;color:#388E3C;margin:8px 0 0">
        Pamiętaj o uregulowaniu pozostałej kwoty przy odbiorze (gotówka lub karta).<br>
        W razie pytań zadzwoń: <strong>+48 22 123 45 67</strong>
      </p>
    </div>

    <div style="background:#FDF8F3;border-radius:12px;padding:16px 20px;margin-top:16px">
      <p style="font-size:12px;color:#A07855;margin:0">
        🕐 Godziny otwarcia: Pon–Pt 9:00–18:00 · Sob 9:00–14:00<br>
        📍 ul. Słodka 12, Warszawa
      </p>
    </div>
    """
    html = _base_template("Twój tort jest gotowy! 🎂", body_html)
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg
