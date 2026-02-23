# Notion – przygotowanie pod integrację z botem

Jesteś na etapie: **szablon Notion gotowy → trzeba go podłączyć do integracji**.

---

## Co już masz (z czatu)

- Internal Integration utworzona (np. „Finance System”)
- Uprawnienia: Read content, Insert content, Update content
- Comment capabilities: wyłączone
- User capabilities: No user information
- **Internal Integration Secret** skopiowany i schowany (nie wklejaj do repozytorium)

---

## Krok 1: Upewnij się, że bazy są w TWOIM workspace

Darmowe szablony często są „z cudzego” workspace. Wtedy **Share** może nie działać lub integracja nie widzi baz.

### Opcja A: Szablon jest w twoim workspace i jesteś Owner

1. Otwórz **Expenses** jako pełną stronę (⋯ → *Open as full page*).
2. W prawym górnym rogu kliknij **Share**.
3. **Invite** → wpisz nazwę integracji (np. *Finance System*) → wybierz ją → Invite.
4. To samo zrób dla **Incomes** i **Transfers** (oraz ewentualnie **Accounts**, jeśli bot ma tam pisać).

Jeśli **Share** się nie pokazuje – przejdź do Opcji B.

### Opcja B: Szablon z marketplace / brak Share

Zrób **własne, czyste bazy** w swoim workspace:

1. W Notion utwórz nową stronę (np. *Finance System Core*).
2. W środku utwórz **nową bazę** (Table – Full page) dla każdej z:
   - **Expenses**
   - **Incomes**
   - **Transfers**
3. Skopiuj z szablonu strukturę kolumn (nazwy i typy), żeby było tak samo jak w ulubionym szablonie.
4. Dla tych **nowych** baz od razu kliknij **Share** → Invite → twoja integracja.

W ten sposób masz 100% kontrolę i integracja na pewno będzie mogła pisać do baz.

---

## Krok 2: Struktura baz – co bot musi „widzieć”

Żeby później napisać bota, bazy muszą mieć kolumny, które API Notion obsługuje. Typy w Notion = typy w API.

### Baza: **Expenses** (wydatki)

| Kolumna (EN) | Typ w Notion   | Opis                          |
|--------------|----------------|-------------------------------|
| Name / Title | Title          | Krótki opis (np. „Biedronka”) |
| Amount       | Number         | Suma (np. 45.50)              |
| Account      | Select lub Relation | Konto: Revolut, Banca Polacca, Muserbank, itd. |
| Category     | Select lub Relation | Kategoria z listy (Apartment, Bills, Transport, …) |
| Date         | Date           | Data transakcji               |
| Type         | Select         | np. Expense / Income / Transfer |
| Description  | Text           | Opcjonalne notatki             |
| Photo        | URL            | Link do zdjęcia (np. z Telegrama) |

### Baza: **Incomes** (przychody)

Analogicznie: Amount, Account, Category, Date, Description, ewentualnie Photo.

### Baza: **Transfers** (przelewy między kontami)

Np.: Amount, From (Account), To (Account), Date, Description.

### Baza / lista: **Accounts** (konta)

Jeśli trzymasz listę banków w Notion – np. kolumny: **Name** (Title), **Currency**, **Type** (Bank / Cash).  
Bot będzie mógł wybierać konto z tej listy (Relation lub Select).

---

## Krok 3: Zebranie ID baz (będzie potrzebne w bocie)

Gdy integracja ma już dostęp do baz:

1. Otwórz bazę (np. Expenses) w przeglądarce.
2. URL wygląda mniej więcej tak:  
   `https://www.notion.so/TwojaPrzestrzeń/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...`
3. **ID bazy** to ciąg 32 znaków (bez myślników) – ten `xxxxxxxx...` z URL.  
   Notion czasem pokazuje ID z myślnikami; w kodzie zwykle używa się wersji bez myślników.

Te ID zapiszesz później w pliku `.env` bota (np. `NOTION_EXPENSES_DATABASE_ID=...`).

---

## Podsumowanie – checklist

- [ ] Internal Integration utworzona, token (Secret) zapisany u siebie
- [ ] Bazy **Expenses**, **Incomes**, **Transfers** są w twoim workspace (własne lub z szablonu, gdzie widzisz Share)
- [ ] Dla każdej z tych baz: **Share** → Invite → twoja integracja
- [ ] Kolumny w bazach pasują do powyższej struktury (lub masz listę, co zmienić)
- [ ] Zapisane ID baz (z URL) – na użytek bota

Jak skończysz ten etap, napisz **„Integracja gotowa”** (albo co już zrobiłaś), wtedy następny krok to: **logika bota i zapis do Notion (kod w Cursor)**.
