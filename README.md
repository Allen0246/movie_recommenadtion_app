# Movie Recommendation Application

A small Flask web app that pulls movies from [The Movie Database (TMDB)](https://www.themoviedb.org/) into a local Postgres database, lets users track which movies they've watched (with a rating and date), get a random recommendation by genre, export their lists to Excel, and — for admins — manage users and view application logs.

Languages: [English](#english) | [Magyar](#magyar)

---

<a name="english"></a>
## English

### How it works

* **web** — a Flask app (Python 3.8) served over HTTPS by its own development server (started via `start.sh`, with an ad-hoc self-signed TLS certificate). On startup it:
  * creates the database tables,
  * creates the default `admin` and `user` accounts (if they don't already exist),
  * fetches the genre list from TMDB,
  * fetches movies released **today** from TMDB (`/discover/movie`) and stores new ones in Postgres.
* **postgres** — PostgreSQL 12, stores users, roles, movies, genres, and each user's watch history/ratings.
* **nginx** — terminates HTTPS on port `443` (mapped to host port `1334`) using the self-signed certificate in `services/nginx/certs/`, and reverse-proxies to the `web` container.

```
Browser --https:1334--> nginx --https--> web:5000 (Flask) --> postgres:5432
```

All three run together via Docker Compose.

### Tech stack

* Python 3.8 / Flask 2.2.2, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Excel
* PostgreSQL 12
* NGINX (TLS termination + reverse proxy)
* Bootstrap 5, DataTables (frontend)
* Docker / Docker Compose

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* A free [TMDB](https://www.themoviedb.org/) account and API Read Access Token

### Getting started

1. Copy the environment template and fill in your own values:
   ```
   cp .env.example .env
   ```
2. In `.env`, set:
   * `THEMOVIEDB_TOKEN` — your TMDB API Read Access Token
   * `SECRET_KEY` and `WTF_CSRF_SECRET_KEY` — random strings, e.g. generate with:
     ```
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   * Optionally change the default admin/user credentials and DB credentials (see [Environment variables](#environment-variables)).
3. Build and start everything:
   ```
   docker-compose up -d --build
   ```
4. Open `https://localhost:1334`. Your browser will warn about the self-signed certificate — this is expected for local development; accept/proceed to continue.

**Windows note:** if the `web` container fails with `exec ./start.sh: no such file or directory`, the file's line endings were saved as CRLF. Change `services/web/start.sh` to use **LF** line endings and rebuild.

### Environment variables

Set these in `.env` (see `.env.example` for a template):

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session signing key — set a long random value |
| `WTF_CSRF_SECRET_KEY` | CSRF protection key — set a different long random value |
| `LOG_BACKUP_COUNT` | Days of rotated log files to keep |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database credentials, used by both `web` and `postgres` |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Database connection target (defaults to the `postgres` service on `5432`) |
| `SQLALCHEMY_POOL_SIZE` | DB connection pool size |
| `THEMOVIEDB_HOSTNAME` | TMDB API host, normally `api.themoviedb.org` |
| `THEMOVIEDB_TOKEN` | Your TMDB API Read Access Token |
| `PRIMARY_RELEASE_DATE_GTE` | Start date used when fetching a wider movie range (see below) |
| `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` | Auto-created admin account credentials |
| `DEFAULT_USER_USERNAME` / `DEFAULT_USER_PASSWORD` | Auto-created regular user account credentials |
| `FLASK_APP`, `FLASK_ENV`, `USE_RELOADER`, `SERVER_NAME`, `FLASK_RUN_HOST`, `FLASK_RUN_PORT` | Flask runtime settings — leave as provided |

### Loading movies from a wider date range

By default, the app only fetches movies released **today**. To fetch a range instead:

1. In `.env`, set `PRIMARY_RELEASE_DATE_GTE` to the start date (`YYYY-MM-DD`) you want to fetch from.
2. In `services/web/project/extensions/REST_THEMOVIEDB.py`, in `get_movies()`, comment out the `'primary_release_date.gte': today,` line and uncomment the `'primary_release_date.gte': app.config['PRIMARY_RELEASE_DATE_GTE'],` line above it.
3. Rebuild/restart the `web` container. New movies are fetched on startup and whenever you click **Update** on the Movies page.

### Using the application

* Default accounts are created automatically: `admin / admin` and `user / user`. You can also register a new account at `/register` (registered users get the `user` role).
* **Everyone (logged in):**
  * **Home** — landing page after login.
  * **Movies** — browse movies currently in the database. **Update** fetches new movies from TMDB; **Export** downloads the list as an `.xlsx` file. Mark a movie as watched with a rating and date.
  * **My Movies** — movies you've marked as watched, with your rating and date. You can remove an entry, re-rate/re-date it, or export the list.
  * **Movie Recommendation** — pick a genre and get a random suggestion from movies in the database you haven't marked as watched.
  * **Log Out**
* **Admin only:**
  * **User** — list, create, edit, and delete user accounts and roles.
  * **System Log** — view and download the application's log files.

### Security notes

* `.env` holds real secrets and is git-ignored — never commit it. Use `.env.example` as the template and keep real values local (or in your deployment's secret manager).
* Rotate `SECRET_KEY`, `WTF_CSRF_SECRET_KEY`, `POSTGRES_PASSWORD`, and `THEMOVIEDB_TOKEN` if they were ever committed or shared.
* The default `admin`/`user` credentials and the TLS certificate/key bundled in `services/nginx/certs/` are for local development only — change the default passwords and replace the certificate before exposing this app beyond `localhost`.

### Credits

The login and home pages are adapted and customized from these free templates:

* Login page — [Login Form 14 (Colorlib)](https://colorlib.com/wp/template/login-form-14/)
* Home page — [Free Bootstrap Real Estate Template (Untree.co)](https://untree.co/free-templates/property-free-bootstrap-real-estate-template/)

---

<a name="magyar"></a>
## Magyar

### Hogyan működik

* **web** — egy Flask alkalmazás (Python 3.8), amelyet a saját fejlesztői szervere szolgál ki HTTPS-en (a `start.sh` indítja, egy ad-hoc, önaláírt TLS tanúsítvánnyal). Induláskor:
  * létrehozza az adatbázis táblákat,
  * létrehozza az alapértelmezett `admin` és `user` felhasználókat (ha még nem léteznek),
  * lekéri a műfaj listát a TMDB-től,
  * lekéri a **mai napon** megjelent filmeket a TMDB-től (`/discover/movie`), és az újakat elmenti a Postgres adatbázisba.
* **postgres** — PostgreSQL 12, ebben tárolódnak a felhasználók, szerepkörök, filmek, műfajok, valamint a felhasználók megtekintési előzményei/értékelései.
* **nginx** — a `443`-as porton (host oldalon `1334`-re leképezve) zárja le a HTTPS kapcsolatot a `services/nginx/certs/` mappában lévő önaláírt tanúsítvánnyal, majd továbbítja a kéréseket a `web` konténer felé.

```
Böngésző --https:1334--> nginx --https--> web:5000 (Flask) --> postgres:5432
```

Mindhárom konténer Docker Compose-zal indul együtt.

### Felhasznált technológiák

* Python 3.8 / Flask 2.2.2, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Excel
* PostgreSQL 12
* NGINX (TLS lezárás + reverse proxy)
* Bootstrap 5, DataTables (frontend)
* Docker / Docker Compose

### Előfeltételek

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Egy ingyenes [TMDB](https://www.themoviedb.org/) fiók és API Read Access Token

### Indítás lépései

1. Másold le a környezeti változó sablont, és töltsd ki a saját értékeiddel:
   ```
   cp .env.example .env
   ```
2. A `.env` fájlban állítsd be:
   * `THEMOVIEDB_TOKEN` — a TMDB API Read Access Token-ed
   * `SECRET_KEY` és `WTF_CSRF_SECRET_KEY` — véletlenszerű karakterláncok, pl.:
     ```
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   * Ha szükséges, módosítsd az alapértelmezett admin/user és adatbázis hitelesítő adatokat (lásd [Környezeti változók](#környezeti-változók)).
3. Build és indítás:
   ```
   docker-compose up -d --build
   ```
4. Nyisd meg: `https://localhost:1334`. A böngésző figyelmeztetni fog az önaláírt tanúsítvány miatt — ez helyi fejlesztés esetén elvárt, fogadd el a folytatáshoz.

**Windows megjegyzés:** ha a `web` konténer ezzel a hibával áll le: `exec ./start.sh: no such file or directory`, akkor a fájl sorvégei CRLF formátumban vannak mentve. Állítsd a `services/web/start.sh` sorvégeit **LF**-re, majd építsd újra a konténert.

### Környezeti változók

Ezeket a `.env` fájlban kell beállítani (sablon: `.env.example`):

| Változó | Szerepe |
|---|---|
| `SECRET_KEY` | Flask session aláíró kulcs — hosszú, véletlenszerű érték legyen |
| `WTF_CSRF_SECRET_KEY` | CSRF védelem kulcsa — másik hosszú, véletlenszerű érték |
| `LOG_BACKUP_COUNT` | Megőrzött, rotált log fájlok napjainak száma |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Adatbázis hitelesítő adatok, mind a `web`, mind a `postgres` szolgáltatás használja |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Az adatbázis elérési címe (alapértelmezetten a `postgres` szolgáltatás, `5432` port) |
| `SQLALCHEMY_POOL_SIZE` | Adatbázis kapcsolat pool mérete |
| `THEMOVIEDB_HOSTNAME` | TMDB API host, alapesetben `api.themoviedb.org` |
| `THEMOVIEDB_TOKEN` | A TMDB API Read Access Token-ed |
| `PRIMARY_RELEASE_DATE_GTE` | Kezdő dátum egy tágabb filmlekéréshez (lásd lentebb) |
| `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` | Automatikusan létrehozott admin fiók adatai |
| `DEFAULT_USER_USERNAME` / `DEFAULT_USER_PASSWORD` | Automatikusan létrehozott sima felhasználói fiók adatai |
| `FLASK_APP`, `FLASK_ENV`, `USE_RELOADER`, `SERVER_NAME`, `FLASK_RUN_HOST`, `FLASK_RUN_PORT` | Flask futtatási beállítások — hagyd az alapértéken |

### Filmek letöltése tágabb dátumintervallumból

Alapesetben az alkalmazás csak a **mai napon** megjelent filmeket tölti le. Ha intervallumot szeretnél:

1. A `.env` fájlban állítsd be a `PRIMARY_RELEASE_DATE_GTE` értékét arra a kezdő dátumra (`ÉÉÉÉ-HH-NN`), amelytől kezdve letöltésre kerüljenek a filmek.
2. A `services/web/project/extensions/REST_THEMOVIEDB.py` fájl `get_movies()` függvényében tedd megjegyzésbe a `'primary_release_date.gte': today,` sort, majd vedd ki a megjegyzést a felette lévő `'primary_release_date.gte': app.config['PRIMARY_RELEASE_DATE_GTE'],` sorból.
3. Építsd újra / indítsd újra a `web` konténert. Az új filmek induláskor, illetve a Movies oldal **Update** gombjára kattintva töltődnek le.

### Az alkalmazás használata

* Az alapértelmezett fiókok automatikusan létrejönnek: `admin / admin` és `user / user`. Új fiókot is regisztrálhatsz a `/register` oldalon (a regisztrált felhasználók `user` szerepkört kapnak).
* **Minden bejelentkezett felhasználó számára elérhető:**
  * **Home** — bejelentkezés utáni főoldal.
  * **Movies** — az adatbázisban lévő filmek böngészése. Az **Update** gomb új filmeket tölt le a TMDB-től, az **Export** gomb `.xlsx` fájlba exportálja a listát. Egy film megtekintettnek jelölhető értékeléssel és dátummal.
  * **My Movies** — a megtekintettnek jelölt filmek, az értékeléssel és dátummal. Egy bejegyzés eltávolítható, újraértékelhető/újradátumozható, vagy exportálható.
  * **Movie Recommendation** — műfaj kiválasztása után véletlenszerű ajánlást ad az adatbázisban lévő, még nem megtekintett filmek közül.
  * **Log Out**
* **Csak admin számára:**
  * **User** — felhasználók és szerepkörök listázása, létrehozása, szerkesztése, törlése.
  * **System Log** — az alkalmazás log fájljainak megtekintése és letöltése.

### Biztonsági megjegyzések

* A `.env` fájl valódi titkokat tartalmaz, és git által figyelmen kívül van hagyva — soha ne commitold. Sablonként a `.env.example`-t használd, a valódi értékeket tartsd helyben (vagy a deployment titokkezelőjében).
* Ha a `SECRET_KEY`, `WTF_CSRF_SECRET_KEY`, `POSTGRES_PASSWORD` vagy `THEMOVIEDB_TOKEN` valaha commitolva vagy megosztva lett, cseréld le őket.
* Az alapértelmezett `admin`/`user` jelszavak, valamint a `services/nginx/certs/` mappában lévő TLS tanúsítvány/kulcs csak helyi fejlesztéshez valók — a `localhost`-on túli használat előtt cseréld le az alapértelmezett jelszavakat és a tanúsítványt.

### Köszönet

A login és a home oldalak az alábbi ingyenes sablonok testreszabásával és átalakításával készültek:

* Login oldal — [Login Form 14 (Colorlib)](https://colorlib.com/wp/template/login-form-14/)
* Home oldal — [Free Bootstrap Real Estate Template (Untree.co)](https://untree.co/free-templates/property-free-bootstrap-real-estate-template/)
