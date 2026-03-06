# 🎂 Smart Order — Cukiernia Artystyczna

Aplikacja Streamlit do składania zamówień na torty.

## Struktura plików

```
smart_order/
├── app.py           ← Główna aplikacja
├── style.css        ← Style CSS (musi być w tym samym folderze co app.py)
├── orders.json      ← Baza zamówień (tworzy się automatycznie)
└── requirements.txt
```

## Uruchomienie lokalne

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Wdrożenie na Streamlit Cloud

1. Umieść pliki w repozytorium GitHub (folder `smart_order/`)
2. Zaloguj się na [share.streamlit.io](https://share.streamlit.io)
3. Utwórz nową aplikację wskazując `app.py`
4. Gotowe!

> **Uwaga**: `orders.json` na Streamlit Cloud nie będzie trwały między restartami.
> Do produkcji zalecane jest podpięcie bazy danych (np. Supabase, Firebase lub Google Sheets).

## Funkcje aplikacji

- ✅ Katalog tortów w 3 kategoriach (9 tortów)
- ✅ Wybór rozmiaru, nadzienia i dekoracji
- ✅ Kalkulator ceny w czasie rzeczywistym
- ✅ Napis na torcie, alergie, uwagi
- ✅ Dane kontaktowe i termin odbioru
- ✅ Opcja dostawy
- ✅ Potwierdzenie z numerem zamówienia
- ✅ Zapisywanie zamówień do JSON
