# Bot ↔ Google Sheets – jak to się łączy

Ten plik opisuje, jak zapis bota w **Transactions** współpracuje z Twoimi zakładkami i formułami.

## Skąd bot bierze listy (dropdown = to samo co w arkuszu)

Bot **czyta opcje z arkusza**, żeby przyciski w Telegramie były takie same jak listy rozwijane w tabeli:

| Lista      | Źródło w arkuszu        |
|------------|--------------------------|
| Konta      | **Accounts** – kolumna A, wiersze 2–100 |
| Kategorie (Expense) | **Dashboard** – kolumna A, wiersze 27–50 |
| Kategorie (Income)  | **Dashboard** – kolumna G, wiersze 27–30 |
| Kredyty (Loan Payment) | **Loans** – kolumna A, wiersze 2–50 |

Jeśli któryś zakres jest pusty lub błąd, bot używa list zapasowych z kodu (CATEGORIES, ACCOUNTS, INCOME_CATEGORIES).

## Zakładka Transactions (źródło danych)

Bot dopisuje wiersze z kolumnami:

| Kolumna | Zawartość od bota |
|--------|--------------------|
| A Date | YYYY-MM-DD |
| B Type | Expense, Income, Transfer, Investment, Loan Payment |
| C Category | np. Food, Apartment, Salary… (zgodne z listą) |
| D Account | np. Revolut Paolo, Santander Kris… (zgodne z listą) |
| E Amount | Liczba: **ujemna** dla Expense/Transfer Out, **dodatnia** dla Income/Transfer In |
| F Currency | EUR, USD, PLN… |
| G Amount EUR | Formuła: `=IFERROR(E×VLOOKUP(F; ExchangeRates!A:B; 2; 0); "")` |
| H Note | Notatka |
| I Month | Miesiąc **po włosku** (np. marzo, aprile) |
| J Year | Rok liczbowo (np. 2026) |

- **Transfer** = dwa wiersze: jeden „Transfer Out” (minus z konta), drugi „Transfer In” (plus na konto).

---

## Dashboard

- **Rok (B2)** i **miesiąc (B3)** – wybierasz ręcznie; filtry w formułach używają **$B$2** (Year) i **$B$3** (Month po włosku).
- **Expenses – Actual (D27:D50):**  
  `SUMIFS(Transactions!$G:$G; Transactions!$B:$B; "Expense"; Transactions!$C:$C; A27; Transactions!$I:$I; $B$3; Transactions!$J:$J; $B$2)`  
  → Sumuje **Amount EUR** (G) dla Type=Expense, Category=A27, Month=B3, Year=B2. **Zapis bota jest zgodny** (I = miesiąc po włosku, J = rok).
- **Income – Actual (J27:J30):**  
  `SUMIFS(Transactions!$E:$E; ...; "Income"; ...; Transactions!$I:$I; $B$3; Transactions!$J:$J; $B$2)`  
  → Sumuje **Amount** (E) dla dochodów. **Zapis bota jest zgodny** (dodatnie kwoty w E dla Income).
- **Years (M3) / Months (N3):**  
  Unikalne lata/miesiące z Transactions J i I – po zapisie transakcji przez bota dane się tam pojawią.
- **Wykresy (O3:P3, Q3:R3):**  
  Używają kategorii i kwot z Expenses/Income – działają na tych samych SUMIFS co powyżej.

---

## Accounts – Current Balance (E)

`=IF(A2="";""; C2 + SUMIF(Transactions!$D:$D; A2; Transactions!$E:$E))`  
→ Sumuje **Amount** (E) po Account (D). Bot wpisuje w E kwoty z plusem/minusem, więc saldo się zgadza.

---

## Loans – Remaining Balance (E)

Bot zapisuje wpłaty **Loan Payment z minusem**; **C (Category)** = nazwa kredytu, **D (Account)** = konto bankowe (np. Santander Paolo).

**Poprawna formuła** (dopasowanie po C, kwoty ujemne w G):

```text
=IF(A2="";""; D2 + SUMIFS(Transactions!$G:$G; Transactions!$B:$B; "Loan Payment"; Transactions!$C:$C; A2))
```

---

## ExchangeRates

- Zakładka: **ExchangeRates** (domyślnie w .env; można nadpisać `GOOGLE_SHEETS_RATES_SHEET`).
- Bot w kolumnie G używa: `VLOOKUP(F; ExchangeRates!A:B; 2; 0)` (w ramach IFERROR).  
- Możesz mieć w tej zakładce np. `=GOOGLEFINANCE("CURRENCY:USDEUR")` itd.

---

## Podsumowanie

| Element | Zgodność |
|--------|----------|
| Transactions A–J | Bot wypełnia wszystkie kolumny; Month po włosku, Year jako liczba. |
| Dashboard Expenses (D27, SUMIFS po I, J, G) | Tak. |
| Dashboard Income (J27, SUMIFS po I, J, E) | Tak. |
| Accounts Current Balance (SUMIF po D, E) | Tak. |
| Loans Remaining Balance (SUMIFS po B, D, G) | Tak, jeśli w Transactions dla Loan Payment używasz D zgodnie z formułą. |
| ExchangeRates / Amount EUR (G) | Domyślna nazwa zakładki ustawiona na **ExchangeRates**. |

Po zapisie transakcji z Telegrama nowe wiersze w Transactions powinny poprawnie zasilać Dashboard, Accounts i Loans.
