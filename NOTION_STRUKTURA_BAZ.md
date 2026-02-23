# Notion – struktura baz „od zera” (pod integrację z botem)

Zrób to w **swoim** workspace (nowa strona), żeby od razu mieć **Share** i zaprosić integrację.

---

## Strona główna

1. W Notion: **New page**.
2. Nazwa np. **Finance System** (lub Finance Tracker).
3. W środku strony tworzysz poniższe bazy. Każdą jako **Table – Full page** (żeby potem mieć Share).

---

## Baza 1: **Accounts** (konta / banki)

Najpierw lista kont – bot będzie z niej wybierał.

| Nazwa kolumny | Typ w Notion | Uwagi |
|---------------|----------------|--------|
| **Name** | Title | np. Revolut, Banca Polacca, Muserbank, Contanti |
| Currency | Select | EUR, PLN, itd. |
| Type | Select | Bank, Cash, Altro |

**Jak dodać:** Nowa baza → Full page → dodaj kolumny (Property) → ustaw typy. Wypełnij kilka wierszy (Revolut, Banca Polacca, …).

---

## Baza 2: **Categories** (kategorie)

Jedna baza z kategoriami – tak jak w Twoim szablonie (Apartment, Bills, Transport, Eating Out, itd.).

| Nazwa kolumny | Typ w Notion | Uwagi |
|---------------|----------------|--------|
| **Name** | Title | Nazwa kategorii |
| Type | Select | Spesa, Entrata, Investimento, Trasferimento |

Albo bez kolumny Type – wtedy w **Expenses** po prostu wybierasz z listy.  
Wypełnij wiersze: Apartment, Bills, Internet, Transport, Home Food, Eating Out, Taxi, Gioia, Sport, House, Tech, Presents, Documents, Events, Charities, Betting, Nostro Benessere, Business, Learning, Travels, Clothes, Health + ewentualnie Investimenti – ETF, Crypto, Azioni, ecc.

---

## Baza 3: **Expenses** (wydatki – tu bot będzie pisał)

| Nazwa kolumny | Typ w Notion | Uwagi |
|---------------|----------------|--------|
| **Name** | Title | Krótki opis (np. Biedronka, Lidl) – bot może tu wpisać sklep/opis |
| Amount | Number | Suma (format: Number, bez waluty w tej kolumnie) |
| Account | Relation | Relation do bazy **Accounts** (many-to-one) |
| Category | Relation | Relation do bazy **Categories** (many-to-one) |
| Date | Date | Data transakcji |
| Type | Select | Spesa | Entrata | Investimento | Trasferimento |
| Description | Text | Opcjonalne notatki |
| Photo | URL | Link do zdjęcia (np. z Telegrama) |
| Utente | Select | np. Io, Marito – kto dodał |

**Jak dodać:** New database → Full page. Dodaj kolumny: Amount (Number), Account (Relation → wybierz bazę Accounts), Category (Relation → Categories), Date (Date), Type (Select – wpisz 4 opcje), Description (Text), Photo (URL), Utente (Select – Io, Marito).

---

## Baza 4: **Incomes** (przychody)

Możesz zrobić osobną bazę albo **jeden wpis w Expenses** z Type = Entrata.  
Jeśli chcesz osobną bazę:

| Nazwa kolumny | Typ w Notion |
|---------------|----------------|
| **Name** | Title |
| Amount | Number |
| Account | Relation → Accounts |
| Category | Relation → Categories lub Select (Zarplata, Altro, …) |
| Date | Date |
| Description | Text |
| Utente | Select (Io, Marito) |

---

## Baza 5: **Transfers** (przelewy między kontami)

| Nazwa kolumny | Typ w Notion |
|---------------|----------------|
| **Name** | Title |
| Amount | Number |
| From | Relation → Accounts |
| To | Relation → Accounts |
| Date | Date |
| Description | Text |
| Utente | Select |

---

## Po stworzeniu

1. Wejdź w **każdą** bazę (Expenses, Incomes, Transfers, Accounts – te, do których bot ma pisać).
2. **⋯** → **Open as full page**.
3. **Share** → **Invite** → twoja integracja (np. Finance System).
4. Z URL każdej bazy skopiuj **ID** (32 znaki, w środku adresu) – przyda się do `.env` bota.

---

## Różnice względem szablonu z marketplace

- **Struktura** jest dopasowana do API Notion i bota (Relation, Select, Number, Date, URL).
- **Wygląd** (ikony, kolory, dashboard z linked databases, widoki) możesz dodać potem – skopiuj widoki i układy ze starego szablonu i podłącz je do tych nowych baz (Same database / Link to database).
- Ważne: bazy są **u Ciebie**, więc **Share** i integracja będą działać.

Jeśli podasz nazwy kolumn i typy ze szablonu z marketplace (albo zrzut ekranu), można dopasować tę strukturę 1:1.
