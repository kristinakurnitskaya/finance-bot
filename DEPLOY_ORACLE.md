# Deploy bota na Oracle Cloud – Always Free

Bot będzie działał 24/7 na darmowej maszynie wirtualnej (VM). Potrzebujesz ok. 30–45 minut przy pierwszym razem.

---

## Krok 1: Konto Oracle Cloud

1. Wejdź na **[oracle.com/cloud/free](https://www.oracle.com/cloud/free/)**.
2. Kliknij **„Start for free”**.
3. Wypełnij formularz (e-mail, kraj, imię itd.).  
   **Uwaga:** potrzebna jest karta (do weryfikacji) – przy Always Free **nie są pobierane opłaty** jeśli nie przekroczysz limitów.
4. Po rejestracji zaloguj się do **Oracle Cloud Console** (cloud.oracle.com).

---

## Krok 2: Utworzenie VM (instancji)

1. W menu (≡) wybierz **Compute** → **Instances**.
2. Kliknij **„Create instance”**.
3. Ustaw:
   - **Name:** np. `finance-bot`
   - **Placement:** zostaw domyślne (np. dowolna Availability Domain).
   - **Image and shape:**  
     - **Image:** wybierz **Ubuntu 22.04** (Canonical).  
     - **Shape:** kliknij **„Edit”** przy Shape → wybierz **VM.Standard.E2.1.Micro** (Always Free-eligible, 1 GB RAM).
   - **Networking:** zostaw domyślną VCN (Virtual Cloud Network).  
     - Jeśli jest opcja **„Assign a public IPv4 address”** – ustaw **Yes**.
   - **Add SSH keys:**  
     - Wybierz **„Generate a key pair for me”** → **„Save Private Key”** i **„Save Public Key”** – zapisz oba pliki (np. `oracle_key` i `oracle_key.pub`).  
     - **Prywatny klucz** będzie potrzebny do SSH (nie udostępniaj go nikomu).
4. Kliknij **„Create”**.  
   Poczekaj 1–2 minuty, aż status instancji zmieni się na **Running**.

---

## Krok 3: Otwarcie portu SSH (jeśli nie możesz się połączyć)

1. W Oracle Console: **Networking** → **Virtual Cloud Networks** → wybierz swoją VCN.
2. **Security Lists** → kliknij domyślną listę (np. **Default Security List**).
3. **Ingress Rules** → **Add Ingress Rules**:
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** TCP
   - **Destination Port Range:** `22`
   - **Description:** np. `SSH`
4. Zapisz.  
   Dzięki temu z internetu da się połączyć przez SSH (port 22).

---

## Krok 4: Połączenie SSH z VM

1. W **Compute** → **Instances** skopiuj **Public IP address** swojej instancji (np. `132.145.xxx.xxx`).
2. Na swoim Macu otwórz **Terminal**.
3. Ustaw uprawnienia do klucza (zamień ścieżkę na tę, gdzie zapisałaś `oracle_key`):
   ```bash
   chmod 400 ~/Downloads/oracle_key
   ```
4. Połącz się (zamień `PRYWATNA_SCIEEZKA` i `PUBLICZNY_IP`):
   ```bash
   ssh -i PRYWATNA_SCIEEZKA ubuntu@PUBLICZNY_IP
   ```
   Np.:
   ```bash
   ssh -i ~/Downloads/oracle_key ubuntu@132.145.xxx.xxx
   ```
5. Przy pierwszym połączeniu zapyta „Are you sure you want to continue connecting?” – wpisz **yes** i Enter.  
   Powinnaś być na VM (prompt np. `ubuntu@finance-bot:~$`).

---

## Krok 5: Na VM – instalacja Pythona i Gita

Wklej po kolei (po każdym Enter poczekaj na zakończenie):

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

---

## Krok 6: Klonowanie repozytorium

```bash
cd ~
git clone https://github.com/kristinakurnitskaya/finance-bot.git
cd finance-bot
```

(Repo jest publiczne albo jest Twoje – jeśli było private, na VM i tak nie wpisujesz hasła; ewentualnie skonfigurujesz token później.)

---

## Krok 7: Środowisko i zależności

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Krok 8: Plik .env (zmienne środowiskowe)

Utwórz plik `.env` na VM. Wklej **jedną** linię (zamień na swoje wartości z lokalnego `.env`):

```bash
nano .env
```

W edytorze wklej (użyj swoje prawdziwe wartości):

```
TELEGRAM_BOT_TOKEN=twoj_token_z_botfather
NOTION_SECRET=twoj_notion_secret
NOTION_EXPENSES_DATABASE_ID=28450736c8d781c69e06c9b783ed4aed
NOTION_INCOME_DATABASE_ID=28450736c8d78129a189dd2594bfce91
NOTION_ACCOUNTS_DATABASE_ID=28450736c8d781838c14de070ca79e7e
NOTION_CATEGORIES_DATABASE_ID=28450736c8d78149994eca6f1bb1636d
NOTION_TRANSFERS_DATABASE_ID=28450736c8d781baa868f729b48567d9
```

Zapisz: **Ctrl+O**, Enter, potem **Ctrl+X**.

(Lub skopiuj całą zawartość swojego lokalnego `.env` i wklej do `nano .env` – bez linii z komentarzami jeśli wolisz.)

---

## Krok 9: Uruchomienie bota w tle (screen)

Żeby bot działał po zamknięciu SSH:

```bash
screen -S bot
python bot.py
```

Zobaczysz w logach np. „Bot uruchomiony…”.  
Odłącz się od `screen` (bot dalej działa): **Ctrl+A**, potem **D**.

---

## Krok 10: Sprawdzenie w Telegramie

W Telegramie wyślij do bota **/start** lub kwotę – bot powinien odpowiadać (VM ma dostęp do internetu).

---

## Przydatne komendy później

- **Wejść z powrotem w ekran z botem:**  
  `screen -r bot`  
  (wyjście: **Ctrl+A**, potem **D**)

- **Zatrzymać bota:**  
  `screen -r bot` → **Ctrl+C** → **Ctrl+A**, **D**

- **Uruchomić bota od nowa:**  
  `cd ~/finance-bot && source venv/bin/activate && screen -S bot -d -m python bot.py`

- **Zaktualizować kod z GitHub:**  
  `cd ~/finance-bot && git pull && source venv/bin/activate`  
  Potem zrestartuj bota (zatrzymaj w screen i uruchom ponownie jak wyżej).

---

## Jeśli coś nie działa

- **SSH:** Sprawdź, że używasz **Public IP** instancji i że w Security List jest port 22 (Ingress).
- **Bot nie odpowiada:** Na VM w `screen -r bot` sprawdź, czy nie ma błędów (Notion, token itd.).
- **Brak internetu na VM:** Domyślnie VM ma ruch wychodzący; jeśli coś blokujesz w VCN, sprawdź Outgress rules.

---

## Koszty

Always Free – przy jednej małej VM (VM.Standard.E2.1.Micro) i bez wykraczania poza limity **0 USD**. Karta służy tylko do weryfikacji; upewnij się, że nie tworzysz płatnych zasobów (zostaj przy „Always Free” / Free Tier).
