# FANTAELEGANZA MULTIMODULO V3 - FILE VERIFICATO
import html
import io
import json
import math
import os
import sqlite3
import re
import hashlib
import hmac
import secrets
import urllib.request
import unicodedata
import unicodedata
from html.parser import HTMLParser
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAZIONE APP
# ============================================================

st.set_page_config(
    page_title="FANTAELEGANZA 26/27",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
/* ============================================================
   NAVIGAZIONE COMPATTA
   Pulsanti più piccoli senza sacrificare la leggibilità
   ============================================================ */

div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    min-height: 34px !important;
    height: 34px !important;
    padding: 0.20rem 0.60rem !important;
    font-size: 0.88rem !important;
    line-height: 1.15 !important;
    border-radius: 7px !important;
}

/* Mobile: leggermente più alti per facilitare il tap */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
        min-height: 36px !important;
        height: 36px !important;
        padding: 0.22rem 0.45rem !important;
        font-size: 0.86rem !important;
        line-height: 1.15 !important;
    }
}

/* ==========================================================
   IQR V45 - BARRA ORIZZONTALE
   ========================================================== */

.iqr-gauge-card {
    width:100%;
    box-sizing:border-box;
    text-align:center;
}

.iqr-gauge-title {
    color:#ffffff;
    font-size:1rem;
    font-weight:900;
    margin-bottom:10px;
}

.iqr-scale-wrap {
    position:relative;
    width:82%;
    margin:0 auto;
    padding-bottom:20px;
}

.iqr-scale {
    display:grid;
    grid-template-columns:40fr 25fr 15fr 20fr;
    width:100%;
    height:24px;
    border-radius:2px;
    overflow:hidden;
}

.iqr-seg {
    height:100%;
}

.iqr-seg-black {
    background:#050505;
}

.iqr-seg-red {
    background:#ff1616;
}

.iqr-seg-blue {
    background:#0b6df5;
}

.iqr-seg-green {
    background:#16a34a;
}

.iqr-pointer {
    position:absolute;
    bottom:0;
    width:0;
    height:0;
    transform:translateX(-50%);
    border-left:11px solid transparent;
    border-right:11px solid transparent;
    border-bottom:15px solid #ffc21c;
}

.iqr-gauge-value {
    color:#ffc21c;
    font-size:1.05rem;
    font-weight:950;
    margin-top:-2px;
    margin-bottom:7px;
}

.iqr-gauge-description {
    display:inline-block;
    min-width:58%;
    color:#ffffff !important;
    font-size:1rem;
    font-weight:950;
    line-height:1;
    text-align:center;
    border:2px solid #050505;
    border-radius:7px;
    padding:8px 14px;
    box-sizing:border-box;
}

/* ==========================================================
   V67 - NAVIGAZIONE PORTATA IN ALTO IN TUTTE LE SEZIONI
   ========================================================== */

/* Nuove versioni Streamlit */
div[data-testid="stMainBlockContainer"] {
    padding-top: 0.20rem !important;
    margin-top: 0 !important;
}

/* Compatibilità con versioni precedenti */
section.main > div,
section[data-testid="stMain"] > div,
.main .block-container,
div[data-testid="stAppViewBlockContainer"] {
    padding-top: 0.20rem !important;
    margin-top: 0 !important;
}

/* Elimina eventuale spazio residuo prima della navbar */
div[data-testid="stMainBlockContainer"] > div:first-child,
.main .block-container > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Titolo NAVIGAZIONE aderente alla parte alta */
.nav-title {
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 4px !important;
}

/* Prima riga di colonne della navbar senza spazio superiore */
div[data-testid="stMainBlockContainer"] .nav-title + div[data-testid="stHorizontalBlock"],
.main .block-container .nav-title + div[data-testid="stHorizontalBlock"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Mantiene un piccolo margine sotto la navigazione */
div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"] {
    margin-top: 0 !important;
}


/* V68 - percentuale IQR accanto al titolo */
.iqr-gauge-title .iqr-title-percent {
    color: #ffc21c !important;
    font-size: inherit !important;
    font-weight: 950 !important;
    margin-left: 5px !important;
    white-space: nowrap !important;
}

/* ==========================================================
   V71 - CARD IQR FEDELE AL MOCKUP
   ========================================================== */

.iqr-card-v71 {
    width:100%;
    box-sizing:border-box;
    text-align:center;
    color:#ffffff;
}

.iqr-v71-top {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    margin-bottom:18px;
}

.iqr-v71-star {
    color:#ffc21c;
    font-size:30px;
    line-height:1;
    font-weight:900;
}

.iqr-v71-title {
    color:#ffffff;
    font-size:20px;
    line-height:1;
    font-weight:900;
}

.iqr-v71-percent {
    color:#ffc21c;
    font-size:20px;
    line-height:1;
    font-weight:950;
}

.iqr-v71-help {
    width:22px;
    height:22px;
    line-height:20px;
    text-align:center;
    border:1px solid #c7d7e8;
    border-radius:50%;
    color:#c7d7e8;
    font-size:13px;
    font-weight:800;
}

.iqr-v71-bar-wrap {
    position:relative;
    width:92%;
    margin:0 auto 14px auto;
    padding-top:18px;
}

.iqr-card-v71 .iqr-scale {
    display:flex !important;
    width:100% !important;
    height:34px !important;
    overflow:hidden !important;
    border-radius:0 !important;
    box-shadow:0 0 0 1px rgba(255,255,255,.12);
}

.iqr-card-v71 .iqr-seg {
    height:100% !important;
}

.iqr-v71-pointer {
    position:absolute;
    top:0;
    width:0;
    height:0;
    transform:translateX(-50%);
    border-left:13px solid transparent;
    border-right:13px solid transparent;
    border-top:18px solid #ffffff;
}

.iqr-v71-status {
    display:inline-block;
    min-width:42%;
    padding:8px 16px;
    margin:0 auto 18px auto;
    color:#ffffff !important;
    font-size:18px;
    line-height:1;
    font-weight:900;
    border-radius:8px;
    border:1px solid rgba(255,255,255,.18);
    box-sizing:border-box;
}

.iqr-v71-legend {
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    gap:10px;
    width:100%;
    margin-top:4px;
}

.iqr-v71-legend-item {
    display:flex;
    align-items:flex-start;
    justify-content:center;
    gap:8px;
    text-align:left;
    color:#ffffff;
    font-size:11px;
    line-height:1.2;
}

.iqr-v71-legend-item b {
    color:#ffffff;
    font-size:11px;
    font-weight:900;
}

.iqr-v71-legend-item span {
    color:#dbe8f5;
    font-size:10px;
}

.iqr-v71-swatch {
    display:block;
    width:18px;
    min-width:18px;
    height:18px;
    border-radius:4px;
    border:1px solid rgba(255,255,255,.24);
    margin-top:1px;
}

.sw-black { background:#050505; }
.sw-red   { background:#ff1616; }
.sw-blue  { background:#0b6df5; }
.sw-green { background:#16a34a; }

/* Sidebar compatta */
section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-top {
    margin-bottom:12px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-star {
    font-size:24px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-title,
section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-percent {
    font-size:16px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-help {
    width:20px;
    height:20px;
    line-height:18px;
    font-size:12px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-bar-wrap {
    width:88%;
    margin-bottom:10px;
    padding-top:15px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-scale {
    height:28px !important;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-pointer {
    border-left-width:10px;
    border-right-width:10px;
    border-top-width:14px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-status {
    min-width:48%;
    font-size:15px;
    padding:7px 12px;
    margin-bottom:12px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-legend {
    gap:6px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-legend-item {
    gap:5px;
    font-size:9px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-legend-item b {
    font-size:9px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-legend-item span {
    font-size:8px;
}

section[data-testid="stSidebar"] .iqr-card-v71 .iqr-v71-swatch {
    width:14px;
    min-width:14px;
    height:14px;
    border-radius:3px;
}

</style>
""", unsafe_allow_html=True)

SOGLIA_BASE = 500.00
MAX_GIOCATORI = 30
MIN_PORTIERI = 2
MAX_UNDO = 10

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fantacalcio.db"
URL_PROBABILI_FORMAZIONI = "https://www.fantacalcio.it/news/calcio-italia/06_08_2026/asta-fantacalcio-le-probabili-formazioni-della-serie-a-enilive-2026-27-495558?utm_source=chatgpt.com"
URL_INDISPONIBILI = "https://www.fantacalcio.it/indisponibili-serie-a"


MAX_SNAPSHOT = 30

CACHE_DIR = BASE_DIR / "cache_fantaeleganza"
CACHE_FORMAZIONI_PATH = CACHE_DIR / "formazioni_tipo.json"
CACHE_INFORTUNI_PATH = CACHE_DIR / "infortunati.json"


def salva_cache_json_locale(percorso, dati):
    """
    Salvataggio atomico best-effort della cache locale.
    Se il disco non è scrivibile, l'app continua comunque a funzionare.
    """
    try:
        CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        temporaneo = percorso.with_suffix(
            percorso.suffix + ".tmp"
        )

        temporaneo.write_text(
            json.dumps(
                dati,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temporaneo.replace(
            percorso
        )

        return True

    except Exception:
        return False


def leggi_cache_json_locale(percorso, default=None):
    try:
        if not percorso.exists():
            return default

        return json.loads(
            percorso.read_text(
                encoding="utf-8"
            )
        )

    except Exception:
        return default




def leggi_segreto(nome):
    """
    Legge prima dalle variabili d'ambiente e poi da st.secrets.
    In locale, se non esistono credenziali cloud, l'app continua
    a usare il normale database SQLite fantacalcio.db.
    """

    valore = os.environ.get(
        nome
    )

    if valore:
        return valore

    try:
        valore = st.secrets.get(
            nome
        )
    except Exception:
        valore = None

    return valore


TURSO_DATABASE_URL = leggi_segreto(
    "TURSO_DATABASE_URL"
)

TURSO_AUTH_TOKEN = leggi_segreto(
    "TURSO_AUTH_TOKEN"
)

USA_DATABASE_CLOUD = bool(
    TURSO_DATABASE_URL
    and TURSO_AUTH_TOKEN
)


# ============================================================
# MULTILEGA 0.5 - AUTH & LEAGUE PORTAL
# ============================================================

def _portal_raw_connection():

    if USA_DATABASE_CLOUD:

        try:
            import libsql
        except ImportError as errore:
            raise RuntimeError(
                "La modalità Cloud richiede il pacchetto libsql."
            ) from errore

        chiave = "_turso_connessione_raw"

        conn = st.session_state.get(
            chiave
        )

        if conn is None:

            conn = libsql.connect(
                database=TURSO_DATABASE_URL,
                auth_token=TURSO_AUTH_TOKEN
            )

            st.session_state[
                chiave
            ] = conn

        return conn

    return sqlite3.connect(
        DB_PATH
    )


def _portal_close(
    conn
):

    if USA_DATABASE_CLOUD:
        return

    try:
        conn.close()
    except Exception:
        pass


def password_hash_sicuro(
    password
):
    """
    PBKDF2-HMAC-SHA256 con salt casuale.
    Nel DB non viene mai salvata la password in chiaro.
    """

    if len(
        str(
            password
        )
    ) < 8:
        raise ValueError(
            "La password deve contenere almeno 8 caratteri."
        )

    salt = secrets.token_bytes(
        16
    )

    iterazioni = 260000

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        str(
            password
        ).encode(
            "utf-8"
        ),
        salt,
        iterazioni
    )

    return (
        "pbkdf2_sha256"
        + "$"
        + str(
            iterazioni
        )
        + "$"
        + salt.hex()
        + "$"
        + digest.hex()
    )


def verifica_password_sicura(
    password,
    hash_salvato
):

    try:

        algoritmo, iterazioni, salt_hex, digest_hex = (
            str(
                hash_salvato
            ).split(
                "$",
                3
            )
        )

        if algoritmo != "pbkdf2_sha256":
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            str(
                password
            ).encode(
                "utf-8"
            ),
            bytes.fromhex(
                salt_hex
            ),
            int(
                iterazioni
            )
        )

        return hmac.compare_digest(
            digest.hex(),
            digest_hex
        )

    except Exception:
        return False


def inizializza_portale_auth():
    """
    Schema minimo necessario PRIMA del login.
    Le CREATE TABLE sono eseguite una sola volta per sessione.
    """

    if st.session_state.get(
        "_ml05_portal_schema_ok",
        False
    ):
        return

    conn = _portal_raw_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password_hash TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS leagues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                stagione TEXT,
                modalita TEXT NOT NULL DEFAULT 'MANTRA',
                stato TEXT NOT NULL DEFAULT 'DRAFT',
                created_by_user_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                owner_user_id INTEGER,
                posizione INTEGER,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, nome)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS league_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                team_id INTEGER,
                is_admin INTEGER NOT NULL DEFAULT 0,
                is_auctioneer INTEGER NOT NULL DEFAULT 0,
                is_team_member INTEGER NOT NULL DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, user_id, team_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS league_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL UNIQUE,
                partecipanti INTEGER NOT NULL DEFAULT 10,
                max_giocatori INTEGER NOT NULL DEFAULT 30,
                min_portieri INTEGER NOT NULL DEFAULT 2,
                budget_iniziale REAL NOT NULL DEFAULT 500,
                incremento_minimo REAL NOT NULL DEFAULT 1,
                soglia_budget REAL NOT NULL DEFAULT 500,
                moltiplicatore_oltre_soglia REAL NOT NULL DEFAULT 3,
                tipo_asta TEXT NOT NULL DEFAULT 'CHIAMATA',
                fonte_listone TEXT NOT NULL DEFAULT 'Fantacalcio.it',
                regolamento_bloccato INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                user_id INTEGER,
                team_id INTEGER,
                azione TEXT NOT NULL,
                entita TEXT,
                entita_id TEXT,
                dettagli_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        st.session_state[
            "_ml05_portal_schema_ok"
        ] = True

    finally:
        _portal_close(
            conn
        )


def autentica_portale(
    username,
    password
):

    username = str(
        username
    ).strip()

    conn = _portal_raw_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                username,
                password_hash,
                is_active
            FROM users
            WHERE LOWER(username) = LOWER(?)
            LIMIT 1
        """, (
            username,
        ))

        riga = cur.fetchone()

        if not riga:
            return None

        user_id, username_db, password_hash, is_active = riga

        if int(
            is_active
            or 0
        ) != 1:
            return None

        if not password_hash:
            # Account legacy creati nelle release precedenti:
            # non possono essere autenticati senza una password.
            return {
                "legacy_password_missing":
                    True,

                "username":
                    str(
                        username_db
                    )
            }

        if not verifica_password_sicura(
            password,
            password_hash
        ):
            return None

        return {
            "user_id":
                int(
                    user_id
                ),

            "username":
                str(
                    username_db
                )
        }

    finally:
        _portal_close(
            conn
        )


def crea_lega_da_portale(
    dati_lega,
    squadre
):
    """
    Creazione atomica della lega completa dal portale pubblico.

    Ogni riga squadra crea:
    USER + TEAM + MEMBERSHIP + RUOLI.
    È obbligatorio almeno un ADMIN.
    """

    squadre_valide = []

    for posizione, squadra in enumerate(
        squadre,
        start=1
    ):

        username = str(
            squadra.get(
                "username",
                ""
            )
        ).strip()

        password = str(
            squadra.get(
                "password",
                ""
            )
        )

        if not username:
            raise ValueError(
                f"Manca il nome della Squadra {posizione}."
            )

        if len(
            password
        ) < 8:
            raise ValueError(
                f"La password di {username} deve avere almeno 8 caratteri."
            )

        squadre_valide.append({
            **squadra,
            "username":
                username,

            "password_hash":
                password_hash_sicuro(
                    password
                )
        })

    usernames_norm = [
        x[
            "username"
        ].casefold()
        for x in squadre_valide
    ]

    if len(
        usernames_norm
    ) != len(
        set(
            usernames_norm
        )
    ):
        raise ValueError(
            "I nomi squadra/username devono essere tutti diversi."
        )

    if not any(
        bool(
            x.get(
                "is_admin"
            )
        )
        for x in squadre_valide
    ):
        raise ValueError(
            "Devi indicare almeno una squadra come ADMIN."
        )

    conn = _portal_raw_connection()
    cur = conn.cursor()

    try:

        # Gli username sono globali: non possono essere duplicati
        # tra leghe diverse.
        for squadra in squadre_valide:

            cur.execute("""
                SELECT id
                FROM users
                WHERE LOWER(username) = LOWER(?)
                LIMIT 1
            """, (
                squadra[
                    "username"
                ],
            ))

            if cur.fetchone():
                raise ValueError(
                    f"Lo username '{squadra['username']}' è già utilizzato."
                )

        # Creatore tecnico = primo Admin definito nel wizard.
        primo_admin = next(
            x
            for x in squadre_valide
            if bool(
                x.get(
                    "is_admin"
                )
            )
        )

        # Crea prima l'utente Admin per poterlo registrare come creator.
        cur.execute("""
            INSERT INTO users (
                username,
                password_hash,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            primo_admin[
                "username"
            ],
            primo_admin[
                "password_hash"
            ]
        ))

        primo_admin_id = int(
            cur.lastrowid
        )

        cur.execute("""
            INSERT INTO leagues (
                nome,
                stagione,
                modalita,
                stato,
                created_by_user_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, 'DRAFT', ?,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            dati_lega[
                "nome"
            ],
            dati_lega[
                "stagione"
            ],
            dati_lega[
                "modalita"
            ],
            primo_admin_id
        ))

        league_id = int(
            cur.lastrowid
        )

        cur.execute("""
            INSERT INTO league_rules (
                league_id,
                partecipanti,
                max_giocatori,
                min_portieri,
                budget_iniziale,
                incremento_minimo,
                soglia_budget,
                moltiplicatore_oltre_soglia,
                tipo_asta,
                fonte_listone,
                regolamento_bloccato,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            league_id,
            int(
                dati_lega[
                    "partecipanti"
                ]
            ),
            int(
                dati_lega[
                    "max_giocatori"
                ]
            ),
            int(
                dati_lega[
                    "min_portieri"
                ]
            ),
            float(
                dati_lega[
                    "budget_iniziale"
                ]
            ),
            float(
                dati_lega[
                    "incremento_minimo"
                ]
            ),
            float(
                dati_lega[
                    "soglia_budget"
                ]
            ),
            float(
                dati_lega[
                    "moltiplicatore"
                ]
            ),
            dati_lega[
                "tipo_asta"
            ],
            dati_lega[
                "fonte_listone"
            ]
        ))

        for posizione, squadra in enumerate(
            squadre_valide,
            start=1
        ):

            if squadra[
                "username"
            ].casefold() == primo_admin[
                "username"
            ].casefold():

                user_id = (
                    primo_admin_id
                )

            else:

                cur.execute("""
                    INSERT INTO users (
                        username,
                        password_hash,
                        is_active,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, 1,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP)
                """, (
                    squadra[
                        "username"
                    ],
                    squadra[
                        "password_hash"
                    ]
                ))

                user_id = int(
                    cur.lastrowid
                )

            cur.execute("""
                INSERT INTO teams (
                    league_id,
                    nome,
                    owner_user_id,
                    posizione,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 1,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP)
            """, (
                league_id,
                squadra[
                    "username"
                ],
                user_id,
                posizione
            ))

            team_id = int(
                cur.lastrowid
            )

            cur.execute("""
                INSERT INTO league_members (
                    league_id,
                    user_id,
                    team_id,
                    is_admin,
                    is_auctioneer,
                    is_team_member,
                    is_active,
                    joined_at
                )
                VALUES (?, ?, ?, ?, ?, 1, 1, CURRENT_TIMESTAMP)
            """, (
                league_id,
                user_id,
                team_id,
                1
                if squadra.get(
                    "is_admin"
                )
                else 0,
                1
                if squadra.get(
                    "is_auctioneer"
                )
                else 0
            ))

        cur.execute("""
            INSERT INTO audit_log (
                league_id,
                user_id,
                team_id,
                azione,
                entita,
                entita_id,
                dettagli_json,
                created_at
            )
            VALUES (?, ?, NULL,
                    'LEAGUE_CREATED_FROM_PORTAL',
                    'LEAGUE', ?, ?, CURRENT_TIMESTAMP)
        """, (
            league_id,
            primo_admin_id,
            str(
                league_id
            ),
            json.dumps(
                {
                    "nome":
                        dati_lega[
                            "nome"
                        ],

                    "partecipanti":
                        int(
                            dati_lega[
                                "partecipanti"
                            ]
                        ),

                    "users":
                        [
                            {
                                "username":
                                    x[
                                        "username"
                                    ],

                                "admin":
                                    bool(
                                        x.get(
                                            "is_admin"
                                        )
                                    ),

                                "auctioneer":
                                    bool(
                                        x.get(
                                            "is_auctioneer"
                                        )
                                    )
                            }
                            for x in squadre_valide
                        ]
                },
                ensure_ascii=False
            )
        ))

        conn.commit()

        return league_id

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:
        _portal_close(
            conn
        )



# ============================================================
# MULTILEGA 0.6 - MIGRAZIONE ACCOUNT LEGACY
# ============================================================

LEGACY_AUTH_BOOTSTRAP = {
    "IBBINI IDIOTA": 'Ibbini26!Asta#91',
    "GOSTOBAR": 'Gostobar26!Mantra#47'
}


def migra_password_account_legacy():
    """
    Migrazione idempotente dei due account storici.

    - NON modifica user_id, league_members, team_id o dati legacy;
    - NON modifica rosa, budget, operazioni o configurazioni;
    - scrive la password soltanto se password_hash è NULL/vuoto;
    - nel DB viene salvato esclusivamente l'hash PBKDF2.
    """

    chiave_sessione = (
        "_ml06_legacy_auth_migration_ok"
    )

    if st.session_state.get(
        chiave_sessione,
        False
    ):
        return

    conn = _portal_raw_connection()
    cur = conn.cursor()

    try:

        for username, password_iniziale in (
            LEGACY_AUTH_BOOTSTRAP.items()
        ):

            cur.execute("""
                SELECT
                    id,
                    password_hash
                FROM users
                WHERE username = ?
                LIMIT 1
            """, (
                username,
            ))

            riga = cur.fetchone()

            if not riga:
                # L'account verrà eventualmente creato dalla normale
                # foundation legacy. Non inventiamo membership qui.
                continue

            user_id = int(
                riga[0]
            )

            hash_esistente = (
                riga[1]
            )

            if (
                hash_esistente is None
                or not str(
                    hash_esistente
                ).strip()
            ):

                nuovo_hash = (
                    password_hash_sicuro(
                        password_iniziale
                    )
                )

                cur.execute("""
                    UPDATE users
                    SET password_hash = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                      AND (
                            password_hash IS NULL
                            OR TRIM(password_hash) = ''
                      )
                """, (
                    nuovo_hash,
                    user_id
                ))

                cur.execute("""
                    INSERT INTO audit_log (
                        league_id,
                        user_id,
                        team_id,
                        azione,
                        entita,
                        entita_id,
                        dettagli_json,
                        created_at
                    )
                    SELECT
                        lm.league_id,
                        ?,
                        lm.team_id,
                        'LEGACY_AUTH_MIGRATED',
                        'USER',
                        ?,
                        ?,
                        CURRENT_TIMESTAMP
                    FROM league_members lm
                    WHERE lm.user_id = ?
                    LIMIT 1
                """, (
                    user_id,
                    str(
                        user_id
                    ),
                    json.dumps(
                        {
                            "username":
                                username,

                            "password_storage":
                                "PBKDF2-HMAC-SHA256",

                            "legacy_data_preserved":
                                True
                        },
                        ensure_ascii=False
                    ),
                    user_id
                ))

        conn.commit()

        st.session_state[
            chiave_sessione
        ] = True

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        _portal_close(
            conn
        )



# ============================================================
# MULTILEGA 0.7 - PROFILO UTENTE
# ============================================================


DEFAULT_FASCE_GOL = {
    "1": 66.0, "2": 72.0, "3": 78.0, "4": 84.0, "5": 90.0,
    "6": 97.0, "7": 103.0, "8": 109.0, "9": 115.0, "10": 121.0
}

TIPI_ASTA_FANTA_LIVE = [
    "A CHIAMATA",
    "ALFABETICO",
    "RANDOM",
    "DRAFT"
]

DEFAULT_RENDIMENTO_FASCE = [
    {"media_min": 6.00, "punti": 0.0},
    {"media_min": 6.25, "punti": 1.0},
    {"media_min": 6.50, "punti": 2.0},
    {"media_min": 6.75, "punti": 3.0},
    {"media_min": 7.00, "punti": 4.0},
]


def inizializza_schema_regolamento_avanzato():
    if st.session_state.get("_ml10_rules_schema_ok", False):
        return
    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        cur.execute("PRAGMA table_info(league_rules)")
        cols={str(r[1]) for r in cur.fetchall()}
        aggiunte=[
            ("fasce_gol_json","TEXT"),
            ("valore_gol_fatto","REAL NOT NULL DEFAULT 3.0"),
            ("valore_gol_subito","REAL NOT NULL DEFAULT -1.0"),
            ("valore_ammonizione","REAL NOT NULL DEFAULT -0.5"),
            ("valore_espulsione","REAL NOT NULL DEFAULT -1.0"),
            ("valore_rigore_segnato","REAL NOT NULL DEFAULT 3.0"),
            ("valore_rigore_subito","REAL NOT NULL DEFAULT -1.0"),
            ("numero_panchinari","INTEGER NOT NULL DEFAULT 10"),
            ("mod_d_factor","INTEGER NOT NULL DEFAULT 0"),
            ("mod_rendimento","INTEGER NOT NULL DEFAULT 0"),
            ("mod_fair_play","INTEGER NOT NULL DEFAULT 0"),
            ("mod_capitano","INTEGER NOT NULL DEFAULT 0"),
            ("mod_rendimento_tipo","TEXT NOT NULL DEFAULT 'BONUS'"),
            ("mod_rendimento_fasce_json","TEXT"),
        ]
        for nome,tipo in aggiunte:
            if nome not in cols:
                cur.execute(f"ALTER TABLE league_rules ADD COLUMN {nome} {tipo}")
        cur.execute("""UPDATE league_rules SET fasce_gol_json=?
                       WHERE fasce_gol_json IS NULL OR TRIM(fasce_gol_json)=''""",
                    (json.dumps(DEFAULT_FASCE_GOL),))
        cur.execute("""UPDATE league_rules SET mod_rendimento_fasce_json=?
                       WHERE mod_rendimento_fasce_json IS NULL
                          OR TRIM(mod_rendimento_fasce_json)=''""",
                    (json.dumps(DEFAULT_RENDIMENTO_FASCE),))
        # Normalizza il vecchio tipo ALTRO senza alterare le leghe valide.
        cur.execute("""UPDATE league_rules SET tipo_asta='A CHIAMATA'
                       WHERE tipo_asta IS NULL OR TRIM(tipo_asta)='' OR UPPER(tipo_asta)='ALTRO'""")
        conn.commit()
        st.session_state["_ml10_rules_schema_ok"]=True
    finally:
        _portal_close(conn)


def _fasce_gol_da_valori(valori):
    return {str(i+1): float(v) for i,v in enumerate(valori)}


def salva_regolamento_avanzato(league_id, valori):
    league_id=int(league_id); uid=int(st.session_state.get("auth_user_id"))
    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        cur.execute("""SELECT COUNT(*) FROM league_members
                       WHERE league_id=? AND user_id=? AND is_admin=1 AND is_active=1""",(league_id,uid))
        if int(cur.fetchone()[0] or 0)==0:
            raise PermissionError("Operazione riservata all'Admin della lega.")
        fasce=[float(x) for x in valori["fasce"]]
        if any(round(x*2)!=x*2 for x in fasce):
            raise ValueError("Le fasce gol devono usare incrementi di 0,5 punti.")
        if any(fasce[i] <= fasce[i-1] for i in range(1,len(fasce))):
            raise ValueError("Le fasce gol devono essere in ordine crescente.")
        if int(valori["moltiplicatore"]) < 1:
            raise ValueError("Il moltiplicatore deve essere un intero almeno pari a 1.")
        if valori["tipo_asta"] not in TIPI_ASTA_FANTA_LIVE:
            raise ValueError("Tipo asta non valido.")
        if not 6 <= int(valori["numero_panchinari"]) <= 10:
            raise ValueError("Il numero panchinari deve essere compreso tra 6 e 10.")
        cur.execute("""UPDATE league_rules SET
                       moltiplicatore_oltre_soglia=?, tipo_asta=?, fasce_gol_json=?,
                       valore_gol_fatto=?, valore_gol_subito=?, valore_ammonizione=?,
                       valore_espulsione=?, valore_rigore_segnato=?, valore_rigore_subito=?,
                       numero_panchinari=?, mod_d_factor=?, mod_rendimento=?,
                       mod_fair_play=?, mod_capitano=?,
                       mod_rendimento_tipo=?, mod_rendimento_fasce_json=?,
                       updated_at=CURRENT_TIMESTAMP
                       WHERE league_id=?""",
                    (int(valori["moltiplicatore"]),valori["tipo_asta"],
                     json.dumps(_fasce_gol_da_valori(fasce)),
                     float(valori["gol_fatto"]),float(valori["gol_subito"]),
                     float(valori["ammonizione"]),float(valori["espulsione"]),
                     float(valori["rigore_segnato"]),float(valori["rigore_subito"]),
                     int(valori["numero_panchinari"]),int(bool(valori["d_factor"])),
                     int(bool(valori["rendimento"])),int(bool(valori["fair_play"])),
                     int(bool(valori["capitano"])),
                     str(valori.get("rendimento_tipo","BONUS")),
                     json.dumps(valori.get("rendimento_fasce",DEFAULT_RENDIMENTO_FASCE)),
                     league_id))
        cur.execute("""INSERT INTO audit_log
                       (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
                       VALUES (?,?,?,'RULES_UPDATED','LEAGUE_RULES',?,?,CURRENT_TIMESTAMP)""",
                    (league_id,uid,st.session_state.get("ml_team_id"),str(league_id),
                     json.dumps(valori,ensure_ascii=False)))
        conn.commit()
        invalida_cache_admin_multilega()
    except Exception:
        try: conn.rollback()
        except Exception: pass
        raise
    finally:
        _portal_close(conn)


def carica_regolamento_avanzato(league_id):
    cache_key="_ml16_admin_rules_"+str(int(league_id))
    cached=st.session_state.get(cache_key)
    if isinstance(cached,dict):
        return dict(cached)

    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        cur.execute("""SELECT moltiplicatore_oltre_soglia,tipo_asta,fasce_gol_json,
                       valore_gol_fatto,valore_gol_subito,valore_ammonizione,valore_espulsione,
                       valore_rigore_segnato,valore_rigore_subito,numero_panchinari,
                       mod_d_factor,mod_rendimento,mod_fair_play,mod_capitano,
                       mod_rendimento_tipo,mod_rendimento_fasce_json
                       FROM league_rules WHERE league_id=? LIMIT 1""",(int(league_id),))
        r=cur.fetchone()
        if not r: return None
        try: fasce=json.loads(r[2] or "{}")
        except Exception: fasce=DEFAULT_FASCE_GOL
        risultato={"moltiplicatore":max(1,int(float(r[0] or 1))),"tipo_asta":str(r[1] or "A CHIAMATA"),
                "fasce":[float(fasce.get(str(i),DEFAULT_FASCE_GOL[str(i)])) for i in range(1,11)],
                "gol_fatto":float(r[3] if r[3] is not None else 3),"gol_subito":float(r[4] if r[4] is not None else -1),
                "ammonizione":float(r[5] if r[5] is not None else -.5),"espulsione":float(r[6] if r[6] is not None else -1),
                "rigore_segnato":float(r[7] if r[7] is not None else 3),"rigore_subito":float(r[8] if r[8] is not None else -1),
                "numero_panchinari":int(r[9] or 10),"d_factor":bool(r[10]),"rendimento":bool(r[11]),
                "fair_play":bool(r[12]),"capitano":bool(r[13]),
                "rendimento_tipo":str(r[14] or "BONUS"),
                "rendimento_fasce":(
                    json.loads(r[15]) if r[15] else DEFAULT_RENDIMENTO_FASCE
                )}
        st.session_state[cache_key]=dict(risultato)
        return risultato
    finally: _portal_close(conn)



def render_tabella_rendimento(prefisso, tipo_default="BONUS", fasce_default=None):
    fasce_default=fasce_default or DEFAULT_RENDIMENTO_FASCE
    st.markdown("##### 1 · BONUS / MALUS")
    tipo=st.radio(
        "Applicazione del modificatore",
        ["BONUS","MALUS"],
        index=0 if str(tipo_default).upper()=="BONUS" else 1,
        horizontal=True,
        key=prefisso+"_tipo",
        help="BONUS aggiunge punti alla propria squadra; MALUS sottrae punti all'avversario."
    )
    st.caption(
        "BONUS: i punti vengono aggiunti alla tua squadra.  ·  "
        "MALUS: i punti vengono sottratti alla squadra avversaria."
    )
    st.markdown("##### 2 · VALORE BONUS / MALUS")
    st.caption("Imposta la soglia di media voto e i punti associati. I punti vanno inseriti come valore positivo: sarà il sistema ad aggiungerli (BONUS) o sottrarli all'avversario (MALUS).")
    valori=[]
    for i,fascia in enumerate(fasce_default):
        c1,c2=st.columns(2)
        with c1:
            media=st.number_input(
                "Media voto da",
                min_value=0.0,max_value=10.0,
                value=float(fascia.get("media_min",6.0)),
                step=0.05,format="%.2f",
                key=f"{prefisso}_media_{i}"
            )
        with c2:
            punti=st.number_input(
                "Punti "+("da aggiungere" if tipo=="BONUS" else "da togliere"),
                min_value=0.0,max_value=20.0,
                value=abs(float(fascia.get("punti",0.0))),
                step=0.5,format="%.2f",
                key=f"{prefisso}_punti_{i}"
            )
        valori.append({"media_min":float(media),"punti":float(punti)})
    return tipo,valori


def render_help_modificatori():
    with st.expander("ℹ️ Come funzionano i modificatori"):
        st.markdown("""
**D-Factor** — premia le buone prestazioni del pacchetto difensivo tramite la media voto dei giocatori eleggibili. Nel Mantra considera normalmente cinque uomini difensivi; esiste anche la configurazione 5+1 con portiere.

**Fattore Rendimento** — premia o penalizza il rendimento complessivo della squadra, valorizzando anche i calciatori che ottengono buoni voti senza bonus. Richiede 11 giocatori a voto.

**Fattore Fair Play** — premia una squadra che conclude la partita senza cartellini. Richiede 11 giocatori a voto.

**Fattore Capitano** — consente di indicare capitano e vice e applicare un bonus/malus in funzione del voto del capitano.

Nota: secondo il regolamento Fantacalcio, **D-Factor e Fattore Rendimento sono alternativi** e non possono essere utilizzati contemporaneamente.
        """)

def inizializza_schema_profilo_utente():
    if st.session_state.get("_ml07_profile_schema_ok", False):
        return
    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(users)")
        colonne = {str(r[1]) for r in cur.fetchall()}
        for nome, tipo in [("display_name","TEXT"),("profile_image","TEXT")]:
            if nome not in colonne:
                cur.execute(f"ALTER TABLE users ADD COLUMN {nome} {tipo}")
        conn.commit()
        st.session_state["_ml07_profile_schema_ok"] = True
    finally:
        _portal_close(conn)


def carica_profilo_utente():
    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, username, email, display_name, profile_image
            FROM users WHERE id = ? LIMIT 1
        """,(int(st.session_state.get("auth_user_id")),))
        r=cur.fetchone()
        if not r: return None
        return {"id":int(r[0]),"username":str(r[1] or ""),
                "email":str(r[2] or ""),"display_name":str(r[3] or ""),
                "profile_image":str(r[4] or "")}
    finally:
        _portal_close(conn)


def salva_profilo_utente(display_name,email,immagine_caricata=None,rimuovi_immagine=False):
    user_id=int(st.session_state.get("auth_user_id"))
    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        immagine_db=None; aggiorna=False
        if rimuovi_immagine:
            immagine_db=""; aggiorna=True
        elif immagine_caricata is not None:
            import base64
            contenuto=immagine_caricata.getvalue()
            if len(contenuto)>2*1024*1024:
                raise ValueError("L'immagine profilo non può superare 2 MB.")
            mime=getattr(immagine_caricata,"type",None) or "image/png"
            if mime not in ("image/png","image/jpeg","image/webp"):
                raise ValueError("Formato immagine non supportato.")
            immagine_db="data:"+mime+";base64,"+base64.b64encode(contenuto).decode("ascii")
            aggiorna=True
        if aggiorna:
            cur.execute("""UPDATE users SET display_name=?,email=?,profile_image=?,
                           updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                        (str(display_name).strip(),str(email).strip(),immagine_db,user_id))
        else:
            cur.execute("""UPDATE users SET display_name=?,email=?,
                           updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                        (str(display_name).strip(),str(email).strip(),user_id))
        conn.commit()
    finally:
        _portal_close(conn)


def modifica_password_utente(password_attuale,nuova_password,conferma_password):
    user_id=int(st.session_state.get("auth_user_id"))
    if nuova_password!=conferma_password:
        raise ValueError("La nuova password e la conferma non coincidono.")
    if len(str(nuova_password))<8:
        raise ValueError("La nuova password deve contenere almeno 8 caratteri.")
    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM users WHERE id=? LIMIT 1",(user_id,))
        r=cur.fetchone()
        if not r or not verifica_password_sicura(password_attuale,r[0]):
            raise ValueError("La password attuale non è corretta.")
        cur.execute("""UPDATE users SET password_hash=?,updated_at=CURRENT_TIMESTAMP
                       WHERE id=?""",(password_hash_sicuro(nuova_password),user_id))
        cur.execute("""INSERT INTO audit_log
                       (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
                       VALUES (?,?,?,'PASSWORD_CHANGED','USER',?,?,CURRENT_TIMESTAMP)""",
                    (st.session_state.get("ml_league_id"),user_id,
                     st.session_state.get("ml_team_id"),str(user_id),
                     json.dumps({"self_service":True})))
        conn.commit()
    finally:
        _portal_close(conn)


def render_profilo_utente():
    profilo=carica_profilo_utente()
    if not profilo:
        st.error("Profilo utente non trovato."); return
    st.subheader("👤 Profilo")
    st.caption("Gestisci i dati del profilo, l'immagine e la password.")
    c1,c2=st.columns([1.1,3.9])
    with c1:
        if profilo["profile_image"]:
            st.image(profilo["profile_image"],width=150)
        else:
            st.markdown("""<div style="width:150px;height:150px;border-radius:50%;
            background:#071a2f;color:#f5b51b;display:flex;align-items:center;
            justify-content:center;font-size:58px;font-weight:900;">👤</div>""",
            unsafe_allow_html=True)
    with c2:
        st.markdown("**Username:** `"+html.escape(profilo["username"])+"`")
        st.caption("Lo username di accesso resta invariato.")
    st.markdown("#### Dati profilo")
    with st.form("ml07_profile_form"):
        nome=st.text_input("Nome visualizzato",value=profilo["display_name"])
        email=st.text_input("Email",value=profilo["email"])
        immagine=st.file_uploader("Immagine profilo",type=["png","jpg","jpeg","webp"],
                                 help="PNG, JPG o WEBP · massimo 2 MB")
        rimuovi=st.checkbox("Rimuovi l'immagine profilo attuale")
        salva=st.form_submit_button("SALVA PROFILO",type="primary",use_container_width=True)
    if salva:
        try:
            salva_profilo_utente(nome,email,immagine,rimuovi)
            st.success("Profilo aggiornato."); st.rerun()
        except Exception as e: st.error(str(e))
    st.markdown("---"); st.markdown("#### Modifica password")
    with st.form("ml07_password_form"):
        attuale=st.text_input("Password attuale",type="password")
        nuova=st.text_input("Nuova password",type="password")
        conferma=st.text_input("Conferma nuova password",type="password")
        cambia=st.form_submit_button("MODIFICA PASSWORD",use_container_width=True)
    if cambia:
        try:
            modifica_password_utente(attuale,nuova,conferma)
            st.success("Password modificata correttamente.")
        except Exception as e: st.error(str(e))


def render_portale_iniziale():

    st.markdown(
        """
        <style>
        .ml05-hero {
            max-width:1050px;
            margin:34px auto 22px auto;
            padding:26px 30px;
            background:linear-gradient(110deg,#061f3a,#0b3158);
            border:2px solid #f5b51b;
            border-radius:20px;
            text-align:center;
            box-shadow:0 10px 30px rgba(0,0,0,.14);
        }
        .ml05-hero-title {
            color:#fff;
            font-size:32px;
            font-weight:950;
        }
        .ml05-hero-title span {
            color:#f5b51b;
        }
        .ml05-hero-sub {
            color:#cbd5e1;
            margin-top:7px;
            font-size:14px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="ml05-hero">
            <div class="ml05-hero-title">
                FANTAELEGANZA <span>26/27</span>
            </div>
            <div class="ml05-hero-sub">
                Il tuo Fantacalcio Mantra, dalla creazione della lega all'asta
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_login, tab_crea = st.tabs(
        [
            "🔐 ACCEDI",
            "🏆 CREA LA TUA LEGA"
        ]
    )

    with tab_login:

        c1, c2, c3 = st.columns(
            [
                1,
                1.5,
                1
            ]
        )

        with c2:

            with st.form(
                "ml05_login_form"
            ):

                username = st.text_input(
                    "Username / Nome squadra"
                )

                password = st.text_input(
                    "Password",
                    type="password"
                )

                submit_login = (
                    st.form_submit_button(
                        "ACCEDI",
                        type="primary",
                        use_container_width=True
                    )
                )

            if submit_login:

                risultato = autentica_portale(
                    username,
                    password
                )

                if (
                    isinstance(
                        risultato,
                        dict
                    )
                    and risultato.get(
                        "legacy_password_missing"
                    )
                ):

                    st.warning(
                        "Questo è un account della versione precedente "
                        "e non possiede ancora una password. "
                        "La migrazione automatica delle credenziali legacy non risulta "
                        "ancora completata. Ricarica l’app o verifica il database."
                    )

                elif risultato is None:

                    st.error(
                        "Username o password non validi."
                    )

                else:

                    st.session_state[
                        "profilo_attivo"
                    ] = risultato[
                        "username"
                    ]

                    st.session_state[
                        "auth_user_id"
                    ] = risultato[
                        "user_id"
                    ]

                    st.session_state[
                        "auth_ok"
                    ] = True

                    st.rerun()

    with tab_crea:

        st.markdown(
            "### Crea una nuova lega"
        )

        st.caption(
            "Definisci il regolamento e crea le credenziali "
            "per tutte le squadre. Le password vengono salvate "
            "esclusivamente come hash sicuro."
        )

        with st.container():

            st.markdown(
                "#### 1 · Regolamento"
            )

            a, b, c = st.columns(
                3
            )

            with a:

                nome = st.text_input(
                    "Nome lega",
                    value="FANTAELEGANZA 26/27"
                )

                stagione = st.text_input(
                    "Stagione",
                    value="2026/27"
                )

                modalita = st.selectbox(
                    "Modalità",
                    [
                        "MANTRA",
                        "CLASSIC"
                    ]
                )

                partecipanti = st.number_input(
                    "Numero squadre",
                    min_value=2,
                    max_value=20,
                    value=10,
                    step=1
                )

            with b:

                max_giocatori = st.number_input(
                    "Rosa massima",
                    min_value=1,
                    max_value=60,
                    value=30,
                    step=1
                )

                min_portieri = st.number_input(
                    "Portieri minimi",
                    min_value=0,
                    max_value=10,
                    value=2,
                    step=1
                )

                budget = st.number_input(
                    "Budget iniziale",
                    min_value=1.0,
                    value=500.0,
                    step=10.0
                )

                incremento = st.number_input(
                    "Incremento minimo",
                    min_value=0.1,
                    value=1.0,
                    step=0.5
                )

            with c:

                soglia = st.number_input(
                    "Soglia budget",
                    min_value=0.0,
                    value=500.0,
                    step=10.0
                )

                moltiplicatore = st.number_input(
                    "Moltiplicatore oltre soglia",
                    min_value=1,
                    value=1,
                    step=1,
                    format="%d"
                )

                tipo_asta = st.selectbox(
                    "Tipo asta",
                    TIPI_ASTA_FANTA_LIVE
                )

                fonte = st.text_input(
                    "Fonte listone",
                    value="Fantacalcio.it"
                )

            st.markdown("#### Bonus / Malus")
            bm1,bm2,bm3=st.columns(3)
            with bm1:
                gol_fatto=st.number_input("GOL FATTO",value=3.0,step=0.5,format="%.2f")
                gol_subito=st.number_input("GOL SUBITO",value=-1.0,step=0.5,format="%.2f")
            with bm2:
                ammonizione=st.number_input("AMMONIZIONE",value=-0.5,step=0.5,format="%.2f")
                espulsione=st.number_input("ESPULSIONE",value=-1.0,step=0.5,format="%.2f")
            with bm3:
                rigore_segnato=st.number_input("RIGORE SEGNATO",value=3.0,step=0.5,format="%.2f")
                rigore_subito=st.number_input("RIGORE SUBITO",value=-1.0,step=0.5,format="%.2f")

            numero_panchinari=st.selectbox("Numero panchinari",list(range(6,11)),index=4)
            st.markdown("#### Modificatori")

            if "ml13_new_df" not in st.session_state:
                st.session_state["ml13_new_df"] = False
            if "ml13_new_rend" not in st.session_state:
                st.session_state["ml13_new_rend"] = False

            def _ml13_new_df_changed():
                if st.session_state.get("ml13_new_df"):
                    st.session_state["ml13_new_rend"] = False

            def _ml13_new_rend_changed():
                if st.session_state.get("ml13_new_rend"):
                    st.session_state["ml13_new_df"] = False

            mo1,mo2,mo3,mo4=st.columns(4)

            with mo1:
                d_factor=st.toggle(
                    "D-Factor",
                    key="ml13_new_df",
                    on_change=_ml13_new_df_changed
                )

            with mo2:
                rendimento=st.toggle(
                    "Fattore Rendimento",
                    key="ml13_new_rend",
                    on_change=_ml13_new_rend_changed
                )

            with mo3:
                fair_play=st.toggle(
                    "Fattore Fair Play",
                    value=False,
                    key="ml13_new_fp"
                )

            with mo4:
                capitano=st.toggle(
                    "Fattore Capitano",
                    value=False,
                    key="ml13_new_cap"
                )

            rendimento_tipo="BONUS"
            rendimento_fasce=DEFAULT_RENDIMENTO_FASCE

            render_help_modificatori()

            st.markdown(
                "#### 2 · Squadre, password e ruoli"
            )

            st.caption(
                "Il nome squadra sarà anche lo username per il primo accesso."
            )

            squadre = []

            for indice in range(
                int(
                    partecipanti
                )
            ):

                st.markdown(
                    f"**Squadra {indice + 1}**"
                )

                q1, q2, q3, q4 = st.columns(
                    [
                        2.4,
                        2.0,
                        1.1,
                        1.1
                    ]
                )

                with q1:

                    user_team = st.text_input(
                        "Nome squadra / Username",
                        key=f"ml05_team_user_{indice}"
                    )

                with q2:

                    pass_team = st.text_input(
                        "Password iniziale",
                        type="password",
                        key=f"ml05_team_pass_{indice}"
                    )

                with q3:

                    banditore = st.checkbox(
                        "Banditore",
                        key=f"ml05_team_band_{indice}"
                    )

                with q4:

                    admin = st.checkbox(
                        "Admin",
                        value=(
                            indice == 0
                        ),
                        key=f"ml05_team_admin_{indice}"
                    )

                squadre.append({
                    "username":
                        user_team,

                    "password":
                        pass_team,

                    "is_admin":
                        admin,

                    "is_auctioneer":
                        banditore
                })

            conferma = st.checkbox(
                "Confermo la creazione della lega e degli account"
            )

            crea = st.button(
                "CREA LA TUA LEGA",
                type="primary",
                use_container_width=True,
                disabled=not conferma,
                key="ml12_create_league"
            )

        if crea:

            try:

                if not str(
                    nome
                ).strip():
                    raise ValueError(
                        "Inserisci il nome della lega."
                    )

                if int(
                    min_portieri
                ) > int(
                    max_giocatori
                ):
                    raise ValueError(
                        "I portieri minimi non possono superare "
                        "la rosa massima."
                    )

                if d_factor and rendimento:
                    raise ValueError(
                        "D-Factor e Fattore Rendimento sono alternativi: attivane uno solo."
                    )

                league_id = crea_lega_da_portale(
                    {
                        "nome":
                            str(
                                nome
                            ).strip(),

                        "stagione":
                            str(
                                stagione
                            ).strip(),

                        "modalita":
                            modalita,

                        "partecipanti":
                            int(
                                partecipanti
                            ),

                        "max_giocatori":
                            int(
                                max_giocatori
                            ),

                        "min_portieri":
                            int(
                                min_portieri
                            ),

                        "budget_iniziale":
                            float(
                                budget
                            ),

                        "incremento_minimo":
                            float(
                                incremento
                            ),

                        "soglia_budget":
                            float(
                                soglia
                            ),

                        "moltiplicatore":
                            float(
                                moltiplicatore
                            ),

                        "tipo_asta":
                            tipo_asta,

                        "fonte_listone":
                            str(
                                fonte
                            ).strip()
                    },
                    squadre
                )

                salva_regolamento_avanzato(
                    league_id,
                    {
                        "moltiplicatore": int(moltiplicatore),
                        "tipo_asta": tipo_asta,
                        "fasce": list(DEFAULT_FASCE_GOL.values()),
                        "gol_fatto": gol_fatto,
                        "gol_subito": gol_subito,
                        "ammonizione": ammonizione,
                        "espulsione": espulsione,
                        "rigore_segnato": rigore_segnato,
                        "rigore_subito": rigore_subito,
                        "numero_panchinari": numero_panchinari,
                        "d_factor": d_factor,
                        "rendimento": rendimento,
                        "fair_play": fair_play,
                        "capitano": capitano,
                        "rendimento_tipo": rendimento_tipo,
                        "rendimento_fasce": rendimento_fasce
                    }
                )

                st.success(
                    f"Lega creata correttamente (ID {league_id}). "
                    "Ora ogni squadra può accedere dalla scheda ACCEDI "
                    "con il proprio nome squadra e la password assegnata."
                )

            except Exception as errore:

                st.error(
                    str(
                        errore
                    )
                )


inizializza_portale_auth()
inizializza_schema_profilo_utente()
inizializza_schema_regolamento_avanzato()

try:

    migra_password_account_legacy()

except Exception as errore_migrazione_auth:

    st.error(
        "Errore durante la migrazione delle credenziali legacy: "
        + str(
            errore_migrazione_auth
        )
    )

    st.stop()


if not st.session_state.get(
    "auth_ok",
    False
):

    render_portale_iniziale()

    st.stop()


PROFILO_ATTIVO = st.session_state[
    "profilo_attivo"
]

SUFFIX_PROFILO = (
    ""
    if PROFILO_ATTIVO == "IBBINI IDIOTA"
    else (
        "_gostobar"
        if PROFILO_ATTIVO == "GOSTOBAR"
        else (
            "_ml_pending_u"
            + str(
                int(
                    st.session_state.get(
                        "auth_user_id",
                        0
                    )
                    or 0
                )
            )
        )
    )
)

PROFILO_LEGACY_SUPPORTATO = (
    PROFILO_ATTIVO
    in [
        "IBBINI IDIOTA",
        "GOSTOBAR"
    ]
)


def nome_tabella_profilo(
    nome_base
):

    return (
        str(
            nome_base
        )
        + SUFFIX_PROFILO
    )


def imposta_workspace_team_multilega():
    """
    V96 - Isolamento operativo.

    Per gli account non legacy il vecchio motore dell'app continua a
    usare le stesse query, ma le tabelle fisiche sono dedicate in modo
    deterministico alla coppia league_id/team_id.

    In questo modo nessun nuovo utente può ricadere sulle tabelle base
    di IBBINI IDIOTA.
    """

    global SUFFIX_PROFILO

    if PROFILO_LEGACY_SUPPORTATO:
        return SUFFIX_PROFILO

    league_id = st.session_state.get(
        "ml_league_id"
    )

    team_id = st.session_state.get(
        "ml_team_id"
    )

    user_id = int(
        st.session_state.get(
            "auth_user_id",
            0
        )
        or 0
    )

    if league_id is None:
        raise RuntimeError(
            "Contesto lega non valido."
        )

    if team_id is None:
        # Un Admin senza squadra non deve mai usare dati di un'altra
        # squadra. Gli assegniamo quindi un workspace tecnico isolato.
        SUFFIX_PROFILO = (
            "_ml_l"
            + str(int(league_id))
            + "_admin_u"
            + str(user_id)
        )
    else:
        SUFFIX_PROFILO = (
            "_ml_l"
            + str(int(league_id))
            + "_t"
            + str(int(team_id))
        )

    st.session_state[
        "ml_workspace_suffix"
    ] = SUFFIX_PROFILO

    return SUFFIX_PROFILO


def inizializza_workspace_team_multilega():
    """
    V98 - inizializzazione veloce del workspace.

    Il workspace viene preparato una sola volta per sessione e coppia
    league_id/team_id. Questo evita round-trip Cloud ripetuti ad ogni
    semplice cambio di sezione.
    """

    if PROFILO_LEGACY_SUPPORTATO:
        return

    league_id = int(st.session_state.get("ml_league_id"))
    team_id = st.session_state.get("ml_team_id")

    workspace_id = (
        "L" + str(league_id)
        + "_T" + str(team_id if team_id is not None else "ADMIN")
    )
    guard_key = "_ml16_workspace_ready_" + workspace_id

    if st.session_state.get(guard_key, False):
        return

    cache_key = "ML98|" + str(PROFILO_ATTIVO) + "|" + workspace_id

    inizializza_database(cache_key)

    if team_id is None:
        st.session_state[guard_key] = True
        return

    raw_conn = _get_raw_connection()
    raw_cur = raw_conn.cursor()

    tab_giocatori = nome_tabella_profilo(
        "giocatori"
    )

    tab_config = nome_tabella_profilo(
        "configurazione_app"
    )

    try:

        raw_cur.execute(
            f"SELECT COUNT(*) FROM {tab_giocatori}"
        )

        quanti = int(
            raw_cur.fetchone()[0]
            or 0
        )

        # Il listone di base viene usato esclusivamente come catalogo.
        # Stato/prezzo non vengono mai copiati.
        if quanti == 0:

            raw_cur.execute(
                f"""
                INSERT INTO {tab_giocatori} (
                    id,
                    ruolo_classico,
                    ruolo_mantra,
                    nome,
                    squadra,
                    quotazione_attuale,
                    quotazione_iniziale,
                    differenza,
                    quotazione_attuale_mantra,
                    quotazione_iniziale_mantra,
                    differenza_mantra,
                    fvm,
                    fvm_mantra,
                    stato,
                    prezzo_acquisto,
                    ultimo_aggiornamento
                )
                SELECT
                    id,
                    ruolo_classico,
                    ruolo_mantra,
                    nome,
                    squadra,
                    quotazione_attuale,
                    quotazione_iniziale,
                    differenza,
                    quotazione_attuale_mantra,
                    quotazione_iniziale_mantra,
                    differenza_mantra,
                    fvm,
                    fvm_mantra,
                    'DISPONIBILE',
                    NULL,
                    CURRENT_TIMESTAMP
                FROM giocatori
                """
            )

        # Budget iniziale della specifica lega.
        raw_cur.execute(
            """
            SELECT COALESCE(
                budget_iniziale,
                500
            )
            FROM league_rules
            WHERE league_id = ?
            LIMIT 1
            """,
            (
                league_id,
            )
        )

        r_budget = raw_cur.fetchone()

        budget_regolamento = float(
            (
                r_budget[0]
                if r_budget
                else 500
            )
            or 500
        )

        raw_cur.execute(
            f"""
            INSERT INTO {tab_config} (
                chiave,
                valore
            )
            VALUES (
                'budget_asta',
                ?
            )
            ON CONFLICT(chiave)
            DO NOTHING
            """,
            (
                str(
                    budget_regolamento
                ),
            )
        )

        raw_conn.commit()
        st.session_state[guard_key] = True

    finally:

        if not USA_DATABASE_CLOUD:
            try:
                raw_conn.close()
            except Exception:
                pass


def verifica_isolamento_workspace():
    """
    Controllo fail-closed: per ogni utente non legacy il suffisso deve
    contenere il league_id e non può mai essere vuoto.
    """

    if PROFILO_LEGACY_SUPPORTATO:
        return True

    league_id = st.session_state.get(
        "ml_league_id"
    )

    if (
        not SUFFIX_PROFILO
        or SUFFIX_PROFILO == ""
        or league_id is None
        or (
            "_ml_l"
            + str(int(league_id))
        ) not in SUFFIX_PROFILO
    ):
        raise RuntimeError(
            "Blocco di sicurezza MULTILEGA: workspace non isolato."
        )

    return True


# ============================================================
# SESSION STATE
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "DASHBOARD"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


# ============================================================
# COLORI INTERFACCIA
# ============================================================

if st.session_state.dark_mode:
    BG_PAGE = "#0b1220"
    BG_CARD = "#121c2d"
    BG_CARD_2 = "#182437"
    TEXT = "#f8fafc"
    TEXT_SOFT = "#aab7ca"
    BORDER = "#29384d"
else:
    BG_PAGE = "#f4f7fb"
    BG_CARD = "#ffffff"
    BG_CARD_2 = "#f8fafc"
    TEXT = "#0f172a"
    TEXT_SOFT = "#64748b"
    BORDER = "#dbe2ea"

NAVY = "#071a2f"
NAVY_2 = "#0c2745"
GOLD = "#f5b51b"
GREEN = "#16a34a"
RED = "#ef4444"
BLUE = "#2563eb"


# ============================================================
# CSS GENERALE
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background: {BG_PAGE};
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1800px;
        padding-top: 0.15rem;
        padding-bottom: 1.2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    /* Rimuove completamente la fascia bianca superiore di Streamlit */
    header[data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        border: 0 !important;
    }}

    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    div[data-testid="stAppViewContainer"] {{
        padding-top: 0 !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT};
    }}

    p {{
        color: {TEXT};
    }}

    /* ======================================================
       HEADER
       ====================================================== */

    .fanta-header {{
        background:
            linear-gradient(
                100deg,
                {NAVY} 0%,
                {NAVY_2} 100%
            );

        border-radius: 0 0 14px 14px;

        padding: 14px 20px;

        margin:
            -0.7rem 0 8px 0;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.15);
    }}

    .fanta-brand {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}

    .fanta-logo {{
        width: 64px;
        height: 64px;
        min-width: 64px;

        display: flex;
        align-items: center;
        justify-content: center;

        border: 3px solid {GOLD};
        border-radius: 16px;

        background: #ffffff;
        overflow: hidden;
        box-sizing: border-box;
    }}

    .fanta-logo img {{
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
        object-position: center top;
    }}

    .fanta-brand-title {{
        color: white;
        font-weight: 900;
        font-size: 30px;
        line-height: 1;
        letter-spacing: 0.2px;
    }}

    .fanta-brand-title span {{
        color: {GOLD};
    }}

    .fanta-brand-subtitle {{
        color: #e2e8f0;
        font-size: 14px;
        margin-top: 5px;
    }}

    /* ======================================================
       METRICHE
       ====================================================== */

    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 11px;

        padding: 8px 11px;

        box-shadow:
            0 2px 6px rgba(15,23,42,0.04);

        min-height: 76px;
    }}

    div[data-testid="stMetricLabel"] {{
        font-size: 14px;
        color: {TEXT_SOFT};
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 22px;
        color: {TEXT};
    }}

    /* ======================================================
       PULSANTI
       ====================================================== */

    .stButton > button,
    .stDownloadButton > button {{
        border-radius: 9px;
        min-height: 90px;
        font-weight: 700;
        transition: all 0.15s ease;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        transform: translateY(-1px);
    }}

    /* ======================================================
       NAVBAR
       ====================================================== */

    .nav-title {{
        color: {TEXT_SOFT};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 6px;
        margin-bottom: 4px;
        letter-spacing: 0.7px;
    }}

    /* ======================================================
       TOOLBAR UNDO
       ====================================================== */

    .operation-info {{
        min-height: 90px;
        display: flex;
        align-items: center;
        padding-left: 8px;
        color: {TEXT_SOFT};
        font-size: 12px;
    }}

    /* ======================================================
       CAMPI MANTRA - GRIGLIA COMPATTA
       ====================================================== */

    .modules-intro {{
        color: {TEXT_SOFT};
        font-size: 11px;
        margin: 2px 0 7px 0;
    }}

    .module-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 6px;
        margin-bottom: 8px;
        box-shadow: 0 2px 6px rgba(15,23,42,0.04);
    }}

    .module-title {{
        color: {TEXT};
        text-align: center;
        font-size: 14px;
        font-weight: 900;
        line-height: 1.05;
        margin: 1px 0;
    }}

    .module-summary {{
        color: {TEXT_SOFT};
        text-align: center;
        font-size: 9px;
        margin: 0 0 4px 0;
    }}

    .pitch {{
        position: relative;
        width: 100%;
        min-height: 690px;
        box-sizing: border-box;
        border-radius: 7px;
        padding: 18px 14px;
        overflow: hidden;
        background: repeating-linear-gradient(
            90deg,
            #16833a 0px,
            #16833a 40px,
            #147836 40px,
            #147836 80px
        );
        border: 2px solid #f8fafc;
        box-shadow: inset 0 0 13px rgba(0,0,0,0.14);
    }}

    .pitch:before {{
        content: "";
        position: absolute;
        top: 5px;
        bottom: 5px;
        left: 5px;
        right: 5px;
        border: 1px solid rgba(255,255,255,0.74);
        border-radius: 3px;
        pointer-events: none;
    }}

    .pitch:after {{
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        border: 1px solid rgba(255,255,255,0.68);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        pointer-events: none;
    }}

    .pitch-half-line {{
        position: absolute;
        top: 50%;
        left: 5px;
        right: 5px;
        border-top: 1px solid rgba(255,255,255,0.68);
        z-index: 0;
    }}

    .pitch-line {{
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-evenly;
        align-items: flex-start;
        gap: 12px;
        margin: 30px 0;
    }}

    .player-slot {{
        flex: 1 1 0;
        min-width: 0;
        max-width: 240px;
        border-radius: 6px;
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(255,255,255,0.88);
        text-align: center;
        padding: 9px 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.13);
    }}

    .slot-code {{
        font-size: 14px;
        font-weight: 900;
        color: #0f172a;
        line-height: 1.05;
        margin-bottom: 6px;
        display: flex;
        justify-content: center;
        align-items: baseline;
        gap: 6px;
        flex-wrap: wrap;
    }}

    .slot-coverage {{
        font-size: 12px;
        font-weight: 900;
        line-height: 1;
    }}

    .slot-description {{
        display: none !important;
    }}

    .player-list {{
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 4px;
        width: 100%;
    }}

    .player-name {{
        display: block;
        width: 100%;
        box-sizing: border-box;
        background: #eef2f7;
        border-radius: 5px;
        padding: 5px 7px;
        margin: 0;
        font-size: 14px;
        line-height: 1.25;
        font-weight: 800;
        white-space: normal;
        overflow-wrap: anywhere;
    }}

    .slot-empty {{
        display: inline-block;
        color: #b91c1c;
        background: #fee2e2;
        border-radius: 8px;
        padding: 1px 4px;
        font-size: 7px;
        font-weight: 800;
        line-height: 1.1;
    }}

    /* ======================================================
       POSIZIONI LATERALI
       ====================================================== */

    .position-row {{
        display: grid;

        grid-template-columns:
            68px 1fr auto;

        align-items: center;

        gap: 6px;

        padding:
            4px 0;

        font-size: 11px;

        border-bottom:
            1px solid {BORDER};
    }}

    .position-code {{
        font-weight: 800;
        color: {TEXT};
    }}

    .position-desc {{
        color: {TEXT_SOFT};
    }}

    .position-ok {{
        background: #dcfce7;
        color: #15803d;

        padding:
            2px 7px;

        border-radius: 10px;

        font-weight: 700;
        font-size: 10px;
    }}

    .position-ko {{
        background: #fee2e2;
        color: #dc2626;

        padding:
            2px 7px;

        border-radius: 10px;

        font-weight: 700;
        font-size: 10px;
    }}

    /* ======================================================
       ROSA VUOTA
       ====================================================== */

    .empty-card {{
        background: {BG_CARD};

        border:
            1px solid {BORDER};

        border-radius: 12px;

        padding:
            28px;

        text-align: center;

        margin-top: 8px;

        box-shadow:
            0 2px 8px
            rgba(15,23,42,0.04);
    }}

    .empty-icon {{
        font-size: 40px;
        margin-bottom: 6px;
    }}

    .empty-title {{
        font-size: 19px;
        font-weight: 800;
        color: {TEXT};
    }}

    .empty-text {{
        color: {TEXT_SOFT};
        font-size: 13px;
        margin-top: 5px;
    }}

    /* ======================================================
       FOOTER
       ====================================================== */

    .fanta-footer {{
        margin:
            22px 0 0 0;

        padding:
            11px 18px;

        background: {NAVY};

        border-radius: 10px;

        color:
            #dce5ef;

        font-size: 11px;
    }}

    /* ======================================================
       MOBILE / RESPONSIVE
       ====================================================== */

    /* Vista ROSA desktop/mobile */
    .rosa-mobile-view {{
        display: none;
    }}

    .rosa-desktop-view {{
        display: block;
    }}

    div[class*="st-key-rosa_mobile_view"] {{
        display: none;
    }}

    div[class*="st-key-rosa_desktop_view"] {{
        display: block;
    }}

    @media
    (max-width: 850px) {{

        /* Pagina più compatta su smartphone */
        .block-container {{
            max-width: 100% !important;
            padding-top: 0.10rem !important;
            padding-bottom: 0.8rem !important;
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
        }}

        /* Header */
        .fanta-header {{
            padding: 9px 10px !important;
            border-radius: 0 0 10px 10px !important;
            margin-bottom: 5px !important;
        }}

        .fanta-brand {{
            gap: 8px !important;
        }}

        .fanta-logo {{
            width: 46px !important;
            height: 46px !important;
            min-width: 46px !important;
            border-width: 2px !important;
            border-radius: 10px !important;
        }}

        .fanta-brand-title {{
            font-size: 19px !important;
            line-height: 1.05 !important;
        }}

        .fanta-brand-subtitle {{
            font-size: 10px !important;
            margin-top: 2px !important;
        }}

        /* Navigazione e pulsanti */
        .stButton > button,
        .stDownloadButton > button {{
            min-height: 46px !important;
            height: auto !important;
            padding: 0.35rem 0.5rem !important;
            font-size: 12px !important;
            line-height: 1.15 !important;
            border-radius: 8px !important;
            white-space: normal !important;

            /* Mobile: contrasto sempre leggibile */
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }}

        /* Anche il testo interno dei pulsanti deve ereditare
           il colore corretto prima del click */
        .stButton > button *,
        .stDownloadButton > button * {{
            color: inherit !important;
        }}

        /* Pulsanti principali: NAV selezionata, ACQUISTA,
           conferme, modulo attivo, ecc. */
        button[data-testid="stBaseButton-primary"],
        .stButton > button[kind="primary"] {{
            background: #071a2f !important;
            color: #ffffff !important;
            border-color: #071a2f !important;
        }}

        button[data-testid="stBaseButton-primary"] *,
        .stButton > button[kind="primary"] * {{
            color: #ffffff !important;
        }}

        /* Pulsanti secondari / normali */
        button[data-testid="stBaseButton-secondary"] {{
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        button[data-testid="stBaseButton-secondary"] * {{
            color: #0f172a !important;
        }}

        .stButton > button:disabled,
        .stDownloadButton > button:disabled {{
            background: #e2e8f0 !important;
            color: #64748b !important;
            opacity: 1 !important;
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: 0.35rem !important;
        }}

        /* Tabs scorrevoli orizzontalmente */
        div[data-baseweb="tab-list"] {{
            overflow-x: auto !important;
            overflow-y: hidden !important;
            white-space: nowrap !important;
            flex-wrap: nowrap !important;
            scrollbar-width: thin;
        }}

        button[data-baseweb="tab"] {{
            min-width: max-content !important;
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
            font-size: 12px !important;
            color: #0f172a !important;
            background: #ffffff !important;
        }}

        button[data-baseweb="tab"] * {{
            color: inherit !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #071a2f !important;
            background: #f8fafc !important;
            font-weight: 800 !important;
        }}

        /* ASTA: il nome giocatore personalizzato deve avere
           spazio sufficiente prima del riquadro sottostante */
        .asta-player-mobile-fix {{
            min-height: 96px !important;
            padding-bottom: 18px !important;
            margin-bottom: 10px !important;
            position: relative !important;
            z-index: 2 !important;
            overflow: visible !important;
        }}

        /* Metriche */
        div[data-testid="stMetric"] {{
            min-height: 62px !important;
            padding: 6px 8px !important;
        }}

        div[data-testid="stMetricLabel"] {{
            font-size: 11px !important;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: 17px !important;
        }}

        /* Titoli e testi */
        h1 {{
            font-size: 1.45rem !important;
        }}

        h2 {{
            font-size: 1.25rem !important;
        }}

        h3 {{
            font-size: 1.08rem !important;
        }}

        h4 {{
            font-size: 0.98rem !important;
        }}

        p,
        label,
        .stMarkdown {{
            line-height: 1.25 !important;
        }}

        /* Input */
        div[data-baseweb="select"] > div,
        input,
        textarea {{
            font-size: 16px !important;
        }}

        /* Ricerca giocatore, prezzo, filtri:
           sfondo chiaro e testo scuro sempre visibile */
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        textarea {{
            min-height: 42px !important;
            background: #ffffff !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            border-color: #cbd5e1 !important;
            caret-color: #0f172a !important;
        }}

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stNumberInput"] input::placeholder,
        textarea::placeholder {{
            color: #64748b !important;
            -webkit-text-fill-color: #64748b !important;
            opacity: 1 !important;
        }}

        /* Selectbox: giocatore, filtri, ecc. */
        div[data-baseweb="select"] > div {{
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {{
            color: #0f172a !important;
        }}

        div[data-baseweb="select"] svg {{
            fill: #0f172a !important;
            color: #0f172a !important;
        }}

        /* Menu a tendina aperto */
        ul[role="listbox"],
        div[role="listbox"] {{
            background: #ffffff !important;
            color: #0f172a !important;
        }}

        li[role="option"],
        div[role="option"] {{
            background: #ffffff !important;
            color: #0f172a !important;
        }}

        li[role="option"]:hover,
        div[role="option"]:hover {{
            background: #f1f5f9 !important;
            color: #0f172a !important;
        }}

        /* ROSA: su mobile nascondiamo la griglia desktop e
           mostriamo la tabella compatta dedicata */
        .rosa-desktop-view {{
            display: none !important;
        }}

        div[class*="st-key-rosa_mobile_view"] {{
            display: block !important;
        }}

        div[class*="st-key-rosa_desktop_view"] {{
            display: none !important;
        }}

        .rosa-mobile-view {{
            display: block !important;
            width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }}

        .rosa-mobile-table {{
            width: 100% !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            font-size: 10px !important;
            background: #ffffff !important;
        }}

        .rosa-mobile-table th {{
            background: #071a2f !important;
            color: #ffffff !important;
            padding: 7px 3px !important;
            border: 1px solid #cbd5e1 !important;
            font-size: 9px !important;
            line-height: 1.1 !important;
        }}

        .rosa-mobile-table td {{
            color: #0f172a !important;
            padding: 7px 3px !important;
            border: 1px solid #e2e8f0 !important;
            vertical-align: middle !important;
            overflow-wrap: anywhere !important;
            line-height: 1.15 !important;
        }}

        .rosa-mobile-table th:nth-child(1),
        .rosa-mobile-table td:nth-child(1) {{ width: 52% !important; }}
        .rosa-mobile-table th:nth-child(2),
        .rosa-mobile-table td:nth-child(2) {{ width: 24% !important; text-align:center !important; }}
        .rosa-mobile-table th:nth-child(3),
        .rosa-mobile-table td:nth-child(3) {{ width: 24% !important; text-align:center !important; }}

        .rosa-mobile-annulla {{
            display: inline-block !important;
            min-width: 30px !important;
            padding: 5px 6px !important;
            border-radius: 6px !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
            font-weight: 800 !important;
            text-align: center !important;
        }}

        /* Tabelle/Dataframe: manteniamo tutti i dati,
           ma consentiamo lo scorrimento orizzontale */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            overflow-x: auto !important;
            max-width: 100% !important;
        }}

        div[data-testid="stDataFrame"] * {{
            font-size: 11px !important;
        }}

        /* Schede e box */
        .empty-card {{
            padding: 18px 10px !important;
        }}

        .operation-info {{
            min-height: 46px !important;
            font-size: 10px !important;
        }}

        /* Priorità acquisto ASTA */
        div[data-testid="stHorizontalBlock"] > div {{
            min-width: 0 !important;
        }}

        div[class*="st-key-priorita_click_"] {{
            position: relative !important;
        }}

        div[class*="st-key-priorita_click_"] .stButton {{
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 20 !important;
            margin: 0 !important;
        }}

        div[class*="st-key-priorita_click_"] .stButton > button {{
            width: 100% !important;
            height: 100% !important;
            min-height: 100% !important;
            opacity: 0 !important;
            cursor: pointer !important;
            border: 0 !important;
            padding: 0 !important;
        }}

        /* ==================================================
           CAMPO MANTRA MOBILE
           ================================================== */

        .module-card {{
            padding: 5px !important;
            margin-bottom: 6px !important;
        }}

        .module-title,
        .module-card-title {{
            font-size: 16px !important;
        }}

        .module-summary,
        .module-card-summary {{
            font-size: 9px !important;
        }}

        .pitch {{
            min-height: auto !important;
            height: auto !important;
            padding: 12px 5px !important;
            border-width: 2px !important;
        }}

        .pitch:after {{
            width: 54px !important;
            height: 54px !important;
        }}

        .pitch-line {{
            flex-wrap: wrap !important;
            gap: 6px !important;
            margin: 18px 0 !important;
            justify-content: center !important;
        }}

        .player-slot {{
            min-width: 112px !important;
            max-width: 155px !important;
            flex: 1 1 112px !important;
            padding: 6px 5px !important;
            border-radius: 6px !important;
        }}

        .slot-code {{
            font-size: 11px !important;
            gap: 4px !important;
            margin-bottom: 4px !important;
        }}

        .slot-coverage {{
            font-size: 10px !important;
        }}

        .player-list {{
            gap: 3px !important;
        }}

        .player-name {{
            font-size: 11px !important;
            line-height: 1.18 !important;
            padding: 4px 5px !important;
        }}

        .slot-empty {{
            font-size: 9px !important;
            padding: 2px 5px !important;
        }}

        /* Dialog più adatti allo smartphone */
        div[data-testid="stDialog"] > div {{
            width: calc(100vw - 1rem) !important;
            max-width: calc(100vw - 1rem) !important;
        }}

        /* Popup/dialog mobile: sfondo chiaro e testo sempre leggibile */
        div[data-testid="stDialog"],
        div[data-testid="stDialog"] > div,
        div[data-testid="stDialog"] section,
        div[role="dialog"],
        div[role="dialog"] > div {{
            background: #ffffff !important;
            color: #0f172a !important;
        }}

        div[data-testid="stDialog"] *,
        div[role="dialog"] * {{
            color: #0f172a !important;
        }}

        /* Titoli, testi, warning, info nei popup */
        div[data-testid="stDialog"] h1,
        div[data-testid="stDialog"] h2,
        div[data-testid="stDialog"] h3,
        div[data-testid="stDialog"] h4,
        div[data-testid="stDialog"] p,
        div[data-testid="stDialog"] label,
        div[role="dialog"] h1,
        div[role="dialog"] h2,
        div[role="dialog"] h3,
        div[role="dialog"] h4,
        div[role="dialog"] p,
        div[role="dialog"] label {{
            color: #0f172a !important;
        }}

        /* Checkbox nei popup */
        div[data-testid="stDialog"] input[type="checkbox"],
        div[role="dialog"] input[type="checkbox"] {{
            accent-color: #071a2f !important;
        }}

        /* Pulsanti popup normali */
        div[data-testid="stDialog"] .stButton > button,
        div[role="dialog"] .stButton > button {{
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }}

        div[data-testid="stDialog"] .stButton > button *,
        div[role="dialog"] .stButton > button * {{
            color: inherit !important;
        }}

        /* Pulsante principale/conferma del popup */
        div[data-testid="stDialog"] button[data-testid="stBaseButton-primary"],
        div[role="dialog"] button[data-testid="stBaseButton-primary"] {{
            background: #071a2f !important;
            color: #ffffff !important;
            border-color: #071a2f !important;
        }}

        div[data-testid="stDialog"] button[data-testid="stBaseButton-primary"] *,
        div[role="dialog"] button[data-testid="stBaseButton-primary"] * {{
            color: #ffffff !important;
        }}

        /* Warning/error/info interni al popup */
        div[data-testid="stDialog"] div[data-testid="stAlert"],
        div[role="dialog"] div[data-testid="stAlert"] {{
            background: #f8fafc !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        div[data-testid="stDialog"] div[data-testid="stAlert"] *,
        div[role="dialog"] div[data-testid="stAlert"] * {{
            color: #0f172a !important;
        }}

        /* Icona X chiusura dialog */
        div[data-testid="stDialog"] button[aria-label="Close"],
        div[role="dialog"] button[aria-label="Close"] {{
            color: #0f172a !important;
            background: #ffffff !important;
        }}

        /* File uploader */
        section[data-testid="stFileUploaderDropzone"] {{
            padding: 0.7rem !important;
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        section[data-testid="stFileUploaderDropzone"] *,
        div[data-testid="stFileUploader"] * {{
            color: #0f172a !important;
        }}

        section[data-testid="stFileUploaderDropzone"] button {{
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }}

        section[data-testid="stFileUploaderDropzone"] button * {{
            color: #0f172a !important;
        }}

        /* Footer */
        .fanta-footer {{
            padding: 8px 10px !important;
            font-size: 9px !important;
        }}
    }}

    @media
    (max-width: 480px) {{

        .fanta-brand-title {{
            font-size: 17px !important;
        }}

        .fanta-brand-subtitle {{
            font-size: 9px !important;
        }}

        .stButton > button,
        .stDownloadButton > button {{
            font-size: 11px !important;
            min-height: 44px !important;
        }}

        .player-slot {{
            min-width: 102px !important;
            max-width: 145px !important;
            flex-basis: 102px !important;
        }}

        .player-name {{
            font-size: 10.5px !important;
        }}

        .pitch-line {{
            margin: 15px 0 !important;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RUOLI
# ============================================================

ORDINE_RUOLI = {
    "POR": 1,
    "DC": 2,
    "B": 3,
    "DD": 4,
    "DS": 5,
    "E": 6,
    "M": 7,
    "C": 8,
    "W": 9,
    "T": 10,
    "A": 11,
    "PC": 12
}

ELENCO_RUOLI = [
    "Por",
    "Dc",
    "B",
    "Dd",
    "Ds",
    "E",
    "M",
    "C",
    "W",
    "T",
    "A",
    "Pc"
]


# ============================================================
# DESCRIZIONI POSIZIONI
# ============================================================

DESCRIZIONI_POSIZIONI = {
    "Por": "Portiere",
    "Dc": "Difensore centrale",
    "Dc/B": "Difensore centrale / braccetto",
    "Dd": "Terzino destro",
    "Ds": "Terzino sinistro",
    "E": "Esterno",
    "E/W": "Esterno / ala",
    "M": "Mediano",
    "M/C": "Mediano / centrocampista",
    "C": "Centrocampista",
    "C/T": "Centrocampista / trequartista",
    "W": "Ala",
    "W/T": "Ala / trequartista",
    "W/A": "Ala / attaccante",
    "T": "Trequartista",
    "T/A": "Trequartista / attaccante",
    "T/A/Pc": "Trequartista / attaccante",
    "A": "Attaccante",
    "A/Pc": "Attaccante / punta"
}


# ============================================================
# MODULI
# ============================================================

MODULI = {

    "3-4-3": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("E_SX", "E"),
            ("MC", "M/C"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("ATTACCO", [
            ("WA_SX", "W/A"),
            ("APC", "A/Pc"),
            ("WA_DX", "W/A")
        ])
    ],

    "3-4-1-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("E_SX", "E"),
            ("MC", "M/C"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("TREQUARTI", [
            ("T", "T")
        ]),
        ("ATTACCO", [
            ("APC_SX", "A/Pc"),
            ("APC_DX", "A/Pc")
        ])
    ],

    "3-4-2-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("M", "M"),
            ("MC", "M/C"),
            ("E_DX", "E")
        ]),
        ("TREQUARTI", [
            ("T_SX", "T"),
            ("TA_DX", "T/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "3-5-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("MC", "M/C"),
            ("M", "M"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("ATTACCO", [
            ("APC_SX", "A/Pc"),
            ("APC_DX", "A/Pc")
        ])
    ],

    "3-5-1-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("M_SX", "M"),
            ("C", "C"),
            ("M_DX", "M"),
            ("EW_DX", "E/W")
        ]),
        ("TREQUARTI", [
            ("TA", "T/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "4-3-3": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DS", "Ds"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DD", "Dd")
        ]),
        ("CENTROCAMPO", [
            ("MC", "M/C"),
            ("M", "M"),
            ("C", "C")
        ]),
        ("ATTACCO", [
            ("WA_SX", "W/A"),
            ("APC", "A/Pc"),
            ("WA_DX", "W/A")
        ])
    ],

    "4-3-1-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DS", "Ds"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DD", "Dd")
        ]),
        ("CENTROCAMPO", [
            ("MC", "M/C"),
            ("M", "M"),
            ("C", "C")
        ]),
        ("TREQUARTI", [
            ("T", "T")
        ]),
        ("ATTACCO", [
            ("TAPC", "T/A/Pc"),
            ("APC", "A/Pc")
        ])
    ],

    "4-4-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DS", "Ds"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DD", "Dd")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("MC", "M/C"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("ATTACCO", [
            ("APC_SX", "A/Pc"),
            ("APC_DX", "A/Pc")
        ])
    ],

    "4-1-4-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DS", "Ds"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DD", "Dd")
        ]),
        ("MEDIANA", [
            ("M", "M")
        ]),
        ("TREQUARTI", [
            ("EW_SX", "E/W"),
            ("CT", "C/T"),
            ("T", "T"),
            ("W_DX", "W")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "4-4-1-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DS", "Ds"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DD", "Dd")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("M", "M"),
            ("C", "C"),
            ("EW_DX", "E/W")
        ]),
        ("TREQUARTI", [
            ("TA", "T/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "4-2-3-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DS", "Ds"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DD", "Dd")
        ]),
        ("MEDIANA", [
            ("M", "M"),
            ("MC", "M/C")
        ]),
        ("TREQUARTI", [
            ("WT_SX", "W/T"),
            ("T", "T"),
            ("WA_DX", "W/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ]
}


# ============================================================
# FUNZIONI RUOLI
# ============================================================

def primo_ruolo(ruolo_mantra):

    if ruolo_mantra is None:
        return ""

    ruolo = str(
        ruolo_mantra
    ).strip()

    if ";" in ruolo:
        ruolo = ruolo.split(";")[0].strip()

    return ruolo


def priorita_ruolo(ruolo_mantra):

    return ORDINE_RUOLI.get(
        primo_ruolo(
            ruolo_mantra
        ).upper(),
        999
    )


def ruoli_giocatore(ruolo_mantra):

    if ruolo_mantra is None:
        return set()

    return {
        r.strip().upper()
        for r in str(
            ruolo_mantra
        ).split(";")
        if r.strip()
    }


def ruoli_posizione(posizione):

    return {
        r.strip().upper()
        for r in posizione.split("/")
        if r.strip()
    }


def compatibile(
    ruolo_giocatore,
    posizione
):

    return bool(
        ruoli_giocatore(
            ruolo_giocatore
        ).intersection(
            ruoli_posizione(
                posizione
            )
        )
    )


def e_portiere(ruolo_mantra):

    return (
        "POR"
        in ruoli_giocatore(
            ruolo_mantra
        )
    )


def giocatori_compatibili(
    df_rosa,
    ruolo_posizione
):

    # --------------------------------------------------------
    # SICUREZZA: ROSA ASSENTE
    # --------------------------------------------------------

    if df_rosa is None:

        return pd.DataFrame(
            columns=[
                "Id",
                "R",
                "RM",
                "Nome",
                "Squadra",
                "Qt.A",
                "Qt.I",
                "Diff.",
                "Qt.A M",
                "Qt.I M",
                "Diff.M",
                "FVM",
                "FVM M",
                "Stato",
                "Prezzo"
            ]
        )

    # --------------------------------------------------------
    # SICUREZZA: ROSA VUOTA
    # --------------------------------------------------------

    if df_rosa.empty:

        return df_rosa.copy()

    # --------------------------------------------------------
    # SICUREZZA: COLONNA RM MANCANTE
    # --------------------------------------------------------

    if "RM" not in df_rosa.columns:

        return df_rosa.iloc[
            0:0
        ].copy()

    # --------------------------------------------------------
    # FILTRO COMPATIBILITÀ
    # --------------------------------------------------------

    filtro = df_rosa["RM"].apply(
        lambda x:
        compatibile(
            x,
            ruolo_posizione
        )
    )

    compatibili = (
        df_rosa.loc[
            filtro
        ]
        .copy()
    )

    if compatibili.empty:

        return compatibili

    # --------------------------------------------------------
    # ORDINAMENTO SICURO
    # --------------------------------------------------------

    colonne_ordine = []
    ordine_ascendente = []

    if "FVM" in compatibili.columns:

        colonne_ordine.append(
            "FVM"
        )

        ordine_ascendente.append(
            False
        )

    if "Nome" in compatibili.columns:

        colonne_ordine.append(
            "Nome"
        )

        ordine_ascendente.append(
            True
        )

    if colonne_ordine:

        compatibili = (
            compatibili
            .sort_values(
                by=colonne_ordine,
                ascending=ordine_ascendente,
                na_position="last"
            )
        )

    return compatibili


# ============================================================
# PRIORITÀ ACQUISTO IN ASTA
# ============================================================

def valuta_priorita_acquisto(
    giocatore,
    df_rosa,
    df_listone
):
    """
    Valuta la priorità di acquisto usando le FASCE qualità
    (VERDE / BLU / ROSSO / NERO), non il valore FVM M puntuale.

    "Rimasti" =
        giocatori ancora DISPONIBILI compatibili con il ruolo
        e appartenenti alla stessa fascia del giocatore selezionato
        oppure a una fascia superiore.

    Esempi:
    - candidato VERDE -> conta solo VERDI
    - candidato BLU   -> conta VERDI + BLU
    - candidato ROSSO -> conta VERDI + BLU + ROSSI
    - candidato NERO  -> conta TUTTI

    Copertura rosa:
        numero di giocatori già presenti in rosa compatibili
        con il ruolo, indipendentemente dalla fascia.

    Priorità:
    - FONDAMENTALE:
        massimo 2 giocatori in rosa
        E meno di 7 pari/superiori per fascia rimasti.
    - NECESSARIO:
        meno di 4 giocatori in rosa
        E meno di 10 pari/superiori per fascia rimasti.
    - FACOLTATIVO:
        tutti gli altri casi.

    Per i multiruolo viene scelta la priorità più alta.
    """

    gerarchia_fasce = {
        "NERO": 1,
        "ROSSO": 2,
        "BLU": 3,
        "VERDE": 4
    }

    fascia_candidato = fascia_iqr_giocatore(
        giocatore.get(
            "RM",
            ""
        ),
        giocatore.get(
            "FVM M"
        )
    )

    livello_fascia_candidato = gerarchia_fasce.get(
        fascia_candidato,
        1
    )

    ruoli_candidato = sorted(
        ruoli_giocatore(
            giocatore.get(
                "RM",
                ""
            )
        )
    )

    if not ruoli_candidato:

        ruolo_principale = primo_ruolo(
            giocatore.get(
                "RM",
                ""
            )
        ).upper()

        ruoli_candidato = (
            [ruolo_principale]
            if ruolo_principale
            else []
        )

    risultati_ruolo = []

    for ruolo in ruoli_candidato:

        ruolo = str(
            ruolo
        ).strip().upper()

        if not ruolo:
            continue

        # ----------------------------------------------------
        # 1. COPERTURA DELLA ROSA NEL RUOLO
        # ----------------------------------------------------

        compatibili_rosa = giocatori_compatibili(
            df_rosa,
            ruolo
        )

        numero_in_rosa = (
            len(
                compatibili_rosa
            )
            if compatibili_rosa is not None
            else 0
        )

        # ----------------------------------------------------
        # 2. GIOCATORI PARI O SUPERIORI PER FASCIA RIMASTI
        # ----------------------------------------------------

        compatibili_listone = giocatori_compatibili(
            df_listone,
            ruolo
        )

        disponibili_equivalenti = 0

        if (
            compatibili_listone is not None
            and not compatibili_listone.empty
        ):

            disponibili = (
                compatibili_listone[
                    compatibili_listone[
                        "Stato"
                    ]
                    .astype(str)
                    .str.upper()
                    == "DISPONIBILE"
                ]
                .copy()
            )

            if not disponibili.empty:

                disponibili[
                    "_fascia_priorita"
                ] = disponibili.apply(
                    lambda r:
                    fascia_iqr_giocatore(
                        r.get(
                            "RM",
                            ""
                        ),
                        r.get(
                            "FVM M"
                        )
                    ),
                    axis=1
                )

                disponibili[
                    "_livello_fascia_priorita"
                ] = disponibili[
                    "_fascia_priorita"
                ].map(
                    gerarchia_fasce
                ).fillna(
                    1
                )

                disponibili_equivalenti = int(
                    (
                        disponibili[
                            "_livello_fascia_priorita"
                        ]
                        >= livello_fascia_candidato
                    )
                    .sum()
                )

        # ----------------------------------------------------
        # 3. CLASSIFICAZIONE
        # ----------------------------------------------------

        if (
            numero_in_rosa <= 2
            and disponibili_equivalenti < 7
        ):

            etichetta = "ACQUISTO FONDAMENTALE"
            livello = 3

        elif (
            numero_in_rosa < 4
            and disponibili_equivalenti < 10
        ):

            etichetta = "ACQUISTO NECESSARIO"
            livello = 2

        else:

            etichetta = "ACQUISTO FACOLTATIVO"
            livello = 1

        risultati_ruolo.append({
            "Etichetta": etichetta,
            "Livello": livello,
            "Ruolo": ruolo,
            "Copertura": int(
                numero_in_rosa
            ),
            "Disponibili": int(
                disponibili_equivalenti
            ),
            "Fascia candidato": fascia_candidato
        })

    if not risultati_ruolo:

        return {
            "Etichetta": "ACQUISTO FACOLTATIVO",
            "Livello": 1,
            "Ruolo": "",
            "Copertura": 0,
            "Disponibili": 0,
            "Fascia candidato": fascia_candidato
        }

    # Priorità più alta. A parità scegliamo il ruolo
    # con meno alternative rimaste e minore copertura.
    migliore = sorted(
        risultati_ruolo,
        key=lambda x: (
            -x["Livello"],
            x["Disponibili"],
            x["Copertura"],
            x["Ruolo"]
        )
    )[0]

    return migliore

def calcola_budget_massimo_consigliato(
    giocatore,
    priorita,
    budget_totale,
    budget_residuo,
    numero_giocatori_rosa
):
    """
    Budget massimo consigliato per il giocatore selezionato.

    Usa:
    1) FVM del giocatore;
    2) priorità di acquisto;
    3) budget residuo e slot ancora da completare.

    Il risultato è solo informativo e non blocca mai l'acquisto.
    """

    def numero(valore, default=0.0):
        try:
            if pd.isna(valore):
                return float(default)
            return float(valore)
        except (TypeError, ValueError):
            return float(default)

    fvm = max(
        0.0,
        numero(
            giocatore.get(
                "FVM",
                0
            )
        )
    )

    budget_totale = max(
        0.0,
        numero(
            budget_totale,
            SOGLIA_BASE
        )
    )

    budget_residuo = max(
        0.0,
        numero(
            budget_residuo,
            0
        )
    )

    # L'FVM Fantacalcio è riferito al budget standard 1000.
    # Lo riportiamo al budget scelto dall'utente.
    valore_base = (
        fvm
        * (
            budget_totale
            / 1000.0
        )
    )

    moltiplicatori_priorita = {
        "ACQUISTO FACOLTATIVO": 0.85,
        "ACQUISTO NECESSARIO": 1.10,
        "ACQUISTO FONDAMENTALE": 1.30
    }

    etichetta = str(
        priorita.get(
            "Etichetta",
            "ACQUISTO FACOLTATIVO"
        )
    ).upper()

    moltiplicatore = (
        moltiplicatori_priorita.get(
            etichetta,
            0.85
        )
    )

    valore_strategico = (
        valore_base
        * moltiplicatore
    )

    slot_liberi = max(
        0,
        MAX_GIOCATORI
        - int(
            numero_giocatori_rosa
        )
    )

    # Conserviamo almeno 1 credito per ciascun giocatore
    # che dovrà ancora essere acquistato DOPO il candidato.
    riserva_completamento = max(
        0,
        slot_liberi - 1
    )

    budget_realmente_disponibile = max(
        0.0,
        budget_residuo
        - riserva_completamento
    )

    # Correttore progressivo di disponibilità:
    # se il budget medio per slot è alto, possiamo essere più generosi;
    # se è basso, comprimiamo il consiglio.
    if slot_liberi > 0:

        budget_medio_slot = (
            budget_residuo
            / slot_liberi
        )

        budget_medio_teorico = (
            budget_totale
            / MAX_GIOCATORI
        )

        rapporto_budget = (
            budget_medio_slot
            / budget_medio_teorico
            if budget_medio_teorico > 0
            else 1.0
        )

        correttore_budget = min(
            1.15,
            max(
                0.70,
                rapporto_budget
            )
        )

    else:
        correttore_budget = 1.0

    valore_corretto = (
        valore_strategico
        * correttore_budget
    )

    massimo = min(
        valore_corretto,
        budget_realmente_disponibile
    )

    # Se esiste almeno un credito realmente spendibile,
    # il consiglio minimo è 1.
    if budget_realmente_disponibile >= 1:

        massimo = max(
            1.0,
            massimo
        )

    massimo = round(
        massimo
    )

    return {
        "Massimo": int(
            massimo
        ),
        "Valore base": round(
            valore_base,
            1
        ),
        "Moltiplicatore priorità": moltiplicatore,
        "Correttore budget": round(
            correttore_budget,
            2
        ),
        "Riserva completamento": int(
            riserva_completamento
        )
    }


def stile_priorita_acquisto(
    etichetta
):
    """
    Colori della casella Priorità acquisto.
    """

    if etichetta == "ACQUISTO FONDAMENTALE":
        return (
            "#fee2e2",
            "#991b1b",
            "#ef4444"
        )

    if etichetta == "ACQUISTO NECESSARIO":
        return (
            "#ffedd5",
            "#9a3412",
            "#f97316"
        )

    return (
        "#dcfce7",
        "#166534",
        "#22c55e"
    )


# ============================================================
# COLORAZIONE NOMI: FVM M + PRIMO RUOLO MANTRA
# ============================================================

SOGLIE_FVM_M = {
    "PC": (110, 70, 40),
    "A": (80, 40, 20),
    "W": (65, 45, 25),
    "T": (85, 45, 20),
    "C": (65, 40, 20),
    "M": (50, 30, 20),
    "E": (80, 25, 15),
    "DS": (25, 15, 10),
    "DD": (25, 15, 10),
    "B": (20, 15, 7),
    "DC": (40, 28, 20),
    "POR": (50, 30, 15)
}

COLORE_VERDE_FVM = "#16a34a"
COLORE_BLU_FVM = "#2563eb"
COLORE_ROSSO_FVM = "#dc2626"
COLORE_NERO_FVM = "#111827"


def colore_fvm_mantra(ruolo_mantra, valore_fvm_m):
    """Usa FVM M e il primo ruolo Mantra (es. Dc;Dd => Dc)."""

    ruolo = primo_ruolo(ruolo_mantra).upper()
    soglie = SOGLIE_FVM_M.get(ruolo)

    if soglie is None:
        return COLORE_NERO_FVM

    try:
        if valore_fvm_m is None or pd.isna(valore_fvm_m):
            return COLORE_NERO_FVM
        valore = float(valore_fvm_m)
    except Exception:
        return COLORE_NERO_FVM

    verde, blu, rosso = soglie

    if valore >= verde:
        return COLORE_VERDE_FVM
    if valore >= blu:
        return COLORE_BLU_FVM
    if valore >= rosso:
        return COLORE_ROSSO_FVM

    return COLORE_NERO_FVM



# ============================================================
# IQR - INDICE QUALITÀ ROSA
# ============================================================

def punteggio_qualita_giocatore(
    ruolo_mantra,
    valore_fvm_m
):
    """
    Punteggio individuale IQR basato sulle fasce colore FVM M.

    Fasce:
    - Verde = 100
    - Blu   = 70
    - Rosso = 40
    - Nero  = da 0 a 20 in funzione del FVM M

    FVM M = 1 vale sempre 0.
    Per doppi/tripli ruoli vale il primo ruolo Mantra.
    """

    ruolo = primo_ruolo(
        ruolo_mantra
    ).upper()

    soglie = SOGLIE_FVM_M.get(
        ruolo
    )

    if soglie is None:
        return 0.0

    try:
        valore = float(
            valore_fvm_m
        )
    except Exception:
        return 0.0

    if pd.isna(
        valore
    ):
        return 0.0

    verde, blu, rosso = soglie

    if valore <= 1:
        return 0.0

    if valore >= verde:
        return 100.0

    if valore >= blu:
        return 70.0

    if valore >= rosso:
        return 40.0

    # Fascia nera:
    # crescita progressiva da 0 (FVM M = 1)
    # a 20 immediatamente sotto la soglia rossa.
    if rosso <= 1:
        return 0.0

    punteggio_nero = (
        (valore - 1.0)
        / (float(rosso) - 1.0)
        * 20.0
    )

    return round(
        max(
            0.0,
            min(
                20.0,
                punteggio_nero
            )
        ),
        2
    )


def fascia_iqr_giocatore(
    ruolo_mantra,
    valore_fvm_m
):
    """
    Restituisce la fascia IQR del giocatore:
    VERDE / BLU / ROSSO / NERO.
    """

    ruolo = primo_ruolo(
        ruolo_mantra
    ).upper()

    soglie = SOGLIE_FVM_M.get(
        ruolo
    )

    if soglie is None:
        return "NERO"

    try:
        valore = float(
            valore_fvm_m
        )
    except Exception:
        return "NERO"

    if pd.isna(
        valore
    ):
        return "NERO"

    verde, blu, rosso = soglie

    if valore >= verde:
        return "VERDE"

    if valore >= blu:
        return "BLU"

    if valore >= rosso:
        return "ROSSO"

    return "NERO"


def descrizione_iqr(
    valore
):
    """
    Fasce qualitative IQR:
    0-40%      -> Rosa debole
    40.1-65%   -> Rosa buona
    65.1-85%   -> Rosa forte
    >85%       -> Rosa eccellente
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        valore = 0.0

    if valore > 85.0:
        return "Rosa eccellente"

    if valore > 65.0:
        return "Rosa forte"

    if valore > 40.0:
        return "Rosa buona"

    return "Rosa debole"



def calcola_iqr(
    df_rosa,
    df_listone=None,
    max_giocatori=MAX_GIOCATORI
):
    """
    IQR V2 - Indice Qualità Rosa.

    La formula ha tre passaggi:

    1) QUALITÀ BASE
       Ogni giocatore vale:
       Verde 100 / Blu 70 / Rosso 40 / Nero 0..20.
       Gli slot vuoti valgono 0.
       La qualità è calcolata su una rosa completa di 30 giocatori.

    2) DENSITÀ DI FASCE ALTE
       Premia una rosa che contiene un numero elevato di giocatori
       Verdi e Blu, con riferimenti realistici per una lega a 12:
       - 8 Verdi = obiettivo massimo della componente Verdi
       - 12 Verdi+Blu = obiettivo massimo della componente Top
       La densità pesa nella formula base per il 20%.

    3) BONUS OFFENSIVO
       I ruoli offensivi sono Pc, A, W, T e C.
       La presenza di molti Verdi/Blu offensivi chiude fino al 35%
       della distanza residua verso 100.
       Riferimenti:
       - 5 Verdi offensivi
       - 8 Verdi+Blu offensivi

    Proprietà:
    - 30 giocatori Verdi = 100%
    - 30 giocatori con FVM M = 1 = 0%
    - il 100% non viene raggiunto tramite il solo bonus offensivo:
      è necessario che la qualità base sia già 100.
    """

    if (
        df_rosa is None
        or df_rosa.empty
    ):
        return 0.0

    max_giocatori = max(
        1,
        int(
            max_giocatori
        )
    )

    totale_punti = 0.0

    numero_verdi = 0
    numero_blu = 0

    numero_verdi_offensivi = 0
    numero_blu_offensivi = 0

    RUOLI_OFFENSIVI_IQR = {
        "PC",
        "A",
        "W",
        "T",
        "C"
    }

    for _, giocatore in (
        df_rosa.iterrows()
    ):

        ruolo_mantra = giocatore.get(
            "RM",
            ""
        )

        valore_fvm_m = giocatore.get(
            "FVM M"
        )

        ruolo = primo_ruolo(
            ruolo_mantra
        ).upper()

        fascia = fascia_iqr_giocatore(
            ruolo_mantra,
            valore_fvm_m
        )

        totale_punti += (
            punteggio_qualita_giocatore(
                ruolo_mantra,
                valore_fvm_m
            )
        )

        if fascia == "VERDE":

            numero_verdi += 1

            if ruolo in RUOLI_OFFENSIVI_IQR:
                numero_verdi_offensivi += 1

        elif fascia == "BLU":

            numero_blu += 1

            if ruolo in RUOLI_OFFENSIVI_IQR:
                numero_blu_offensivi += 1

    # --------------------------------------------------------
    # 1) QUALITÀ MEDIA SU 30 SLOT
    # --------------------------------------------------------

    qualita_base = (
        totale_punti
        / (
            max_giocatori
            * 100.0
        )
        * 100.0
    )

    # --------------------------------------------------------
    # 2) DENSITÀ FASCE ALTE - LEGA A 12
    # --------------------------------------------------------

    quota_verdi = min(
        1.0,
        numero_verdi
        / 8.0
    )

    quota_top = min(
        1.0,
        (
            numero_verdi
            + numero_blu
        )
        / 12.0
    )

    densita_alta_qualita = (
        quota_verdi
        * 70.0
        + quota_top
        * 30.0
    )

    iqr_base = (
        qualita_base
        * 0.80
        + densita_alta_qualita
        * 0.20
    )

    # --------------------------------------------------------
    # 3) PREMIO OFFENSIVO
    # --------------------------------------------------------
    #
    # Il bonus non è una semplice somma di punti.
    # Chiude una parte della distanza tra l'IQR base e 100,
    # così:
    # - premia le rose con tanti top offensivi;
    # - non permette di superare 100;
    # - 30 Verdi restano esattamente 100.

    quota_verdi_offensivi = min(
        1.0,
        numero_verdi_offensivi
        / 5.0
    )

    quota_top_offensivi = min(
        1.0,
        (
            numero_verdi_offensivi
            + numero_blu_offensivi
        )
        / 8.0
    )

    forza_offensiva = (
        quota_verdi_offensivi
        * 70.0
        + quota_top_offensivi
        * 30.0
    )

    distanza_da_100 = max(
        0.0,
        100.0
        - iqr_base
    )

    bonus_offensivo = (
        distanza_da_100
        * 0.35
        * (
            forza_offensiva
            / 100.0
        )
    )

    iqr_finale = (
        iqr_base
        + bonus_offensivo
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                iqr_finale
            )
        ),
        1
    )




def colore_iqr(
    valore
):
    """
    Colore della fascia qualitativa IQR.
    Nero -> Rosso -> Blu -> Verde.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        valore = 0.0

    if valore > 85.0:
        return "#16a34a"

    if valore > 65.0:
        return "#0b6df5"

    if valore > 40.0:
        return "#ff1616"

    return "#050505"



def genera_html_gauge_iqr(
    valore
):
    """
    Card IQR pulita:
    titolo + percentuale, barra completa, indicatore e stato qualitativo.
    """

    try:
        valore = float(valore)
    except Exception:
        valore = 0.0

    valore = max(0.0, min(100.0, valore))

    descrizione = html.escape(
        descrizione_iqr(valore)
    )

    colore_descrizione = colore_iqr(valore)

    posizione = max(
        1.5,
        min(98.5, valore)
    )

    return (
        '<div class="iqr-gauge-card iqr-card-v73">'
        '<div class="iqr-v73-top">'
        '<div class="iqr-v73-star">★</div>'
        '<div class="iqr-v73-title">IQR</div>'
        f'<div class="iqr-v73-percent">{valore:.1f}%</div>'
        '</div>'
        '<div class="iqr-v73-bar-wrap">'
        '<div class="iqr-v73-bar"></div>'
        f'<div class="iqr-v73-pointer" style="left:{posizione:.1f}%"></div>'
        '</div>'
        f'<div class="iqr-v73-status" style="background:{colore_descrizione};">'
        f'{descrizione}'
        '</div>'
        '</div>'
    )



def dettaglio_iqr_per_ruolo(
    df_rosa
):
    """
    Costruisce la tabella di dettaglio IQR ruolo per ruolo.
    Il ruolo di riferimento è sempre il primo ruolo Mantra.
    """

    colonne = [
        "Ruolo",
        "Giocatori",
        "Verdi",
        "Blu",
        "Rossi",
        "Neri",
        "FVM M medio",
        "Qualità media",
        "Offensivo"
    ]

    if (
        df_rosa is None
        or df_rosa.empty
    ):
        return pd.DataFrame(
            columns=colonne
        )

    ruoli_offensivi = {
        "PC",
        "A",
        "W",
        "T",
        "C"
    }

    righe = []

    for ruolo in SOGLIE_FVM_M.keys():

        selezione = []

        for _, giocatore in (
            df_rosa.iterrows()
        ):

            ruolo_giocatore = primo_ruolo(
                giocatore.get(
                    "RM",
                    ""
                )
            ).upper()

            if ruolo_giocatore == ruolo:
                selezione.append(
                    giocatore
                )

        if not selezione:
            continue

        verdi = 0
        blu = 0
        rossi = 0
        neri = 0
        valori_fvm = []
        punti = []

        for giocatore in selezione:

            fascia = fascia_iqr_giocatore(
                giocatore.get(
                    "RM",
                    ""
                ),
                giocatore.get(
                    "FVM M"
                )
            )

            if fascia == "VERDE":
                verdi += 1
            elif fascia == "BLU":
                blu += 1
            elif fascia == "ROSSO":
                rossi += 1
            else:
                neri += 1

            try:
                valore_fvm = float(
                    giocatore.get(
                        "FVM M"
                    )
                )

                if not pd.isna(
                    valore_fvm
                ):
                    valori_fvm.append(
                        valore_fvm
                    )

            except Exception:
                pass

            punti.append(
                punteggio_qualita_giocatore(
                    giocatore.get(
                        "RM",
                        ""
                    ),
                    giocatore.get(
                        "FVM M"
                    )
                )
            )

        media_fvm = (
            sum(
                valori_fvm
            )
            / len(
                valori_fvm
            )
            if valori_fvm
            else 0.0
        )

        qualita_media = (
            sum(
                punti
            )
            / len(
                punti
            )
            if punti
            else 0.0
        )

        righe.append({
            "Ruolo": ruolo,
            "Giocatori": len(
                selezione
            ),
            "Verdi": verdi,
            "Blu": blu,
            "Rossi": rossi,
            "Neri": neri,
            "FVM M medio": round(
                media_fvm,
                1
            ),
            "Qualità media": f"{qualita_media:.1f}%",
            "Offensivo": (
                "Sì"
                if ruolo in ruoli_offensivi
                else "No"
            )
        })

    return pd.DataFrame(
        righe,
        columns=colonne
    )


# ============================================================
# FORMATTAZIONE
# ============================================================

def formatta_crediti(valore):

    try:

        if valore is None:
            return ""

        if pd.isna(valore):
            return ""

        return (
            f"{float(valore):.2f}"
            .replace(".", ",")
        )

    except Exception:

        return ""


# ============================================================
# BUDGET ASTA
# ============================================================


def leggi_config_generica(
    chiave,
    default=""
):
    """
    Lettura robusta della configurazione.

    In modalità Cloud/libsql una connessione persistente può diventare
    temporaneamente non valida e generare ValueError durante execute().
    Questo non deve bloccare la sezione ROSA: tentiamo una riconnessione
    una volta e, se fallisce ancora, restituiamo il default così le
    formazioni possono usare la cache locale/snapshot.
    """

    ultimo_errore = None

    for tentativo in range(2):

        conn = None

        try:

            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT valore "
                "FROM configurazione_app "
                "WHERE chiave = ?",
                (
                    chiave,
                )
            )

            riga = cur.fetchone()

            return (
                riga[0]
                if riga
                else default
            )

        except Exception as errore:

            ultimo_errore = errore

            # In Cloud forza una nuova connessione al secondo tentativo.
            if (
                USA_DATABASE_CLOUD
                and tentativo == 0
            ):

                vecchia = st.session_state.pop(
                    "_turso_connessione_raw",
                    None
                )

                if vecchia is not None:

                    try:
                        vecchia.close()
                    except Exception:
                        pass

                continue

            break

        finally:

            if conn is not None:

                try:
                    chiudi_connessione(
                        conn
                    )
                except Exception:
                    pass

    # La configurazione web non è critica per il rendering:
    # carica_probabili_web() passerà automaticamente alla cache locale
    # o allo snapshot incorporato.
    return default

def salva_config_generica(chiave,valore):
    conn=get_connection(); cur=conn.cursor()
    try:
        cur.execute("INSERT INTO configurazione_app (chiave,valore) VALUES (?,?) ON CONFLICT(chiave) DO UPDATE SET valore=excluded.valore",(chiave,valore))
        conn.commit()
    finally: chiudi_connessione(conn)

class PFParser(HTMLParser):
    def __init__(self): super().__init__(); self.x=[]
    def handle_data(self,d):
        d=re.sub(r"\s+"," ",str(d)).strip()
        if d: self.x.append(d)

def pf_mod(x): return bool(re.fullmatch(r"[1-5](?:-[1-5]){2,4}",str(x).strip()))
def pf_pct(x): return bool(re.fullmatch(r"\d{1,3}\s*%",str(x).strip()))
def pf_num(x):
    m=re.search(r"\d{1,3}",str(x)); return int(m.group()) if m else 0

def colore_status_titolarita(status):
    status = str(status or "").upper()
    if status == "TITOLARE":
        return "#16a34a"
    if status == "BALLOTTAGGIO":
        return "#2563eb"
    return "#dc2626"


class GoalTextParser(HTMLParser):
    """Extracts readable text from GOAL while ignoring script/style payloads."""
    def __init__(self):
        super().__init__()
        self.items = []
        self._ignore = 0

    def handle_starttag(self, tag, attrs):
        if str(tag).lower() in ("script", "style", "noscript"):
            self._ignore += 1

    def handle_endtag(self, tag):
        if str(tag).lower() in ("script", "style", "noscript") and self._ignore:
            self._ignore -= 1

    def handle_data(self, data):
        if self._ignore:
            return
        x = re.sub(r"\s+", " ", str(data)).strip()
        if x:
            self.items.append(x)


def _goal_nome_valido(nome):
    nome = re.sub(
        r"\s+",
        " ",
        str(nome or "")
    ).strip(" .:-")

    if not nome:
        return False

    testo = nome.lower()

    rumore = (
        "pubblicità",
        "pubblicita",
        "advertisement",
        "continua a leggere",
        "leggi anche",
        "scopri di più",
        "scopri di piu",
        "guarda il video",
        "newsletter",
        "cookie",
        "privacy",
        "scarica l'app",
        "seguici",
        "condividi",
        "copyright",
        "tutti i diritti"
    )

    if any(x in testo for x in rumore):
        return False

    if len(nome) > 38:
        return False

    return bool(
        re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿ]",
            nome
        )
    )


def _goal_split_names(text):
    risultato = []

    for pezzo in str(text).split(","):

        nome = re.sub(
            r"\s+",
            " ",
            pezzo
        ).strip(" .:-")

        nome = re.split(
            r"\b(?:Pubblicità|Pubblicita|Advertisement|Continua a leggere)\b",
            nome,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0].strip(" .:-")

        if (
            _goal_nome_valido(nome)
            and nome not in risultato
        ):
            risultato.append(nome)

    return risultato


def _goal_parse_formation_line(line):
    """
    GOAL encodes tactical lines with semicolons:
      goalkeeper ; defence ; midfield ; attack
    This is the key fix: we NEVER redistribute players by list order.
    """
    m = re.match(
        r"^\(([1-5](?:-[1-5]){2,4})\)\s*:\s*(.+?)\.?$",
        str(line).strip()
    )
    if not m:
        return None

    modulo = m.group(1)
    body = m.group(2)
    groups = [g.strip() for g in body.split(";") if g.strip()]
    names_by_group = [_goal_split_names(g) for g in groups]
    flat = [n for grp in names_by_group for n in grp]

    # A formation is accepted only if GOAL itself gives exactly eleven names.
    if len(flat) != 11:
        return None

    return {
        "modulo": modulo,
        "linee_fonte": names_by_group,
        "titolari": flat
    }


class FantacalcioFormazioniParser(HTMLParser):
    """
    Estrae i blocchi squadra dall'articolo Fantacalcio.it.

    La struttura editoriale utile è:
        H2 = squadra
        Allenatore:
        Modulo:
        Probabile formazione (da dx a sx):
        Ballottaggi:

    Non utilizziamo immagini/infografiche e non ricostruiamo dati
    non esplicitamente pubblicati dalla fonte.
    """

    def __init__(self):
        super().__init__()

        self.in_h2 = False
        self.h2_parts = []

        self.current_heading = None
        self.current_parts = []

        self.blocks = []


    def _flush(self):

        if (
            self.current_heading
            and self.current_parts
        ):

            testo = re.sub(
                r"\s+",
                " ",
                " ".join(
                    self.current_parts
                )
            ).strip()

            self.blocks.append(
                (
                    self.current_heading,
                    testo
                )
            )

        self.current_parts = []


    def handle_starttag(
        self,
        tag,
        attrs
    ):

        if str(
            tag
        ).lower() == "h2":

            self._flush()

            self.in_h2 = True
            self.h2_parts = []


    def handle_endtag(
        self,
        tag
    ):

        if str(
            tag
        ).lower() == "h2":

            self.in_h2 = False

            titolo = re.sub(
                r"\s+",
                " ",
                " ".join(
                    self.h2_parts
                )
            ).strip()

            self.current_heading = (
                titolo
                if titolo
                else None
            )

            self.h2_parts = []


    def handle_data(
        self,
        data
    ):

        testo = re.sub(
            r"\s+",
            " ",
            str(
                data
            )
        ).strip()

        if not testo:
            return

        if self.in_h2:

            self.h2_parts.append(
                testo
            )

        elif self.current_heading:

            self.current_parts.append(
                testo
            )


    def close(self):

        super().close()
        self._flush()


def _fc_pulisci_nome(nome):

    nome = re.sub(
        r"\s+",
        " ",
        str(
            nome
            or ""
        )
    ).strip(
        " .,:;-"
    )

    return nome


def _fc_split_giocatori(testo):

    risultato = []

    for pezzo in str(
        testo
    ).split(
        ","
    ):

        nome = _fc_pulisci_nome(
            pezzo
        )

        if (
            nome
            and _goal_nome_valido(
                nome
            )
        ):

            risultato.append(
                nome
            )

    return risultato


def _fc_parse_formazione(
    testo_formazione,
    modulo
):
    """
    Fantacalcio.it pubblica la formazione "da dx a sx" e separa
    le linee con punto e virgola.

    Manteniamo ESATTAMENTE quelle linee:
      P ; D ; C/... ; A

    e accettiamo soltanto una formazione con 11 nomi.
    """

    testo_formazione = re.sub(
        r"\s+",
        " ",
        str(
            testo_formazione
        )
    ).strip(
        " ."
    )

    linee = []

    for gruppo in testo_formazione.split(
        ";"
    ):

        nomi = _fc_split_giocatori(
            gruppo
        )

        if nomi:
            linee.append(
                nomi
            )

    titolari = [
        nome
        for linea in linee
        for nome in linea
    ]

    if len(
        titolari
    ) != 11:

        return None

    # Coerenza minima col modulo:
    # il modulo deve sempre rappresentare 10 giocatori di movimento.
    try:

        componenti = [
            int(
                x
            )
            for x in str(
                modulo
            ).split(
                "-"
            )
        ]

    except Exception:

        componenti = []

    if (
        not componenti
        or sum(
            componenti
        ) != 10
    ):

        return None

    return {
        "linee_fonte":
            linee,

        "titolari":
            titolari
    }


def _fc_parse_ballottaggi(testo):
    """
    Legge i ballottaggi espliciti pubblicati da Fantacalcio.it.

    La fonte usa sia ";" sia "," per separare le coppie:
        Zappacosta/Bellanova; Hien/Kolasinac
        Stones/Bisseck, Diouf/Luis Henrique

    Le note editoriali tra parentesi vengono eliminate.
    """

    testo = re.sub(
        r"\([^)]*\)",
        "",
        str(
            testo
            or ""
        )
    )

    coppie = []

    # Fantacalcio.it usa indifferentemente virgole e punti e virgola.
    for blocco in re.split(
        r"[;,]",
        testo
    ):

        blocco = re.sub(
            r"\s+",
            " ",
            blocco
        ).strip(
            " .,:;"
        )

        if "/" not in blocco:
            continue

        parti = [
            _fc_pulisci_nome(
                x
            )
            for x in blocco.split(
                "/",
                1
            )
        ]

        if (
            len(
                parti
            ) == 2
            and all(
                parti
            )
            and all(
                _goal_nome_valido(
                    x
                )
                for x in parti
            )
        ):

            coppie.append({
                "a": parti[0],
                "b": parti[1]
            })

    return coppie

def _fc_testo_da_jsonld(raw_html):
    """
    Cerca il contenuto dell'articolo nei blocchi JSON-LD.
    È spesso la rappresentazione più stabile perché non dipende
    dalla struttura grafica/DOM della pagina.
    """

    candidati = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw_html,
        flags=re.IGNORECASE | re.DOTALL
    )

    testi = []

    for blocco in candidati:

        blocco = blocco.strip()

        if not blocco:
            continue

        try:
            dati = json.loads(
                blocco
            )
        except Exception:
            continue

        oggetti = (
            dati
            if isinstance(
                dati,
                list
            )
            else [
                dati
            ]
        )

        for oggetto in oggetti:

            if not isinstance(
                oggetto,
                dict
            ):
                continue

            # Gestisce anche @graph.
            grafi = oggetto.get(
                "@graph",
                []
            )

            if isinstance(
                grafi,
                list
            ):
                oggetti.extend(
                    [
                        g
                        for g in grafi
                        if isinstance(
                            g,
                            dict
                        )
                    ]
                )

            corpo = oggetto.get(
                "articleBody"
            )

            if corpo:

                testo = re.sub(
                    r"\s+",
                    " ",
                    str(
                        corpo
                    )
                ).strip()

                if (
                    "Probabile formazione"
                    in testo
                    and "Ballottaggi"
                    in testo
                ):

                    testi.append(
                        testo
                    )

    if not testi:
        return ""

    return max(
        testi,
        key=len
    )


def _fc_testo_visibile(raw_html):
    """
    Fallback: estrae il testo visibile ignorando script/style.
    """

    parser = GoalTextParser()
    parser.feed(
        raw_html
    )

    parti = []

    for elemento in parser.items:

        testo = re.sub(
            r"\s+",
            " ",
            str(
                elemento
            )
        ).strip()

        if testo:
            parti.append(
                testo
            )

    return re.sub(
        r"\s+",
        " ",
        " ".join(
            parti
        )
    ).strip()


def _fc_normalizza_testo_articolo(testo):

    testo = (
        str(
            testo
            or ""
        )
        .replace(
            "\xa0",
            " "
        )
        .replace(
            "’",
            "'"
        )
        .replace(
            "–",
            "-"
        )
        .replace(
            "—",
            "-"
        )
    )

    return re.sub(
        r"\s+",
        " ",
        testo
    ).strip()


def _fc_squadre_attese():
    """
    Usa i nomi squadra del listone già caricato.
    È molto più robusto che provare a capire i titoli dall'HTML.

    La fonte dei dati sportivi resta esclusivamente Fantacalcio.it:
    il listone serve solo per sapere quali nomi squadra cercare.
    """

    squadre = []

    if (
        "df_completo"
        in globals()
        and df_completo is not None
        and not df_completo.empty
        and "Squadra"
        in df_completo.columns
    ):

        for valore in (
            df_completo[
                "Squadra"
            ]
            .dropna()
            .astype(
                str
            )
            .tolist()
        ):

            nome = re.sub(
                r"\s+",
                " ",
                valore
            ).strip()

            if (
                nome
                and nome not in squadre
            ):

                squadre.append(
                    nome
                )

    return squadre


def _fc_estrai_blocco_squadra(
    testo,
    nome_squadra
):
    """
    Cerca il blocco di una squadra usando il nome del club come ancora,
    seguito dalle etichette Allenatore / Modulo / Probabile formazione.
    """

    nome_esc = re.escape(
        nome_squadra
    )

    pattern = re.compile(
        rf"(?<!\w){nome_esc}(?!\w)"
        r"\s+Allenatore:\s*"
        r"(?P<allenatore>.+?)"
        r"\s+Modulo:\s*"
        r"(?P<modulo>[1-5](?:-[1-5]){2,4})"
        r"(?:\s*\([^)]*\))?"
        r"\s+Probabile formazione"
        r"(?:\s*\(da dx a sx\))?\s*:\s*"
        r"(?P<formazione>.+?)"
        r"\s+Ballottaggi:\s*"
        r"(?P<ballottaggi>.+?)"
        r"(?=\s+Rigoristi:|\s+Calci da fermo:|\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ' .-]{2,25}\s+Allenatore:|$)",
        flags=re.IGNORECASE
    )

    return pattern.search(
        testo
    )


def _fc_html_in_testo_puro(raw_html):
    """
    Converte l'HTML di Fantacalcio.it in testo continuo senza
    dipendere dalla struttura DOM o dai tag H2.

    Mantiene punteggiatura e separatori utili alla formazione.
    """

    testo = str(
        raw_html
        or ""
    )

    # Elimina contenuti che possono inquinare il parser.
    testo = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        testo,
        flags=re.IGNORECASE | re.DOTALL
    )

    testo = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        testo,
        flags=re.IGNORECASE | re.DOTALL
    )

    testo = re.sub(
        r"<noscript\b[^>]*>.*?</noscript>",
        " ",
        testo,
        flags=re.IGNORECASE | re.DOTALL
    )

    # I tag diventano semplicemente spazi.
    testo = re.sub(
        r"<[^>]+>",
        " ",
        testo
    )

    # Decodifica &nbsp;, &agrave;, apostrofi HTML, ecc.
    testo = html.unescape(
        testo
    )

    testo = (
        testo
        .replace(
            "\xa0",
            " "
        )
        .replace(
            "’",
            "'"
        )
        .replace(
            "–",
            "-"
        )
        .replace(
            "—",
            "-"
        )
    )

    return re.sub(
        r"\s+",
        " ",
        testo
    ).strip()



# ============================================================
# SNAPSHOT DI SICUREZZA - FONTE UNICA FANTACALCIO.IT
# Dati derivati ESCLUSIVAMENTE dalla pagina URL_PROBABILI_FORMAZIONI.
# Serve perché Streamlit Cloud può ricevere dalla pagina HTML una
# risposta anti-bot/shell priva del corpo dell'articolo.
# ============================================================

FANTACALCIO_SNAPSHOT_V15 = [
  {
    "squadra": "Atalanta",
    "allenatore": "Maurizio Sarri",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "Carnesecchi"
      ],
      [
        "Bellanova",
        "Kristensen",
        "Scalvini",
        "Bernasconi"
      ],
      [
        "Kessie",
        "Gaetano",
        "Ederson"
      ],
      [
        "De Ketelaere",
        "Scamacca",
        "Rowe"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Bellanova",
        "b": "Zappacosta"
      },
      {
        "a": "Kristensen",
        "b": "Hien"
      },
      {
        "a": "Kessie",
        "b": "Samardzic"
      },
      {
        "a": "Scamacca",
        "b": "Krstovic"
      },
      {
        "a": "Rowe",
        "b": "Raspadori"
      }
    ],
    "formazione": [
      {
        "nome": "Carnesecchi"
      },
      {
        "nome": "Bellanova"
      },
      {
        "nome": "Kristensen"
      },
      {
        "nome": "Scalvini"
      },
      {
        "nome": "Bernasconi"
      },
      {
        "nome": "Kessie"
      },
      {
        "nome": "Gaetano"
      },
      {
        "nome": "Ederson"
      },
      {
        "nome": "De Ketelaere"
      },
      {
        "nome": "Scamacca"
      },
      {
        "nome": "Rowe"
      }
    ]
  },
  {
    "squadra": "Bologna",
    "allenatore": "Domenico Tedesco",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "Skorupski"
      ],
      [
        "Zortea",
        "Heggem",
        "Theate",
        "Miranda"
      ],
      [
        "Odgaard",
        "Ferguson",
        "Pobega"
      ],
      [
        "Orsolini",
        "Dovbyk",
        "Cambiaghi"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Pobega",
        "b": "Moro"
      },
      {
        "a": "Odgaard",
        "b": "Amondarain"
      },
      {
        "a": "Orsolini",
        "b": "Bernardeschi"
      },
      {
        "a": "Dovbyk",
        "b": "Piccoli"
      },
      {
        "a": "Cambiaghi",
        "b": "Mbangula"
      }
    ],
    "formazione": [
      {
        "nome": "Skorupski"
      },
      {
        "nome": "Zortea"
      },
      {
        "nome": "Heggem"
      },
      {
        "nome": "Theate"
      },
      {
        "nome": "Miranda"
      },
      {
        "nome": "Odgaard"
      },
      {
        "nome": "Ferguson"
      },
      {
        "nome": "Pobega"
      },
      {
        "nome": "Orsolini"
      },
      {
        "nome": "Dovbyk"
      },
      {
        "nome": "Cambiaghi"
      }
    ]
  },
  {
    "squadra": "Cagliari",
    "allenatore": "Fabio Pisacane",
    "modulo": "4-4-2",
    "linee_fonte": [
      [
        "Caprile"
      ],
      [
        "Ze Pedro",
        "Mina",
        "Rodriguez",
        "Obert"
      ],
      [
        "Adopo",
        "Winks",
        "Romano",
        "Fazzini"
      ],
      [
        "Maldini",
        "Kevin Carlos"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Ze Pedro",
        "b": "Sugawara"
      },
      {
        "a": "Adopo",
        "b": "Fadera"
      },
      {
        "a": "Kevin Carlos",
        "b": "Nzola"
      }
    ],
    "formazione": [
      {
        "nome": "Caprile"
      },
      {
        "nome": "Ze Pedro"
      },
      {
        "nome": "Mina"
      },
      {
        "nome": "Rodriguez"
      },
      {
        "nome": "Obert"
      },
      {
        "nome": "Adopo"
      },
      {
        "nome": "Winks"
      },
      {
        "nome": "Romano"
      },
      {
        "nome": "Fazzini"
      },
      {
        "nome": "Maldini"
      },
      {
        "nome": "Kevin Carlos"
      }
    ]
  },
  {
    "squadra": "Como",
    "allenatore": "Cesc Fabregas",
    "modulo": "4-2-3-1",
    "linee_fonte": [
      [
        "Butez"
      ],
      [
        "Couto",
        "Chalobah",
        "Ramon",
        "Valle"
      ],
      [
        "Da Cunha",
        "Perrone"
      ],
      [
        "Diao",
        "Paz",
        "Baturina"
      ],
      [
        "Kean"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Couto",
        "b": "Smolcic"
      },
      {
        "a": "Valle",
        "b": "Kaiki"
      },
      {
        "a": "Diao",
        "b": "Rodriguez"
      },
      {
        "a": "Baturina",
        "b": "Milla"
      },
      {
        "a": "Kean",
        "b": "Douvikas"
      }
    ],
    "formazione": [
      {
        "nome": "Butez"
      },
      {
        "nome": "Couto"
      },
      {
        "nome": "Chalobah"
      },
      {
        "nome": "Ramon"
      },
      {
        "nome": "Valle"
      },
      {
        "nome": "Da Cunha"
      },
      {
        "nome": "Perrone"
      },
      {
        "nome": "Diao"
      },
      {
        "nome": "Paz"
      },
      {
        "nome": "Baturina"
      },
      {
        "nome": "Kean"
      }
    ]
  },
  {
    "squadra": "Fiorentina",
    "allenatore": "Fabio Grosso",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "De Gea"
      ],
      [
        "Jimenez",
        "Dragusin",
        "Viery",
        "Valdepenas"
      ],
      [
        "Ndour",
        "Fagioli",
        "Atta"
      ],
      [
        "Mastantuono",
        "Beto",
        "Goncalves"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Jimenez",
        "b": "Joao Mario"
      },
      {
        "a": "Viery",
        "b": "Pongracic"
      },
      {
        "a": "Fagioli",
        "b": "Oulai"
      },
      {
        "a": "Goncalves",
        "b": "Njie"
      },
      {
        "a": "Beto",
        "b": "Pellegrino"
      }
    ],
    "formazione": [
      {
        "nome": "De Gea"
      },
      {
        "nome": "Jimenez"
      },
      {
        "nome": "Dragusin"
      },
      {
        "nome": "Viery"
      },
      {
        "nome": "Valdepenas"
      },
      {
        "nome": "Ndour"
      },
      {
        "nome": "Fagioli"
      },
      {
        "nome": "Atta"
      },
      {
        "nome": "Mastantuono"
      },
      {
        "nome": "Beto"
      },
      {
        "nome": "Goncalves"
      }
    ]
  },
  {
    "squadra": "Frosinone",
    "allenatore": "Massimiliano Alvini",
    "modulo": "4-2-3-1",
    "linee_fonte": [
      [
        "Palmisani"
      ],
      [
        "Tchato",
        "Calvani",
        "Monterisi",
        "Bracaglia"
      ],
      [
        "Grillitsch",
        "Calò"
      ],
      [
        "Ghedjemis",
        "Schimd",
        "Kvernadze"
      ],
      [
        "Raimondo"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Tchato",
        "b": "Oyono"
      },
      {
        "a": "Bracaglia",
        "b": "Terzic"
      },
      {
        "a": "Grillitsch",
        "b": "Cichella"
      },
      {
        "a": "Raimondo",
        "b": "Bobcek"
      },
      {
        "a": "Ghedjemis",
        "b": "Zerbin"
      }
    ],
    "formazione": [
      {
        "nome": "Palmisani"
      },
      {
        "nome": "Tchato"
      },
      {
        "nome": "Calvani"
      },
      {
        "nome": "Monterisi"
      },
      {
        "nome": "Bracaglia"
      },
      {
        "nome": "Grillitsch"
      },
      {
        "nome": "Calò"
      },
      {
        "nome": "Ghedjemis"
      },
      {
        "nome": "Schimd"
      },
      {
        "nome": "Kvernadze"
      },
      {
        "nome": "Raimondo"
      }
    ]
  },
  {
    "squadra": "Genoa",
    "allenatore": "Daniele De Rossi",
    "modulo": "3-4-2-1",
    "linee_fonte": [
      [
        "Bijlow"
      ],
      [
        "Marcandalli",
        "Ostigard",
        "Vasquez"
      ],
      [
        "Ellertsson",
        "Frendrup",
        "Sow",
        "Mitaj"
      ],
      [
        "Baldanzi",
        "Vitinha"
      ],
      [
        "Colombo"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Mitaj",
        "b": "Puczka"
      },
      {
        "a": "Sow",
        "b": "Amorim"
      },
      {
        "a": "Vitinha",
        "b": "Osmajic"
      }
    ],
    "formazione": [
      {
        "nome": "Bijlow"
      },
      {
        "nome": "Marcandalli"
      },
      {
        "nome": "Ostigard"
      },
      {
        "nome": "Vasquez"
      },
      {
        "nome": "Ellertsson"
      },
      {
        "nome": "Frendrup"
      },
      {
        "nome": "Sow"
      },
      {
        "nome": "Mitaj"
      },
      {
        "nome": "Baldanzi"
      },
      {
        "nome": "Vitinha"
      },
      {
        "nome": "Colombo"
      }
    ]
  },
  {
    "squadra": "Inter",
    "allenatore": "Cristian Chivu",
    "modulo": "3-5-2",
    "linee_fonte": [
      [
        "Martinez"
      ],
      [
        "Bisseck",
        "Akanji",
        "Bastoni"
      ],
      [
        "Spence",
        "Barella",
        "Calhanoglu",
        "Jones",
        "Dimarco"
      ],
      [
        "Thuram",
        "Lautaro"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Bisseck",
        "b": "Stones"
      },
      {
        "a": "Spence",
        "b": "Diouf"
      },
      {
        "a": "Jones",
        "b": "Zielinski"
      },
      {
        "a": "Thuram",
        "b": "Pio Esposito"
      }
    ],
    "formazione": [
      {
        "nome": "Martinez"
      },
      {
        "nome": "Bisseck"
      },
      {
        "nome": "Akanji"
      },
      {
        "nome": "Bastoni"
      },
      {
        "nome": "Spence"
      },
      {
        "nome": "Barella"
      },
      {
        "nome": "Calhanoglu"
      },
      {
        "nome": "Jones"
      },
      {
        "nome": "Dimarco"
      },
      {
        "nome": "Thuram"
      },
      {
        "nome": "Lautaro"
      }
    ]
  },
  {
    "squadra": "Juventus",
    "allenatore": "Luciano Spalletti",
    "modulo": "4-2-3-1",
    "linee_fonte": [
      [
        "Vicario"
      ],
      [
        "Kalulu",
        "Bremer",
        "Lucumì",
        "Celik"
      ],
      [
        "Locatelli",
        "Sarr"
      ],
      [
        "Conceicao",
        "McKennie",
        "Gonzalez"
      ],
      [
        "Kolo Muani"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Lucumì",
        "b": "Kelly"
      },
      {
        "a": "Celik",
        "b": "Cambiaso"
      },
      {
        "a": "Sarr",
        "b": "Douglas Luiz"
      },
      {
        "a": "Gonzalez",
        "b": "Alajbegovic"
      },
      {
        "a": "Kolo Muani",
        "b": "Woltemade"
      }
    ],
    "formazione": [
      {
        "nome": "Vicario"
      },
      {
        "nome": "Kalulu"
      },
      {
        "nome": "Bremer"
      },
      {
        "nome": "Lucumì"
      },
      {
        "nome": "Celik"
      },
      {
        "nome": "Locatelli"
      },
      {
        "nome": "Sarr"
      },
      {
        "nome": "Conceicao"
      },
      {
        "nome": "McKennie"
      },
      {
        "nome": "Gonzalez"
      },
      {
        "nome": "Kolo Muani"
      }
    ]
  },
  {
    "squadra": "Lazio",
    "allenatore": "Gennaro Gattuso",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "Mandas"
      ],
      [
        "Marusic",
        "Sutalo",
        "Provstgaard",
        "Tavares"
      ],
      [
        "Frattesi",
        "Rovella",
        "Taylor"
      ],
      [
        "Isaksen",
        "Pinamonti",
        "Zaccagni"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Marusic",
        "b": "Floriani"
      },
      {
        "a": "Sutalo",
        "b": "Doekhi"
      },
      {
        "a": "Tavares",
        "b": "Pedraza"
      },
      {
        "a": "Isaksen",
        "b": "Cancellieri"
      },
      {
        "a": "Pinamonti",
        "b": "Gudmundsson"
      }
    ],
    "formazione": [
      {
        "nome": "Mandas"
      },
      {
        "nome": "Marusic"
      },
      {
        "nome": "Sutalo"
      },
      {
        "nome": "Provstgaard"
      },
      {
        "nome": "Tavares"
      },
      {
        "nome": "Frattesi"
      },
      {
        "nome": "Rovella"
      },
      {
        "nome": "Taylor"
      },
      {
        "nome": "Isaksen"
      },
      {
        "nome": "Pinamonti"
      },
      {
        "nome": "Zaccagni"
      }
    ]
  },
  {
    "squadra": "Lecce",
    "allenatore": "Eusebio Di Francesco",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "Falcone"
      ],
      [
        "Danilo Veiga",
        "Gaspar",
        "Tiago Gabriel",
        "Gallo"
      ],
      [
        "Coulibaly",
        "Ilic",
        "Berisha"
      ],
      [
        "Pierotti",
        "Geubbels",
        "Monteiro"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Ilic",
        "b": "Ngom"
      },
      {
        "a": "Berisha",
        "b": "Gandelman"
      },
      {
        "a": "Geubbels",
        "b": "Stulic"
      },
      {
        "a": "Monteiro",
        "b": "Fatah"
      }
    ],
    "formazione": [
      {
        "nome": "Falcone"
      },
      {
        "nome": "Danilo Veiga"
      },
      {
        "nome": "Gaspar"
      },
      {
        "nome": "Tiago Gabriel"
      },
      {
        "nome": "Gallo"
      },
      {
        "nome": "Coulibaly"
      },
      {
        "nome": "Ilic"
      },
      {
        "nome": "Berisha"
      },
      {
        "nome": "Pierotti"
      },
      {
        "nome": "Geubbels"
      },
      {
        "nome": "Monteiro"
      }
    ]
  },
  {
    "squadra": "Milan",
    "allenatore": "Ruben Amorim",
    "modulo": "3-4-2-1",
    "linee_fonte": [
      [
        "Maignan"
      ],
      [
        "Gila",
        "Gabbia",
        "Pavlovic"
      ],
      [
        "Moreira",
        "Modric",
        "Musah",
        "Bartesaghi"
      ],
      [
        "Rabiot",
        "Pulisic"
      ],
      [
        "Ramos"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Gabbia",
        "b": "De Winter"
      },
      {
        "a": "Bartesaghi",
        "b": "Chukwueze"
      },
      {
        "a": "Musah",
        "b": "Loftus-Cheek"
      },
      {
        "a": "Pulisic",
        "b": "Saelemaekers"
      }
    ],
    "formazione": [
      {
        "nome": "Maignan"
      },
      {
        "nome": "Gila"
      },
      {
        "nome": "Gabbia"
      },
      {
        "nome": "Pavlovic"
      },
      {
        "nome": "Moreira"
      },
      {
        "nome": "Modric"
      },
      {
        "nome": "Musah"
      },
      {
        "nome": "Bartesaghi"
      },
      {
        "nome": "Rabiot"
      },
      {
        "nome": "Pulisic"
      },
      {
        "nome": "Ramos"
      }
    ]
  },
  {
    "squadra": "Monza",
    "allenatore": "Ivan Juric",
    "modulo": "3-4-2-1",
    "linee_fonte": [
      [
        "Tornqvist"
      ],
      [
        "Ziolkowski",
        "Lucchesi",
        "Carboni"
      ],
      [
        "Birindelli",
        "Tourè",
        "Akinsanmiro",
        "Mangas"
      ],
      [
        "Ngonge",
        "Folorunsho"
      ],
      [
        "Varela"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Ziolkowski",
        "b": "Kouadio"
      },
      {
        "a": "Ngonge",
        "b": "Colpani"
      },
      {
        "a": "Varela",
        "b": "Cutrone"
      },
      {
        "a": "Tourè",
        "b": "Mout"
      },
      {
        "a": "Birindelli",
        "b": "Zeballos"
      }
    ],
    "formazione": [
      {
        "nome": "Tornqvist"
      },
      {
        "nome": "Ziolkowski"
      },
      {
        "nome": "Lucchesi"
      },
      {
        "nome": "Carboni"
      },
      {
        "nome": "Birindelli"
      },
      {
        "nome": "Tourè"
      },
      {
        "nome": "Akinsanmiro"
      },
      {
        "nome": "Mangas"
      },
      {
        "nome": "Ngonge"
      },
      {
        "nome": "Folorunsho"
      },
      {
        "nome": "Varela"
      }
    ]
  },
  {
    "squadra": "Napoli",
    "allenatore": "Massimiliano Allegri",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "Meret"
      ],
      [
        "Di Lorenzo",
        "Rrahmani",
        "Badiashile",
        "Spinazzola"
      ],
      [
        "De Bruyne",
        "Lobotka",
        "McTominay"
      ],
      [
        "Politano",
        "Hojlund",
        "Alisson Santos"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Badiashile",
        "b": "Buongiorno"
      },
      {
        "a": "Spinazzola",
        "b": "Olivera"
      },
      {
        "a": "De Bruyne",
        "b": "Anguissa"
      },
      {
        "a": "Politano",
        "b": "Vergara"
      }
    ],
    "formazione": [
      {
        "nome": "Meret"
      },
      {
        "nome": "Di Lorenzo"
      },
      {
        "nome": "Rrahmani"
      },
      {
        "nome": "Badiashile"
      },
      {
        "nome": "Spinazzola"
      },
      {
        "nome": "De Bruyne"
      },
      {
        "nome": "Lobotka"
      },
      {
        "nome": "McTominay"
      },
      {
        "nome": "Politano"
      },
      {
        "nome": "Hojlund"
      },
      {
        "nome": "Alisson Santos"
      }
    ]
  },
  {
    "squadra": "Parma",
    "allenatore": "Carlos Cuesta",
    "modulo": "4-3-1-2",
    "linee_fonte": [
      [
        "Corvi"
      ],
      [
        "Delprato",
        "Troilo",
        "Diego Carlos",
        "Valeri"
      ],
      [
        "Fabbian",
        "Keita",
        "Ordonez"
      ],
      [
        "Bernabè"
      ],
      [
        "Romero",
        "Tourè"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Corvi",
        "b": "Daffara"
      },
      {
        "a": "Romero",
        "b": "Elphege"
      },
      {
        "a": "Fabbian",
        "b": "Britschgi"
      }
    ],
    "formazione": [
      {
        "nome": "Corvi"
      },
      {
        "nome": "Delprato"
      },
      {
        "nome": "Troilo"
      },
      {
        "nome": "Diego Carlos"
      },
      {
        "nome": "Valeri"
      },
      {
        "nome": "Fabbian"
      },
      {
        "nome": "Keita"
      },
      {
        "nome": "Ordonez"
      },
      {
        "nome": "Bernabè"
      },
      {
        "nome": "Romero"
      },
      {
        "nome": "Tourè"
      }
    ]
  },
  {
    "squadra": "Roma",
    "allenatore": "Gian Piero Gasperini",
    "modulo": "3-4-2-1",
    "linee_fonte": [
      [
        "Svilar"
      ],
      [
        "Mancini",
        "N’Dicka",
        "Hermoso"
      ],
      [
        "Molina",
        "Koné",
        "Cristante",
        "Wesley"
      ],
      [
        "Dybala",
        "Mora"
      ],
      [
        "Malen"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Hermoso",
        "b": "Koulierakis"
      },
      {
        "a": "Mora",
        "b": "Soulè"
      },
      {
        "a": "Dybala",
        "b": "Castro"
      }
    ],
    "formazione": [
      {
        "nome": "Svilar"
      },
      {
        "nome": "Mancini"
      },
      {
        "nome": "N’Dicka"
      },
      {
        "nome": "Hermoso"
      },
      {
        "nome": "Molina"
      },
      {
        "nome": "Koné"
      },
      {
        "nome": "Cristante"
      },
      {
        "nome": "Wesley"
      },
      {
        "nome": "Dybala"
      },
      {
        "nome": "Mora"
      },
      {
        "nome": "Malen"
      }
    ]
  },
  {
    "squadra": "Sassuolo",
    "allenatore": "Alberto Aquilani",
    "modulo": "4-3-3",
    "linee_fonte": [
      [
        "Muric"
      ],
      [
        "Van der Brempt",
        "Idzes",
        "Caleta-Car",
        "Obrador"
      ],
      [
        "Thorstvedt",
        "Matic",
        "Adzic"
      ],
      [
        "Berardi",
        "Esposito",
        "Laurientè"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Caleta-Car",
        "b": "Leysen"
      },
      {
        "a": "Obrador",
        "b": "Doig"
      },
      {
        "a": "Adzic",
        "b": "Bakola"
      },
      {
        "a": "Esposito",
        "b": "Bowie"
      }
    ],
    "formazione": [
      {
        "nome": "Muric"
      },
      {
        "nome": "Van der Brempt"
      },
      {
        "nome": "Idzes"
      },
      {
        "nome": "Caleta-Car"
      },
      {
        "nome": "Obrador"
      },
      {
        "nome": "Thorstvedt"
      },
      {
        "nome": "Matic"
      },
      {
        "nome": "Adzic"
      },
      {
        "nome": "Berardi"
      },
      {
        "nome": "Esposito"
      },
      {
        "nome": "Laurientè"
      }
    ]
  },
  {
    "squadra": "Torino",
    "allenatore": "Ignazio Abate",
    "modulo": "3-4-2-1",
    "linee_fonte": [
      [
        "Perri"
      ],
      [
        "Comuzzo",
        "Coco",
        "Comert"
      ],
      [
        "Belghali",
        "Mandragora",
        "Fitz-Jim",
        "Cacciamani"
      ],
      [
        "Casadei",
        "Vlasic"
      ],
      [
        "Simeone"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Coco",
        "b": "Ismajli"
      },
      {
        "a": "Belghali",
        "b": "Patterson"
      },
      {
        "a": "Cacciamani",
        "b": "Fortini"
      },
      {
        "a": "Casadei",
        "b": "Braganca"
      }
    ],
    "formazione": [
      {
        "nome": "Perri"
      },
      {
        "nome": "Comuzzo"
      },
      {
        "nome": "Coco"
      },
      {
        "nome": "Comert"
      },
      {
        "nome": "Belghali"
      },
      {
        "nome": "Mandragora"
      },
      {
        "nome": "Fitz-Jim"
      },
      {
        "nome": "Cacciamani"
      },
      {
        "nome": "Casadei"
      },
      {
        "nome": "Vlasic"
      },
      {
        "nome": "Simeone"
      }
    ]
  },
  {
    "squadra": "Udinese",
    "allenatore": "Kosta Runjaic",
    "modulo": "3-4-2-1",
    "linee_fonte": [
      [
        "Okoye"
      ],
      [
        "Palma",
        "Kabasele",
        "Solet"
      ],
      [
        "Vojvoda",
        "Piotrowski",
        "Karlstrom",
        "Kamara"
      ],
      [
        "Zaniolo",
        "Ekkelenkamp"
      ],
      [
        "Davis"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Palma",
        "b": "Abankwah"
      },
      {
        "a": "Piotrowski",
        "b": "Miller"
      }
    ],
    "formazione": [
      {
        "nome": "Okoye"
      },
      {
        "nome": "Palma"
      },
      {
        "nome": "Kabasele"
      },
      {
        "nome": "Solet"
      },
      {
        "nome": "Vojvoda"
      },
      {
        "nome": "Piotrowski"
      },
      {
        "nome": "Karlstrom"
      },
      {
        "nome": "Kamara"
      },
      {
        "nome": "Zaniolo"
      },
      {
        "nome": "Ekkelenkamp"
      },
      {
        "nome": "Davis"
      }
    ]
  },
  {
    "squadra": "Venezia",
    "allenatore": "Giovanni Stroppa",
    "modulo": "3-5-2",
    "linee_fonte": [
      [
        "Stankovic"
      ],
      [
        "Schingtienne",
        "Bella-Kotchap",
        "Juan Jesus"
      ],
      [
        "Mazzocchi",
        "Kike Perez",
        "Busio",
        "Basic",
        "Haps"
      ],
      [
        "Yeboah",
        "Akor Adams"
      ]
    ],
    "ballottaggi": [
      {
        "a": "Juan Jesus",
        "b": "Halhal"
      },
      {
        "a": "Mazzocchi",
        "b": "Hainaut"
      },
      {
        "a": "Haps",
        "b": "Correia"
      },
      {
        "a": "Kike Perez",
        "b": "Sohm"
      },
      {
        "a": "Akor Adams",
        "b": "Rrahmani"
      }
    ],
    "formazione": [
      {
        "nome": "Stankovic"
      },
      {
        "nome": "Schingtienne"
      },
      {
        "nome": "Bella-Kotchap"
      },
      {
        "nome": "Juan Jesus"
      },
      {
        "nome": "Mazzocchi"
      },
      {
        "nome": "Kike Perez"
      },
      {
        "nome": "Busio"
      },
      {
        "nome": "Basic"
      },
      {
        "nome": "Haps"
      },
      {
        "nome": "Yeboah"
      },
      {
        "nome": "Akor Adams"
      }
    ]
  }
]


# ============================================================
# RIGORISTI E CALCI PIAZZATI - FONTE FANTACALCIO.IT
# Ordine = gerarchia pubblicata dalla fonte.
# ============================================================

FANTACALCIO_SPECIALISTI = {
    "Atalanta": {
        "rigoristi": ["Scamacca", "Krstovic", "Samardzic"],
        "calci_piazzati": ["De Ketelaere", "Samardzic", "Gaetano"],
    },
    "Bologna": {
        "rigoristi": ["Orsolini", "Bernardeschi", "Dovbyk"],
        "calci_piazzati": ["Orsolini", "Bernardeschi", "Miranda"],
    },
    "Cagliari": {
        "rigoristi": ["Nzola", "Kevin Carlos", "Mina"],
        "calci_piazzati": ["Fazzini", "Maldini", "Romano"],
    },
    "Como": {
        "rigoristi": ["Da Cunha", "Kean", "Douvikas"],
        "calci_piazzati": ["Paz", "Baturina", "Milla"],
    },
    "Fiorentina": {
        "rigoristi": ["Beto", "Pellegrino", "Goncalves"],
        "calci_piazzati": ["Mastantuono", "Atta", "Goncalves"],
    },
    "Frosinone": {
        "rigoristi": ["Calò", "Schimd", "Bobcek"],
        "calci_piazzati": ["Calò", "Schimd", "Ghedjemis"],
    },
    "Genoa": {
        "rigoristi": ["Colombo", "Ostigard", "Vitinha"],
        "calci_piazzati": ["Baldanzi", "Vitinha", "Messias"],
    },
    "Inter": {
        "rigoristi": ["Calhanoglu", "Zielinski", "Lautaro Martinez"],
        "calci_piazzati": ["Calhanoglu", "Dimarco", "Zielinski"],
    },
    "Juventus": {
        "rigoristi": ["Kolo Muani", "Woltemade", "Gonzalez"],
        "calci_piazzati": ["Yildiz", "Locatelli", "Douglas Luiz"],
    },
    "Lazio": {
        "rigoristi": ["Zaccagni", "Pinamonti", "Gudmundsson"],
        "calci_piazzati": ["Rovella", "Zaccagni", "Gudmundsson"],
    },
    "Lecce": {
        "rigoristi": ["Geubbels", "Stulic", "Berisha"],
        "calci_piazzati": ["Pierotti", "Berisha", "Gallo"],
    },
    "Milan": {
        "rigoristi": ["Ramos", "Pulisic", "Modric"],
        "calci_piazzati": ["Modric", "Pulisic", "Saelemaekers"],
    },
    "Monza": {
        "rigoristi": ["Cutrone", "Varela", "Ngonge"],
        "calci_piazzati": ["Ngonge", "Folorunsho", "Pessina"],
    },
    "Napoli": {
        "rigoristi": ["De Bruyne", "Hojlund", "Politano"],
        "calci_piazzati": ["De Bruyne", "Politano", "Neres"],
    },
    "Parma": {
        "rigoristi": ["Tourè", "Romero", "Valeri"],
        "calci_piazzati": ["Bernabè", "Nicolussi Caviglia", "Valeri"],
    },
    "Roma": {
        "rigoristi": ["Malen", "Dybala", "Castro"],
        "calci_piazzati": ["Dybala", "Malen", "Pellegrini"],
    },
    "Sassuolo": {
        "rigoristi": ["Berardi", "Esposito", "Laurientè"],
        "calci_piazzati": ["Berardi", "Laurientè", "Adzic"],
    },
    "Torino": {
        "rigoristi": ["Vlasic", "Simeone", "Mandragora"],
        "calci_piazzati": ["Vlasic", "Mandragora", "Gineitis"],
    },
    "Udinese": {
        "rigoristi": ["Davis", "Solet", "Zaniolo"],
        "calci_piazzati": ["Zaniolo", "Ekkelenkamp", "Unai Gomez"],
    },
    "Venezia": {
        "rigoristi": ["Busio", "Adams", "Adorante"],
        "calci_piazzati": ["Busio", "Yeboah", "Kike Perez"],
    },
}


def _specialisti_squadra(nome_squadra):
    target = _normalizza_nome_goal(
        nome_squadra
    )

    for squadra, dati in FANTACALCIO_SPECIALISTI.items():
        if _normalizza_nome_goal(
            squadra
        ) == target:
            return dati

    return {
        "rigoristi": [],
        "calci_piazzati": [],
    }


def _stesso_giocatore_specialista(
    nome_giocatore,
    nome_fonte,
    squadra
):
    """
    Prova prima il match testuale; poi usa il collegamento al listone
    già presente nell'app per gestire abbreviazioni tipo
    Lautaro / Lautaro Martinez, Adams / Akor Adams, ecc.
    """

    a = _normalizza_nome_goal(
        nome_giocatore
    )

    b = _normalizza_nome_goal(
        nome_fonte
    )

    if (
        a == b
        or a in b
        or b in a
    ):
        return True

    try:
        riga_fonte = _trova_giocatore_listone(
            nome_fonte,
            squadra
        )

        riga_giocatore = _trova_giocatore_listone(
            nome_giocatore,
            squadra
        )

        if (
            riga_fonte is not None
            and riga_giocatore is not None
        ):
            return int(
                riga_fonte.get(
                    "Id"
                )
            ) == int(
                riga_giocatore.get(
                    "Id"
                )
            )

    except Exception:
        pass

    return False



def invalida_cache_titolarita():
    """
    Invalida soltanto la cache derivata delle Formazioni Tipo.
    Va chiamata quando i dati delle formazioni vengono aggiornati.
    """

    prefisso = (
        "_rosa_titolarita_cache_"
    )

    for chiave in list(
        st.session_state.keys()
    ):

        if chiave.startswith(
            prefisso
        ):
            st.session_state.pop(
                chiave,
                None
            )

    st.session_state.pop(
        "_formazioni_tipo_fast_cache",
        None
    )


def costruisci_mappa_titolarita():
    """
    MULTILEGA 0.4 - FAST CACHE

    La mappa di titolarità è indipendente dal contenuto della rosa:
    dipende esclusivamente dalle Formazioni Tipo.

    Per questo viene costruita una sola volta e riutilizzata nei
    successivi ingressi in ROSA. La chiave include profilo, lega e team
    per evitare contaminazioni tra contesti multilega.
    """

    cache_key = (
        "_rosa_titolarita_cache_"
        + str(
            PROFILO_ATTIVO
        )
        + "_"
        + str(
            st.session_state.get(
                "ml_league_id",
                "legacy"
            )
        )
        + "_"
        + str(
            st.session_state.get(
                "ml_team_id",
                "none"
            )
        )
    )

    cache_esistente = (
        st.session_state.get(
            cache_key
        )
    )

    if isinstance(
        cache_esistente,
        dict
    ):
        return cache_esistente

    # Primo ingresso: usa i dati Formazioni Tipo e costruisce la mappa.
    dati_formazioni = carica_probabili_web()

    mappa = {}

    if not dati_formazioni:
        return mappa

    for squadra_data in dati_formazioni.get(
        "squadre",
        []
    ):

        squadra_nome = str(
            squadra_data.get(
                "squadra",
                ""
            )
        )

        squadra_key = _normalizza_nome_goal(
            squadra_nome
        )

        titolari = [
            str(
                g.get(
                    "nome",
                    ""
                )
            )
            for g in squadra_data.get(
                "formazione",
                []
            )
        ]

        # Inserisce prima tutti i titolari come TITOLARE.
        for nome in titolari:

            nome_key = _normalizza_nome_goal(
                nome
            )

            if nome_key:

                mappa[
                    (
                        squadra_key,
                        nome_key
                    )
                ] = {
                    "tipo":
                        "TITOLARE",

                    "contro":
                        ""
                }

        # Poi sovrascrive i giocatori coinvolti nei ballottaggi.
        for coppia in (
            squadra_data.get(
                "ballottaggi",
                []
            )
            or []
        ):

            a = str(
                coppia.get(
                    "a",
                    ""
                )
            )

            b = str(
                coppia.get(
                    "b",
                    ""
                )
            )

            a_key = _normalizza_nome_goal(
                a
            )

            b_key = _normalizza_nome_goal(
                b
            )

            if a_key:

                mappa[
                    (
                        squadra_key,
                        a_key
                    )
                ] = {
                    "tipo":
                        "BALLOTTAGGIO",

                    "contro":
                        b
                }

            if b_key:

                mappa[
                    (
                        squadra_key,
                        b_key
                    )
                ] = {
                    "tipo":
                        "BALLOTTAGGIO",

                    "contro":
                        a
                }

    st.session_state[
        cache_key
    ] = mappa

    return mappa


def info_titolarita_giocatore(
    nome_giocatore,
    squadra,
    mappa_titolarita=None
):
    """
    Lookup O(1) sulla mappa precomputata.

    Include un fallback leggero per nomi equivalenti tipo
    Lautaro / Lautaro Martinez.
    """

    if mappa_titolarita is None:

        mappa_titolarita = (
            costruisci_mappa_titolarita()
        )

    squadra_key = _normalizza_nome_goal(
        squadra
    )

    nome_key = _normalizza_nome_goal(
        nome_giocatore
    )

    chiave = (
        squadra_key,
        nome_key
    )

    if chiave in mappa_titolarita:

        return mappa_titolarita[
            chiave
        ]

    # Fallback limitato alla stessa squadra:
    # evita il costoso lookup sul dataframe completo.
    for (
        sq_key,
        giocatore_key
    ), info in mappa_titolarita.items():

        if sq_key != squadra_key:
            continue

        if (
            nome_key == giocatore_key
            or nome_key in giocatore_key
            or giocatore_key in nome_key
        ):

            return info

    return {
        "tipo": "",
        "contro": ""
    }



def html_titolarita_rosa(
    nome_giocatore,
    squadra,
    mappa_titolarita=None
):
    info = info_titolarita_giocatore(
        nome_giocatore,
        squadra,
        mappa_titolarita
    )

    tipo = info.get(
        "tipo",
        ""
    )

    if tipo == "TITOLARE":

        return (
            '<span style="font-weight:900;'
            'font-size:1.05rem;">⭐</span>'
        )

    if tipo == "BALLOTTAGGIO":

        contro = html.escape(
            str(
                info.get(
                    "contro",
                    ""
                )
            )
        )

        return (
            '<span style="color:#2563eb;'
            'font-weight:900;">B</span>'
            + (
                '<span style="color:#334155;'
                'font-weight:700;"> '
                + contro
                + '</span>'
                if contro
                else ""
            )
        )

    return ""


def sigle_specialista_giocatore(
    nome_giocatore,
    squadra
):
    """
    Restituisce, ad esempio:
        R1 · CP2
        R3
        CP1
    """

    dati = _specialisti_squadra(
        squadra
    )

    sigle = []

    for indice, nome_fonte in enumerate(
        dati.get(
            "rigoristi",
            []
        )[
            :3
        ],
        start=1
    ):
        if _stesso_giocatore_specialista(
            nome_giocatore,
            nome_fonte,
            squadra
        ):
            sigle.append(
                f"R{indice}"
            )
            break

    for indice, nome_fonte in enumerate(
        dati.get(
            "calci_piazzati",
            []
        )[
            :3
        ],
        start=1
    ):
        if _stesso_giocatore_specialista(
            nome_giocatore,
            nome_fonte,
            squadra
        ):
            sigle.append(
                f"CP{indice}"
            )
            break

    return " · ".join(
        sigle
    )


def _fc_snapshot_v18():
    return {
        "versione_dati": 21,
        "fonte": "Fantacalcio.it",
        "url_fonte": URL_PROBABILI_FORMAZIONI,
        "metodo_import": "snapshot_verificato",
        "scaricato_il": datetime.now(
            ZoneInfo(
                "Europe/Rome"
            )
        ).strftime(
            "%d/%m/%Y %H:%M"
        ),
        "squadre": FANTACALCIO_SNAPSHOT_V15
    }


def aggiorna_probabili_web():
    """
    V15 - FONTE UNICA E SOLA:
    URL_PROBABILI_FORMAZIONI

    Prova a leggere live ESATTAMENTE quella pagina.
    Se Streamlit Cloud riceve una shell/anti-bot senza il corpo
    dell'articolo, NON mostra errore e usa lo snapshot verificato
    derivato dalla stessa identica pagina.

    Nessuna seconda fonte, nessun AMP, nessun altro sito.
    """

    dati_live = None

    try:

        richiesta = urllib.request.Request(
            URL_PROBABILI_FORMAZIONI,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/152 Safari/537.36"
                ),
                "Accept":
                    "text/html,application/xhtml+xml",
                "Accept-Language":
                    "it-IT,it;q=0.9,en;q=0.7",
                "Cache-Control":
                    "no-cache"
            }
        )

        with urllib.request.urlopen(
            richiesta,
            timeout=25
        ) as risposta:

            raw = risposta.read().decode(
                "utf-8",
                "ignore"
            )

        testo = _fc_html_in_testo_puro(
            raw
        )

        squadre_live = []

        # Ricaviamo i nomi squadra DALLO SNAPSHOT della stessa fonte:
        # serve solo come indice per localizzare i blocchi.
        for riferimento in FANTACALCIO_SNAPSHOT_V15:

            nome_club = riferimento[
                "squadra"
            ]

            pattern = re.compile(
                rf"(?<![A-Za-zÀ-ÖØ-öø-ÿ])"
                rf"{re.escape(nome_club)}"
                rf"(?![A-Za-zÀ-ÖØ-öø-ÿ])"
                r"\s+Allenatore:\s*"
                r"(?P<allenatore>.+?)"
                r"\s+Modulo:\s*"
                r"(?P<modulo>[1-5](?:-[1-5]){2,4})"
                r"(?:\s*\([^)]*\))?"
                r"\s+Probabile formazione"
                r"\s*(?:\(da dx a sx\))?"
                r"\s*:\s*"
                r"(?P<formazione>.+?)"
                r"\s+Ballottaggi:\s*"
                r"(?P<ballottaggi>.+?)"
                r"\s+Rigoristi:\s*",
                flags=re.IGNORECASE
            )

            match = pattern.search(
                testo
            )

            if not match:
                continue

            modulo = match.group(
                "modulo"
            ).strip()

            parsed = _fc_parse_formazione(
                match.group(
                    "formazione"
                ),
                modulo
            )

            if not parsed:
                continue

            squadre_live.append({
                "squadra":
                    nome_club,

                "allenatore":
                    re.sub(
                        r"\s+",
                        " ",
                        match.group(
                            "allenatore"
                        )
                    ).strip(),

                "modulo":
                    modulo,

                "linee_fonte":
                    parsed[
                        "linee_fonte"
                    ],

                "formazione": [
                    {
                        "nome":
                            nome
                    }
                    for nome in parsed[
                        "titolari"
                    ]
                ],

                "ballottaggi":
                    _fc_parse_ballottaggi(
                        match.group(
                            "ballottaggi"
                        )
                    )
            })

        if (
            len(
                squadre_live
            ) == 20
            and all(
                len(
                    squadra.get(
                        "formazione",
                        []
                    )
                ) == 11
                for squadra in squadre_live
            )
        ):

            dati_live = {
                "versione_dati":
                    18,

                "fonte":
                    "Fantacalcio.it",

                "url_fonte":
                    URL_PROBABILI_FORMAZIONI,

                "metodo_import":
                    "live",

                "scaricato_il":
                    datetime.now(
                        ZoneInfo(
                            "Europe/Rome"
                        )
                    ).strftime(
                        "%d/%m/%Y %H:%M"
                    ),

                "squadre":
                    squadre_live
            }

    except Exception:
        dati_live = None

    # Se la lettura live è bloccata dal sito, usa SOLO il contenuto
    # verificato della STESSA pagina Fantacalcio.it.
    dati = (
        dati_live
        if dati_live
        else _fc_snapshot_v18()
    )

    salva_config_generica(
        "formazioni_tipo_fantacalcio_v21",
        json.dumps(
            dati,
            ensure_ascii=False
        )
    )

    # Cache locale persistente: resta disponibile anche senza Internet
    # e anche dopo la chiusura del browser/app.
    salva_cache_json_locale(
        CACHE_FORMAZIONI_PATH,
        dati
    )

    return dati

def carica_probabili_web():

    # MULTILEGA 0.4:
    # se i dati sono già stati letti in questa sessione, non interroga
    # nuovamente il DB cloud entrando in ROSA o FORMAZIONI TIPO.
    fast_cache = st.session_state.get(
        "_formazioni_tipo_fast_cache"
    )

    if (
        isinstance(
            fast_cache,
            dict
        )
        and len(
            fast_cache.get(
                "squadre",
                []
            )
        ) == 20
    ):
        return fast_cache

    # 1) Database/configurazione del profilo attivo.
    try:

        raw = leggi_config_generica(
            "formazioni_tipo_fantacalcio_v21",
            ""
        )

    except Exception:

        # La ROSA deve restare utilizzabile anche se il database cloud
        # della configurazione è momentaneamente indisponibile.
        raw = ""

    if raw:

        try:

            dati = json.loads(
                raw
            )

            if (
                isinstance(
                    dati,
                    dict
                )
                and len(
                    dati.get(
                        "squadre",
                        []
                    )
                ) == 20
            ):

                # Mantiene sincronizzata anche la cache locale.
                salva_cache_json_locale(
                    CACHE_FORMAZIONI_PATH,
                    dati
                )

                st.session_state[
                    "_formazioni_tipo_fast_cache"
                ] = dati

                return dati

        except Exception:
            pass

    # 2) Cache persistente locale dell'ultimo aggiornamento valido.
    dati_cache = leggi_cache_json_locale(
        CACHE_FORMAZIONI_PATH,
        None
    )

    if (
        isinstance(
            dati_cache,
            dict
        )
        and len(
            dati_cache.get(
                "squadre",
                []
            )
        ) == 20
    ):

        st.session_state[
            "_formazioni_tipo_fast_cache"
        ] = dati_cache

        return dati_cache

    # 3) Ultimo fallback incorporato nell'app.
    dati_snapshot = _fc_snapshot_v18()

    salva_cache_json_locale(
        CACHE_FORMAZIONI_PATH,
        dati_snapshot
    )

    st.session_state[
        "_formazioni_tipo_fast_cache"
    ] = dati_snapshot

    return dati_snapshot

def _normalizza_nome_goal(nome):
    testo = unicodedata.normalize(
        "NFKD",
        str(
            nome
            or ""
        )
    )

    testo = "".join(
        carattere
        for carattere in testo
        if not unicodedata.combining(
            carattere
        )
    )

    testo = testo.lower()

    testo = re.sub(
        r"[^a-z0-9 ]",
        " ",
        testo
    )

    return re.sub(
        r"\s+",
        " ",
        testo
    ).strip()




class _ParserTestoFantacalcio(HTMLParser):
    """
    Estrae tutto il testo visibile mantenendo l'ordine della pagina.
    Non dipende da classi CSS, <li>, immagini o struttura DOM specifica.
    """
    def __init__(self):
        super().__init__()
        self.tokens = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if (
            tag.lower() in {"script", "style", "noscript"}
            and self._skip_depth > 0
        ):
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth:
            return

        testo = html.unescape(
            str(data or "")
        )

        testo = re.sub(
            r"\s+",
            " ",
            testo
        ).strip()

        if testo:
            self.tokens.append(
                testo
            )


SQUADRE_INDISPONIBILI = [
    "Atalanta",
    "Bologna",
    "Cagliari",
    "Como",
    "Fiorentina",
    "Frosinone",
    "Genoa",
    "Inter",
    "Juventus",
    "Lazio",
    "Lecce",
    "Milan",
    "Monza",
    "Napoli",
    "Parma",
    "Roma",
    "Sassuolo",
    "Torino",
    "Udinese",
    "Venezia",
]


def _squadra_da_testo(token):
    """
    Riconosce la squadra anche se il token contiene altro testo,
    ad esempio 'ATALANTA - Infortunati' o 'Indisponibili Atalanta'.
    """
    norm = _normalizza_nome_goal(
        token
    )

    for squadra in SQUADRE_INDISPONIBILI:

        squadra_norm = _normalizza_nome_goal(
            squadra
        )

        if re.search(
            rf"(^| ){re.escape(squadra_norm)}($| )",
            norm
        ):
            return squadra

    return ""


def _sembra_nome_giocatore(token):
    """
    Euristica prudente: un nome giocatore è breve e non contiene
    frasi tipiche della descrizione medica/editoriale.
    """
    testo = str(
        token
        or ""
    ).strip()

    norm = _normalizza_nome_goal(
        testo
    )

    if not testo or len(testo) > 55:
        return False

    esclusi = {
        "infortunati",
        "squalificati",
        "diffidati",
        "nessuno",
        "indisponibili",
        "serie a",
        "probabili formazioni",
        "prossimo turno",
    }

    if norm in esclusi:
        return False

    parole_descrizione = [
        "lesione",
        "risentimento",
        "problema",
        "trauma",
        "operato",
        "recupero",
        "rientro",
        "tempi",
        "stop",
        "infortunio",
        "fastidio",
        "elongazione",
        "distrazione",
        "frattura",
        "contusione",
        "affaticamento",
        "pubalgia",
        "ginocchio",
        "caviglia",
        "coscia",
        "polpaccio",
        "muscolare",
        "tendine",
        "spalla",
        "schiena",
    ]

    if any(
        parola in norm
        for parola in parole_descrizione
    ):
        return False

    # Evita frasi normali troppo articolate.
    if len(
        testo.split()
    ) > 5:
        return False

    return True


def _sembra_descrizione_infortunio(token):
    testo = str(
        token
        or ""
    ).strip()

    norm = _normalizza_nome_goal(
        testo
    )

    if len(testo) < 18:
        return False

    segnali = [
        "lesione",
        "risentimento",
        "problema",
        "trauma",
        "operato",
        "recupero",
        "rientro",
        "tempi",
        "stop",
        "infortunio",
        "fastidio",
        "elongazione",
        "distrazione",
        "frattura",
        "contusione",
        "affaticamento",
        "pubalgia",
        "ginocchio",
        "caviglia",
        "coscia",
        "polpaccio",
        "muscolare",
        "tendine",
        "spalla",
        "schiena",
        "settembre",
        "ottobre",
        "novembre",
        "dicembre",
        "gennaio",
        "febbraio",
        "marzo",
        "aprile",
        "maggio",
    ]

    return (
        any(
            segnale in norm
            for segnale in segnali
        )
        or len(
            testo
        ) >= 45
    )


def _estrai_infortunati_da_tokens(tokens):
    """
    Strategia:
    1. individua ogni sezione 'Infortunati';
    2. ricava la squadra cercando nei token immediatamente precedenti;
    3. legge coppie NOME -> DESCRIZIONE fino a Squalificati/Diffidati
       o alla squadra successiva.

    Questo evita la dipendenza dalla struttura HTML del sito.
    """
    risultati = []

    for indice, token in enumerate(
        tokens
    ):

        norm = _normalizza_nome_goal(
            token
        )

        # La pagina può contenere "Infortunati" da solo o dentro un titolo.
        if (
            norm != "infortunati"
            and " infortunati" not in f" {norm}"
        ):
            continue

        squadra = ""

        # Cerca la squadra nei 20 token precedenti.
        for j in range(
            indice,
            max(
                -1,
                indice - 21
            ),
            -1
        ):
            squadra = _squadra_da_testo(
                tokens[
                    j
                ]
            )

            if squadra:
                break

        # Se non trovata prima, prova il token stesso.
        if not squadra:
            squadra = _squadra_da_testo(
                token
            )

        if not squadra:
            continue

        i = indice + 1

        while i < len(
            tokens
        ):

            corrente = tokens[
                i
            ]

            corrente_norm = _normalizza_nome_goal(
                corrente
            )

            # Fine sezione.
            if (
                corrente_norm in {
                    "squalificati",
                    "diffidati"
                }
                or corrente_norm.startswith(
                    "squalificati "
                )
                or corrente_norm.startswith(
                    "diffidati "
                )
            ):
                break

            # Fine anche se compare chiaramente una nuova squadra.
            nuova_squadra = _squadra_da_testo(
                corrente
            )

            if (
                nuova_squadra
                and nuova_squadra != squadra
                and i > indice + 1
            ):
                break

            if corrente_norm == "nessuno":
                break

            if not _sembra_nome_giocatore(
                corrente
            ):
                i += 1
                continue

            # Cerca la descrizione nei pochi token successivi.
            dettaglio_parts = []
            trovato_dettaglio = False

            for k in range(
                i + 1,
                min(
                    len(
                        tokens
                    ),
                    i + 7
                )
            ):

                successivo = tokens[
                    k
                ]

                successivo_norm = _normalizza_nome_goal(
                    successivo
                )

                if successivo_norm in {
                    "squalificati",
                    "diffidati",
                    "infortunati"
                }:
                    break

                if (
                    _squadra_da_testo(
                        successivo
                    )
                    and _squadra_da_testo(
                        successivo
                    ) != squadra
                ):
                    break

                if _sembra_descrizione_infortunio(
                    successivo
                ):

                    dettaglio_parts.append(
                        successivo
                    )

                    trovato_dettaglio = True

                    # A volte la descrizione è spezzata in due token.
                    if (
                        k + 1 < len(
                            tokens
                        )
                        and _sembra_descrizione_infortunio(
                            tokens[
                                k + 1
                            ]
                        )
                        and not _sembra_nome_giocatore(
                            tokens[
                                k + 1
                            ]
                        )
                    ):
                        dettaglio_parts.append(
                            tokens[
                                k + 1
                            ]
                        )

                    break

            if trovato_dettaglio:

                risultati.append({
                    "squadra":
                        squadra,

                    "nome":
                        corrente,

                    "dettaglio":
                        re.sub(
                            r"\s+",
                            " ",
                            " ".join(
                                dettaglio_parts
                            )
                        ).strip()
                })

            i += 1

    # Deduplica squadra + nome.
    finali = []
    visti = set()

    for item in risultati:

        key = (
            _normalizza_nome_goal(
                item.get(
                    "squadra",
                    ""
                )
            ),
            _normalizza_nome_goal(
                item.get(
                    "nome",
                    ""
                )
            )
        )

        if (
            key[0]
            and key[1]
            and key not in visti
        ):
            visti.add(
                key
            )

            finali.append(
                item
            )

    return finali


INFORTUNATI_SNAPSHOT_VERIFICATO = [
  {
    "squadra": "Atalanta",
    "nome": "Sulemana K.",
    "dettaglio": "Lesione del collaterale mediale di secondo grado del ginocchio sinistro; recuperabile da inizio ottobre."
  },
  {
    "squadra": "Atalanta",
    "nome": "Hien",
    "dettaglio": "Operato per una lesione del tendine prossimale del semimembranoso della coscia sinistra; rientro previsto da inizio ottobre."
  },
  {
    "squadra": "Atalanta",
    "nome": "Kristensen T.",
    "dettaglio": "Problema alla caviglia; indisponibile nelle ultime gare e da valutare quotidianamente."
  },
  {
    "squadra": "Bologna",
    "nome": "El Azzouzi O.",
    "dettaglio": "Lesione del bicipite femorale della coscia sinistra; recuperabile dalla seconda metà di settembre."
  },
  {
    "squadra": "Bologna",
    "nome": "Orsolini",
    "dettaglio": "Risentimento ai flessori della coscia sinistra; condizioni da valutare con esami, assente nel prossimo turno."
  },
  {
    "squadra": "Cagliari",
    "nome": "Mina",
    "dettaglio": "Affaticamento muscolare al polpaccio; out nell'ultimo turno e da valutare quotidianamente."
  },
  {
    "squadra": "Cagliari",
    "nome": "Trepy",
    "dettaglio": "Condizioni monitorate dallo staff medico; tempi di recupero da valutare, assente nel prossimo turno."
  },
  {
    "squadra": "Cagliari",
    "nome": "Idrissi R.",
    "dettaglio": "In recupero dalla rottura del legamento crociato; possibile rientro dalla fine di ottobre."
  },
  {
    "squadra": "Como",
    "nome": "Addai",
    "dettaglio": "Rottura del tendine d'Achille; rientro atteso dalla seconda metà di settembre."
  },
  {
    "squadra": "Fiorentina",
    "nome": "Parisi",
    "dettaglio": "Recupero dall'infortunio al legamento crociato del ginocchio; possibile rientro da novembre."
  },
  {
    "squadra": "Genoa",
    "nome": "Venturino",
    "dettaglio": "Operato al tendine rotuleo; in recupero, ipotesi di rientro da fine settembre."
  },
  {
    "squadra": "Juventus",
    "nome": "Yildiz",
    "dettaglio": "Frattura della base del V metatarso del piede sinistro, operato il 31 agosto; stop di circa tre mesi, rientro ipotizzato da fine novembre."
  },
  {
    "squadra": "Juventus",
    "nome": "Ekhator",
    "dettaglio": "Lesione di medio grado del muscolo semitendinoso; nuovi esami a metà settembre, possibile rientro da fine ottobre."
  },
  {
    "squadra": "Juventus",
    "nome": "Thuram K.",
    "dettaglio": "Sindrome femoro-rotulea; dopo consulto medico ha deciso di operarsi. Tempi lunghi, rientro ipotizzato da gennaio."
  },
  {
    "squadra": "Juventus",
    "nome": "McKennie",
    "dettaglio": "Affaticamento muscolare alla gamba; convocazione a rischio e condizioni da valutare."
  },
  {
    "squadra": "Lazio",
    "nome": "Patric",
    "dettaglio": "Problema fisico; indisponibile nell'ultimo turno e tempi di recupero da valutare."
  },
  {
    "squadra": "Lazio",
    "nome": "Marusic",
    "dettaglio": "Lesione muscolare alla coscia; ipotesi di rientro da inizio ottobre."
  },
  {
    "squadra": "Lazio",
    "nome": "Cataldi",
    "dettaglio": "In recupero dall'ernia bilaterale; possibile rientro dalla metà di settembre."
  },
  {
    "squadra": "Lazio",
    "nome": "Dele-Bashiru",
    "dettaglio": "Problema muscolare alla gamba; da valutare, possibile recupero dalla metà di settembre."
  },
  {
    "squadra": "Lecce",
    "nome": "Geubbels",
    "dettaglio": "Distorsione alla caviglia; tempi di recupero da valutare."
  },
  {
    "squadra": "Monza",
    "nome": "Ciurria",
    "dettaglio": "Noie fisiche; indisponibile nel prossimo turno, da valutare."
  },
  {
    "squadra": "Monza",
    "nome": "Pessina",
    "dettaglio": "Lussazione della rotula del ginocchio destro; possibile rientro da inizio novembre."
  },
  {
    "squadra": "Monza",
    "nome": "Varela G.",
    "dettaglio": "Fastidio muscolare all'adduttore; tempi di recupero da valutare."
  },
  {
    "squadra": "Napoli",
    "nome": "McTominay",
    "dettaglio": "Intervento di ablazione per lieve aritmia benigna; rientro previsto da inizio ottobre."
  },
  {
    "squadra": "Napoli",
    "nome": "Buongiorno",
    "dettaglio": "Operato al menisco del ginocchio destro; possibile rientro da metà novembre."
  },
  {
    "squadra": "Napoli",
    "nome": "Marianucci",
    "dettaglio": "Lesione di alto grado del collaterale mediale del ginocchio sinistro; stop di almeno due mesi."
  },
  {
    "squadra": "Parma",
    "nome": "Nicolussi Caviglia",
    "dettaglio": "Lesione di medio grado alla coscia destra e successivo intervento; lungo stop, rientro ipotizzato da novembre."
  },
  {
    "squadra": "Roma",
    "nome": "N'Dicka",
    "dettaglio": "Fastidio all'adduttore; da valutare."
  },
  {
    "squadra": "Sassuolo",
    "nome": "Walukiewicz",
    "dettaglio": "Forte trauma contusivo alla gamba destra; rientro da valutare da metà settembre."
  },
  {
    "squadra": "Sassuolo",
    "nome": "Candè",
    "dettaglio": "Rottura del legamento crociato anteriore del ginocchio destro; possibile rientro dalla metà di settembre."
  },
  {
    "squadra": "Sassuolo",
    "nome": "Pieragnolo",
    "dettaglio": "Recupero da lesione del legamento crociato anteriore; possibile rientro da ottobre."
  },
  {
    "squadra": "Sassuolo",
    "nome": "Boloca",
    "dettaglio": "Problema al ginocchio; rientro da valutare da fine settembre."
  },
  {
    "squadra": "Sassuolo",
    "nome": "Konè I.",
    "dettaglio": "Rottura di tibia e perone; operato, rientro previsto da dicembre."
  },
  {
    "squadra": "Torino",
    "nome": "Casadei",
    "dettaglio": "Affaticamento muscolare alla gamba; convocazione a rischio e condizioni da valutare."
  },
  {
    "squadra": "Udinese",
    "nome": "Palma",
    "dettaglio": "Problema muscolare all'adduttore della coscia destra; stop fino alla metà di settembre."
  },
  {
    "squadra": "Udinese",
    "nome": "Zanoli",
    "dettaglio": "Recupero da lesione del legamento crociato anteriore del ginocchio destro; possibile rientro da ottobre."
  },
  {
    "squadra": "Udinese",
    "nome": "Chakvetadze",
    "dettaglio": "Frattura del terzo metatarso del piede destro; recuperabile dalla prima metà di settembre."
  },
  {
    "squadra": "Udinese",
    "nome": "Zaniolo",
    "dettaglio": "Lesione muscolare al bicipite femorale della coscia destra; stop di circa 25 giorni, recuperabile dalla seconda metà di settembre."
  },
  {
    "squadra": "Venezia",
    "nome": "Moreno M.",
    "dettaglio": "Noie fisiche; da valutare il rientro."
  },
  {
    "squadra": "Venezia",
    "nome": "Sverko",
    "dettaglio": "Operato per un problema all'anca; recuperabile da fine ottobre."
  },
  {
    "squadra": "Venezia",
    "nome": "Franjic",
    "dettaglio": "Problema fisico; indisponibile nel prossimo turno."
  },
  {
    "squadra": "Venezia",
    "nome": "Adorante",
    "dettaglio": "Operato per un problema alla schiena; possibile rientro da ottobre."
  }
]


@st.cache_data(ttl=600, show_spinner=False)
def carica_infortunati_fantacalcio():
    """
    Modalità offline resiliente.

    Ordine:
    1. snapshot incorporato;
    2. ultima cache persistente salvata sul PC;
    3. dati live Fantacalcio.it, se raggiungibili.

    Il risultato viene risalvato su disco e resta disponibile
    anche se Internet cade durante l'asta o al riavvio dell'app.
    """

    unione = {}

    def aggiungi(items):
        for item in (
            items
            or []
        ):

            chiave = (
                _normalizza_nome_goal(
                    item.get(
                        "squadra",
                        ""
                    )
                ),
                _normalizza_nome_goal(
                    item.get(
                        "nome",
                        ""
                    )
                )
            )

            if (
                chiave[0]
                and chiave[1]
            ):

                unione[
                    chiave
                ] = dict(
                    item
                )

    # Base incorporata.
    aggiungi(
        INFORTUNATI_SNAPSHOT_VERIFICATO
    )

    # Ultima cache locale valida.
    cache_locale = leggi_cache_json_locale(
        CACHE_INFORTUNI_PATH,
        []
    )

    if isinstance(
        cache_locale,
        list
    ):
        aggiungi(
            cache_locale
        )

    # Aggiornamento live best-effort.
    risultati_live = []

    try:

        richiesta = urllib.request.Request(
            URL_INDISPONIBILI,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/152 Safari/537.36"
                ),
                "Accept":
                    "text/html,application/xhtml+xml",
                "Accept-Language":
                    "it-IT,it;q=0.9",
                "Cache-Control":
                    "no-cache"
            }
        )

        with urllib.request.urlopen(
            richiesta,
            timeout=10
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="ignore"
            )

        parser = _ParserTestoFantacalcio()
        parser.feed(
            raw
        )
        parser.close()

        risultati_live = _estrai_infortunati_da_tokens(
            parser.tokens
        )

    except Exception:

        risultati_live = []

    aggiungi(
        risultati_live
    )

    risultato = list(
        unione.values()
    )

    # Salva l'ultimo stato utilizzabile per la modalità offline.
    salva_cache_json_locale(
        CACHE_INFORTUNI_PATH,
        risultato
    )

    return risultato


def diagnostica_infortunati_fantacalcio():
    """
    Funzione diagnostica non mostrata nell'interfaccia.
    Utile per controllare rapidamente cosa ha letto il parser.
    """
    dati = carica_infortunati_fantacalcio()

    return {
        "totale":
            len(
                dati
            ),

        "giocatori":
            dati
    }



def info_disponibilita_giocatore(
    nome_giocatore,
    squadra
):
    """
    Determina la disponibilità usando l'elenco completo degli infortunati.
    Prima tenta il match sul listone, poi alias e confronto normalizzato.
    """

    squadra_norm = _normalizza_nome_goal(
        squadra
    )

    target_norm = _normalizza_nome_goal(
        nome_giocatore
    )

    riga_target = _trova_giocatore_listone(
        nome_giocatore,
        squadra
    )

    target_id = None

    if riga_target is not None:

        try:
            target_id = int(
                riga_target.get(
                    "Id"
                )
            )
        except Exception:
            target_id = None

    for item in carica_infortunati_fantacalcio():

        squadra_item = item.get(
            "squadra",
            ""
        )

        if _normalizza_nome_goal(
            squadra_item
        ) != squadra_norm:
            continue

        nome_item = item.get(
            "nome",
            ""
        )

        # 1. Match tramite ID del listone.
        riga_item = _trova_giocatore_listone(
            nome_item,
            squadra_item
        )

        if (
            target_id is not None
            and riga_item is not None
        ):

            try:

                if target_id == int(
                    riga_item.get(
                        "Id"
                    )
                ):

                    return {
                        "disponibile":
                            False,

                        "dettaglio":
                            item.get(
                                "dettaglio",
                                ""
                            ),

                        "nome_fonte":
                            nome_item
                    }

            except Exception:
                pass

        # 2. Alias esplicito.
        alias = _alias_nome_listone(
            nome_item,
            squadra_item
        )

        if (
            alias
            and _normalizza_nome_goal(
                alias
            ) == target_norm
        ):

            return {
                "disponibile":
                    False,

                "dettaglio":
                    item.get(
                        "dettaglio",
                        ""
                    ),

                "nome_fonte":
                    nome_item
            }

        # 3. Nome identico/compatibile.
        item_norm = _normalizza_nome_goal(
            nome_item
        )

        if (
            target_norm
            and item_norm
            and (
                target_norm == item_norm
                or target_norm in item_norm
                or item_norm in target_norm
            )
        ):

            return {
                "disponibile":
                    False,

                "dettaglio":
                    item.get(
                        "dettaglio",
                        ""
                    ),

                "nome_fonte":
                    nome_item
            }

    return {
        "disponibile":
            True,

        "dettaglio":
            "",

        "nome_fonte":
            ""
    }




def diagnostica_infortunati_non_abbinati():
    """
    Elenco degli infortunati della fonte che non trovano corrispondenza
    nel listone. Utile per controlli futuri dopo aggiornamenti del listone.
    """

    mancanti = []

    for item in carica_infortunati_fantacalcio():

        riga = _trova_giocatore_listone(
            item.get(
                "nome",
                ""
            ),
            item.get(
                "squadra",
                ""
            )
        )

        if riga is None:

            mancanti.append({
                "Squadra":
                    item.get(
                        "squadra",
                        ""
                    ),

                "Nome fonte":
                    item.get(
                        "nome",
                        ""
                    )
            })

    return mancanti


@st.dialog("Dettaglio infortunio")
def mostra_dettaglio_infortunio(nome,squadra,dettaglio):
    st.markdown(f"### {html.escape(str(nome))}")
    st.caption(html.escape(str(squadra)))
    st.markdown(
        '<div style="border-left:5px solid #dc2626;background:#fff5f5;'
        'padding:14px 16px;border-radius:8px;font-size:1rem;line-height:1.45;">'
        + html.escape(str(dettaglio))
        + '</div>',
        unsafe_allow_html=True
    )
    st.caption("Fonte: Fantacalcio.it · Indisponibili Serie A")




# ============================================================
# ALIAS NOMI FANTACALCIO.IT -> LISTONE
# Serve a gestire abbreviazioni/differenze editoriali tra
# la pagina Formazioni Tipo e il listone ufficiale caricato.
# ============================================================

ALIAS_NOMI_FORMAZIONI = {
    ("atalanta", "kristensen"): "Kristensen T.",
    ("atalanta", "ederson"): "Ederson D.S.",

    ("bologna", "miranda"): "Miranda J.",
    ("bologna", "moro"): "Moro N.",

    ("cagliari", "rodriguez"): "Rodriguez Ju.",

    ("como", "chalobah"): "Chalobah T.",
    ("como", "paz"): "Paz N.",
    ("como", "smolcic"): "Smolcic I.",
    ("como", "rodriguez"): "Rodriguez Je.",

    ("fiorentina", "jimenez"): "Jimenez A.",
    ("fiorentina", "pellegrino"): "Pellegrino M.",

    ("frosinone", "schimd"): "Schmid",

    ("genoa", "vitinha"): "Vitinha O.",

    ("inter", "martinez"): "Martinez Jo.",
    ("inter", "lautaro"): "Martinez L.",
    ("inter", "lautaro martinez"): "Martinez L.",
    ("inter", "jones"): "Jones C.",
    ("inter", "pio esposito"): "Esposito F.P.",

    ("juventus", "kelly"): "Kelly L.",

    ("lazio", "sutalo"): "Sutalo J.",
    ("lazio", "tavares"): "Tavares N.",
    ("lazio", "taylor"): "Taylor K.",
    ("lazio", "floriani"): "Floriani Mussolini",

    ("lecce", "danilo veiga"): "Veiga D.",
    ("lecce", "gaspar"): "Gaspar K.",
    ("lecce", "coulibaly"): "Coulibaly L.",
    ("lecce", "berisha"): "Berisha M.",

    ("milan", "ramos"): "Ramos G.",

    ("monza", "carboni"): "Carboni A.",
    ("monza", "tourè"): "Tourè I.",
    ("monza", "varela"): "Varela G.",

    ("napoli", "alisson santos"): "Santos A.",
    ("napoli", "anguissa"): "Zambo Anguissa",

    ("parma", "keita"): "Keita M.",
    ("parma", "ordonez"): "Ordonez C.",
    ("parma", "romero"): "Romero D.",
    ("parma", "tourè"): "Tourè E.",

    ("roma", "molina"): "Molina N.",
    ("roma", "koné"): "Konè M.",
    ("roma", "kone"): "Konè M.",
    ("roma", "castro"): "Castro S.",

    ("sassuolo", "leysen"): "Leysen F.",

    ("udinese", "kamara"): "Kamara H.",
    ("udinese", "davis"): "Davis K.",
    ("udinese", "miller"): "Miller L.",

    ("venezia", "stankovic"): "Stankovic F.",
    ("venezia", "kike perez"): "Perez K.",
    ("venezia", "yeboah"): "Yeboah J.",
    ("venezia", "akor adams"): "Adams A.",
    ("venezia", "correia"): "Correia T.",
    ("venezia", "rrahmani"): "Rrahmani Al.",

    # Alias specifici della fonte Infortunati Fantacalcio.it
    ("atalanta", "sulemana k"): "Sulemana K.",
    ("atalanta", "kristensen t"): "Kristensen T.",
    ("cagliari", "mina"): "Mina",
    ("cagliari", "trepy"): "Trepy",
    ("juventus", "yildiz"): "Yildiz",
    ("juventus", "thuram k"): "Thuram K.",
    ("juventus", "thuram"): "Thuram K.",

    # Alias per indisponibili correnti
    ("fiorentina", "parisi"): "Parisi",
    ("lazio", "pellegrini lu"): "Pellegrini Lu.",
    ("sassuolo", "kone i"): "Konè I.",
    ("sassuolo", "kone"): "Konè I.",
    ("bologna", "el azzouzi o"): "El Azzouzi O.",
    ("bologna", "el azzouzi"): "El Azzouzi O.",
    ("atalanta", "sulemana"): "Sulemana K.",
    ("atalanta", "sulemana k"): "Sulemana K.",
    ("atalanta", "kristensen"): "Kristensen T.",
    ("atalanta", "kristensen t"): "Kristensen T.",
}


def _alias_nome_listone(
    nome_fonte,
    squadra_fonte
):
    squadra_key = _normalizza_nome_goal(
        squadra_fonte
    )

    nome_key = _normalizza_nome_goal(
        nome_fonte
    )

    return ALIAS_NOMI_FORMAZIONI.get(
        (
            squadra_key,
            nome_key
        )
    )


def _trova_giocatore_listone(
    nome_goal,
    squadra_goal=""
):
    if (
        "df_completo" not in globals()
        or df_completo is None
        or df_completo.empty
        or "Nome" not in df_completo.columns
    ):
        return None

    target = _normalizza_nome_goal(
        nome_goal
    )

    squadra_target = _normalizza_nome_goal(
        squadra_goal
    )

    if not target:
        return None

    # 1) Alias espliciti: soluzione prioritaria e sicura per i
    # nomi editoriali che non condividono token col listone
    # (es. Lautaro -> Martinez L.).
    alias_esatto = _alias_nome_listone(
        nome_goal,
        squadra_goal
    )

    if alias_esatto:

        alias_norm = _normalizza_nome_goal(
            alias_esatto
        )

        for _, riga in df_completo.iterrows():

            if (
                _normalizza_nome_goal(
                    riga.get(
                        "Squadra",
                        ""
                    )
                ) == squadra_target
                and _normalizza_nome_goal(
                    riga.get(
                        "Nome",
                        ""
                    )
                ) == alias_norm
            ):
                return riga

    candidati = []

    for _, riga in df_completo.iterrows():

        nome_listone = str(
            riga.get(
                "Nome",
                ""
            )
        )

        squadra_listone = str(
            riga.get(
                "Squadra",
                ""
            )
        )

        normalizzato = _normalizza_nome_goal(
            nome_listone
        )

        squadra_norm = _normalizza_nome_goal(
            squadra_listone
        )

        if not normalizzato:
            continue

        bonus_squadra = 0

        if squadra_target:

            if squadra_norm == squadra_target:
                bonus_squadra = 30

            elif (
                squadra_target in squadra_norm
                or squadra_norm in squadra_target
            ):
                bonus_squadra = 20

            else:
                continue

        if normalizzato == target:
            return riga

        token_target = set(
            target.split()
        )

        token_listone = set(
            normalizzato.split()
        )

        intersezione = (
            token_target
            & token_listone
        )

        if intersezione:

            punteggio = (
                bonus_squadra
                + len(
                    intersezione
                ) * 10
                - abs(
                    len(
                        token_target
                    )
                    - len(
                        token_listone
                    )
                )
            )

            if (
                target in normalizzato
                or normalizzato in target
            ):
                punteggio += 8

            candidati.append(
                (
                    punteggio,
                    riga
                )
            )

    if not candidati:

        # 3) Fallback fuzzy molto prudente, solo nella stessa squadra.
        # Si attiva esclusivamente se esiste un candidato nettamente
        # simile (>= 0.84) e non ambiguo.
        import difflib

        fuzzy = []

        for _, riga in df_completo.iterrows():

            squadra_norm = _normalizza_nome_goal(
                riga.get(
                    "Squadra",
                    ""
                )
            )

            if (
                squadra_target
                and squadra_norm != squadra_target
            ):
                continue

            nome_norm = _normalizza_nome_goal(
                riga.get(
                    "Nome",
                    ""
                )
            )

            if not nome_norm:
                continue

            similarita = difflib.SequenceMatcher(
                None,
                target,
                nome_norm
            ).ratio()

            if similarita >= 0.84:

                fuzzy.append(
                    (
                        similarita,
                        riga
                    )
                )

        fuzzy.sort(
            key=lambda x: x[0],
            reverse=True
        )

        if fuzzy:

            migliore = fuzzy[0]

            secondo = (
                fuzzy[1][0]
                if len(
                    fuzzy
                ) > 1
                else 0
            )

            # Richiede un margine minimo dal secondo candidato.
            if (
                migliore[0] >= 0.84
                and (
                    migliore[0]
                    - secondo
                ) >= 0.05
            ):
                return migliore[1]

        return None

    candidati.sort(
        key=lambda x: x[0],
        reverse=True
    )

    soglia = (
        20
        if squadra_target
        else 9
    )

    if candidati[0][0] < soglia:
        return None

    return candidati[0][1]


def diagnostica_nomi_formazioni_senza_riscontro():
    """
    Restituisce un elenco dei nomi presenti nelle Formazioni Tipo
    che non trovano alcuna corrispondenza nel listone corrente.

    Non viene mostrato automaticamente nell'interfaccia.
    È utile per futuri controlli dopo aggiornamenti del listone.
    """

    dati = carica_probabili_web()

    if (
        not dati
        or "df_completo" not in globals()
        or df_completo is None
        or df_completo.empty
    ):
        return []

    mancanti = []
    gia_visti = set()

    for squadra in dati.get(
        "squadre",
        []
    ):

        nome_squadra = squadra.get(
            "squadra",
            ""
        )

        nomi = []

        for giocatore in squadra.get(
            "formazione",
            []
        ):
            nomi.append(
                giocatore.get(
                    "nome",
                    ""
                )
            )

        for coppia in (
            squadra.get(
                "ballottaggi",
                []
            )
            or []
        ):
            nomi.extend(
                [
                    coppia.get(
                        "a",
                        ""
                    ),
                    coppia.get(
                        "b",
                        ""
                    )
                ]
            )

        for nome in nomi:

            chiave = (
                _normalizza_nome_goal(
                    nome_squadra
                ),
                _normalizza_nome_goal(
                    nome
                )
            )

            if (
                not chiave[1]
                or chiave in gia_visti
            ):
                continue

            gia_visti.add(
                chiave
            )

            if _trova_giocatore_listone(
                nome,
                nome_squadra
            ) is None:

                mancanti.append({
                    "Squadra":
                        nome_squadra,

                    "Nome formazione":
                        nome
                })

    return mancanti


def _ruoli_mantra_goal(
    nome_goal,
    squadra_goal=""
):
    riga = _trova_giocatore_listone(
        nome_goal,
        squadra_goal
    )

    if riga is None:
        return []

    rm = str(
        riga.get(
            "RM",
            ""
        )
        or ""
    ).strip()

    if not rm:
        return []

    return [
        ruolo.strip()
        for ruolo in rm.split(
            ";"
        )
        if ruolo.strip()
    ]


def _gruppo_tattico_da_ruolo(ruolo):
    ruolo = str(
        ruolo
        or ""
    ).strip().upper()

    if ruolo == "POR":
        return "P"

    if ruolo in {
        "DC",
        "B",
        "DD",
        "DS"
    }:
        return "D"

    if ruolo in {
        "E",
        "M",
        "C"
    }:
        return "C"

    if ruolo in {
        "W",
        "T",
        "A",
        "PC"
    }:
        return "A"

    return ""


def _ruolo_singolo_per_linea(
    ruoli,
    gruppo_linea
):
    """
    Mostra UN SOLO ruolo Mantra, scegliendo quello più coerente
    con la linea tattica in cui il giocatore viene collocato.
    """

    ruoli = [
        str(
            r
        ).strip()
        for r in (
            ruoli
            or []
        )
        if str(
            r
        ).strip()
    ]

    if not ruoli:
        return "—"

    preferenze = {
        "P": [
            "Por"
        ],
        "D": [
            "Ds",
            "Dd",
            "Dc",
            "B"
        ],
        "C": [
            "E",
            "M",
            "C"
        ],
        "A": [
            "W",
            "T",
            "A",
            "Pc"
        ]
    }

    for preferito in preferenze.get(
        gruppo_linea,
        []
    ):

        for ruolo in ruoli:

            if ruolo.upper() == preferito.upper():
                return ruolo

    return ruoli[
        0
    ]


def _gruppi_linee_goal(
    modulo,
    numero_linee
):
    """
    Le linee GOAL arrivano come:
    P ; D ; C/... ; A

    Restituiamo il gruppo tattico di ciascuna linea
    nello stesso ordine della fonte.
    """

    if numero_linee <= 1:
        return [
            "P"
        ]

    # Prima linea = portiere.
    gruppi = [
        "P"
    ]

    # Seconda = difesa.
    if numero_linee >= 2:
        gruppi.append(
            "D"
        )

    # Ultima = attacco.
    linee_intermedie = max(
        0,
        numero_linee - 3
    )

    for indice in range(
        linee_intermedie
    ):
        # Se ci sono più linee tra difesa e attacco,
        # l'ultima intermedia è più offensiva.
        if (
            linee_intermedie > 1
            and indice
            == linee_intermedie - 1
        ):
            gruppi.append(
                "A"
            )
        else:
            gruppi.append(
                "C"
            )

    if numero_linee >= 3:
        gruppi.append(
            "A"
        )

    return gruppi[
        :numero_linee
    ]


def _goal_visual_lines(
    squadra
):
    """
    Mantiene ESATTAMENTE le linee tattiche pubblicate da GOAL.
    Restituisce attacco -> ... -> portiere, come richiesto dal campo.
    """

    linee = squadra.get(
        "linee_fonte",
        []
    ) or []

    gruppi = _gruppi_linee_goal(
        squadra.get(
            "modulo",
            ""
        ),
        len(
            linee
        )
    )

    coppie = list(
        zip(
            linee,
            gruppi
        )
    )

    return list(
        reversed(
            coppie
        )
    )


def _stesso_giocatore(
    nome_a,
    nome_b
):

    return (
        _normalizza_nome_goal(
            nome_a
        )
        == _normalizza_nome_goal(
            nome_b
        )
    )


def _ballottaggio_del_titolare(
    squadra,
    nome_titolare
):
    """
    Cerca la PRIMA coppia Fantacalcio.it che coinvolge il titolare.

    Se la fonte scrive:
        Piccoli/Dovbyk
    e Dovbyk è nell'XI, restituisce Piccoli.

    Se scrive:
        Bellanova/Zappacosta
    e Bellanova è nell'XI, restituisce Zappacosta.

    Massimo un concorrente per card.
    """

    for coppia in (
        squadra.get(
            "ballottaggi",
            []
        )
        or []
    ):

        a = coppia.get(
            "a",
            ""
        )

        b = coppia.get(
            "b",
            ""
        )

        if _stesso_giocatore(
            nome_titolare,
            a
        ):

            return b

        if _stesso_giocatore(
            nome_titolare,
            b
        ):

            return a

    return None



def stato_giocatore_formazione(
    nome_giocatore,
    squadra
):
    """
    Restituisce lo stato corrente del giocatore nel listone:
      MIO         -> acquistato dalla nostra rosa
      AVVERSARIO  -> acquistato da un avversario
      DISPONIBILE -> ancora libero

    Il matching usa la stessa funzione già impiegata per ruoli Mantra
    e specialisti, quindi resta coerente col resto dell'app.
    """

    try:

        riga = _trova_giocatore_listone(
            nome_giocatore,
            squadra
        )

        if riga is None:
            return "DISPONIBILE"

        stato = str(
            riga.get(
                "Stato",
                "DISPONIBILE"
            )
            or "DISPONIBILE"
        ).strip().upper()

        if stato in {
            "MIO",
            "AVVERSARIO"
        }:
            return stato

    except Exception:
        pass

    return "DISPONIBILE"


def html_nome_formazione(
    nome_giocatore,
    squadra,
    classe_css,
    colore
):
    """
    Applica la resa grafica richiesta:
    - ⭐ prima del nome se il giocatore è nella nostra rosa
    - nome barrato se è stato acquistato da un avversario
    """

    stato = stato_giocatore_formazione(
        nome_giocatore,
        squadra
    )

    nome_html = html.escape(
        str(
            nome_giocatore
        )
    )

    if stato == "MIO":

        contenuto = (
            "⭐ "
            + nome_html
        )

        style_extra = ""

    elif stato == "AVVERSARIO":

        contenuto = nome_html

        style_extra = (
            "text-decoration-line:line-through;"
            "text-decoration-color:#000000;"
            "text-decoration-thickness:3px;"
            "opacity:0.72;"
        )

    else:

        contenuto = nome_html
        style_extra = ""

    return (
        '<span class="'
        + classe_css
        + '" style="color:'
        + colore
        + ' !important;'
        + style_extra
        + '">'
        + contenuto
        + '</span>'
    )


def mostra_probabile(
    squadra
):
    """
    CARD V10:

    CASO 1 - nessun ballottaggio:
        TITOLARE VERDE + ruoli Mantra

    CASO 2 - ballottaggio esplicito Fantacalcio.it:
        TITOLARE BLU + ruoli Mantra
        CONCORRENTE BLU + ruoli Mantra

    Nessun altro nome viene mostrato nella card.
    """

    linee_originali = squadra.get(
        "linee_fonte",
        []
    ) or []

    righe_html = ""

    # Fantacalcio.it pubblica:
    # portiere -> difesa -> centrocampo/... -> attacco.
    # Sul campo mostriamo attacco -> ... -> portiere.
    for linea in reversed(
        linee_originali
    ):

        giocatori_html = ""

        nomi_validi = list(
            reversed(
                [
                    nome
                    for nome in linea
                    if _goal_nome_valido(
                        nome
                    )
                ]
            )
        )

        for nome_raw in nomi_validi:

            concorrente = (
                _ballottaggio_del_titolare(
                    squadra,
                    nome_raw
                )
            )

            in_ballottaggio = bool(
                concorrente
            )

            colore_principale = (
                "#2563eb"
                if in_ballottaggio
                else "#16a34a"
            )

            nome = str(
                nome_raw
            )

            ruoli = _ruoli_mantra_goal(
                nome_raw,
                squadra.get(
                    "squadra",
                    ""
                )
            )

            ruolo = html.escape(
                ";".join(
                    ruoli
                )
                if ruoli
                else "—"
            )

            secondo_html = ""

            if concorrente:

                nome_alt = str(
                    concorrente
                )

                ruoli_alt = (
                    _ruoli_mantra_goal(
                        concorrente,
                        squadra.get(
                            "squadra",
                            ""
                        )
                    )
                )

                ruolo_alt = html.escape(
                    ";".join(
                        ruoli_alt
                    )
                    if ruoli_alt
                    else "—"
                )

                secondo_html = (
                    '<div class="pf-sub-player">'
                    + html_nome_formazione(
                        nome_alt,
                        squadra.get(
                            "squadra",
                            ""
                        ),
                        "pf-sub-name",
                        "#2563eb"
                    )
                    + '<span class="pf-sub-role">'
                    + ruolo_alt
                    + '</span>'
                    '</div>'
                )

            giocatori_html += (
                '<div class="pf-player pf-player-goal">'
                '<div class="pf-main-player">'
                + html_nome_formazione(
                    nome,
                    squadra.get(
                        "squadra",
                        ""
                    ),
                    "pf-name",
                    colore_principale
                )
                + '<span class="pf-mantra-role">'
                + ruolo
                + '</span>'
                '</div>'
                + secondo_html
                + '</div>'
            )

        numero_card_linea = max(
            1,
            len(
                nomi_validi
            )
        )

        righe_html += (
            '<div class="pf-line pf-line-count-'
            + str(
                numero_card_linea
            )
            + '">'
            + giocatori_html
            + '</div>'
        )

    titolo = html.escape(
        str(
            squadra.get(
                "squadra",
                ""
            )
        )
    )

    modulo = html.escape(
        str(
            squadra.get(
                "modulo",
                ""
            )
        )
    )

    st.markdown(
        '<div class="pf-team">'
        + titolo
        + '<span>'
        + modulo
        + '</span></div>'
        + '<div class="pf-pitch">'
        + righe_html
        + '</div>',
        unsafe_allow_html=True
    )

    specialisti = _specialisti_squadra(
        squadra.get(
            "squadra",
            ""
        )
    )

    rigoristi = ", ".join(
        specialisti.get(
            "rigoristi",
            []
        )[
            :3
        ]
    ) or "—"

    piazzati = ", ".join(
        specialisti.get(
            "calci_piazzati",
            []
        )[
            :3
        ]
    ) or "—"

    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #dbe3ec;
            border-top:0;
            border-radius:0 0 10px 10px;
            padding:8px 12px 10px 12px;
            margin-top:-2px;
            font-size:1.00rem;
            line-height:1.45;
            color:#334155;
        ">
            <div>
                <b>⚽ Rigoristi:</b>
                {html.escape(rigoristi)}
            </div>
            <div>
                <b>🎯 Calci piazzati:</b>
                {html.escape(piazzati)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def leggi_budget_asta():

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT valore
            FROM configurazione_app
            WHERE chiave = 'budget_asta'
        """)

        riga = cur.fetchone()

    finally:

        chiudi_connessione(
            conn
        )

    if not riga:

        return float(
            SOGLIA_BASE
        )

    try:

        return float(
            riga[0]
        )

    except Exception:

        return float(
            SOGLIA_BASE
        )


def salva_budget_asta(
    valore
):

    try:

        valore = round(
            max(
                0.0,
                float(
                    valore
                )
            ),
            2
        )

    except Exception:

        valore = float(
            SOGLIA_BASE
        )

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO configurazione_app (
                chiave,
                valore
            )
            VALUES (
                'budget_asta',
                ?
            )

            ON CONFLICT(chiave)
            DO UPDATE SET
                valore = excluded.valore
        """, (
            str(
                valore
            ),
        ))

        conn.commit()

    finally:

        chiudi_connessione(
            conn
        )

    return valore


def aggiorna_budget_da_widget():

    try:

        nuovo_budget = round(
            float(
                st.session_state.get(
                    "budget_asta_input",
                    SOGLIA_BASE
                )
            ),
            2
        )

    except Exception:

        nuovo_budget = float(
            SOGLIA_BASE
        )

    budget_corrente = round(
        float(
            st.session_state.get(
                "budget_asta_corrente",
                SOGLIA_BASE
            )
        ),
        2
    )

    if nuovo_budget == budget_corrente:
        return

    st.session_state[
        "budget_asta_corrente"
    ] = (
        salva_budget_asta(
            nuovo_budget
        )
    )


# ============================================================
# ECONOMIA
# ============================================================

def calcola_spesa_effettiva(
    valore_acquisti
):

    valore = round(
        float(
            valore_acquisti
            or 0
        ),
        2
    )

    if valore <= SOGLIA_BASE:

        return valore

    eccedenza = round(
        valore
        - SOGLIA_BASE,
        2
    )

    return round(
        SOGLIA_BASE
        + eccedenza * 3,
        2
    )


# ============================================================
# SNAPSHOT AUTOMATICI / RIPRISTINO
# Persistenti anche nella versione Cloud
# ============================================================

TABELLE_SNAPSHOT = [
    "giocatori",
    "costi_svincoli",
    "operazioni"
]


def pulisci_testo_snapshot(
    testo
):

    testo = str(
        testo
        or "OPERAZIONE"
    ).strip()

    caratteri = []

    for carattere in testo:

        if carattere.isalnum():

            caratteri.append(
                carattere
            )

        elif carattere in (
            " ",
            "-",
            "_"
        ):

            caratteri.append(
                "_"
            )

    risultato = "".join(
        caratteri
    )

    while "__" in risultato:

        risultato = (
            risultato.replace(
                "__",
                "_"
            )
        )

    return (
        risultato.strip("_")
        or "OPERAZIONE"
    )


def estrai_tabella_snapshot(
    conn,
    nome_tabella
):

    cur = conn.cursor()

    cur.execute(
        f"SELECT * FROM {nome_tabella}"
    )

    righe = cur.fetchall()

    colonne = [
        descrizione[0]
        for descrizione
        in cur.description
    ]

    return {
        "colonne":
            colonne,

        "righe":
            [
                list(
                    riga
                )
                for riga
                in righe
            ]
    }


def serializza_stato_database(
    conn
):

    contenuto = {
        "versione":
            1,

        "creato_il":
            datetime.now().isoformat(),

        "tabelle":
            {}
    }

    for nome_tabella in (
        TABELLE_SNAPSHOT
    ):

        contenuto[
            "tabelle"
        ][
            nome_tabella
        ] = estrai_tabella_snapshot(
            conn,
            nome_tabella
        )

    return json.dumps(
        contenuto,
        ensure_ascii=False
    )


def elimina_snapshot_eccessivi(
    conn
):

    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM snapshot_archivio
        ORDER BY id DESC
    """)

    ids = [
        riga[0]
        for riga
        in cur.fetchall()
    ]

    da_eliminare = ids[
        MAX_SNAPSHOT:
    ]

    for snapshot_id in (
        da_eliminare
    ):

        cur.execute("""
            DELETE FROM snapshot_archivio
            WHERE id = ?
        """, (
            snapshot_id,
        ))

    conn.commit()


def crea_snapshot_database(
    motivo="MANUALE"
):

    conn = get_connection()

    try:

        stato_json = (
            serializza_stato_database(
                conn
            )
        )

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO snapshot_archivio (
                motivo,
                contenuto_json,
                data_creazione
            )
            VALUES (
                ?, ?,
                CURRENT_TIMESTAMP
            )
        """, (
            pulisci_testo_snapshot(
                motivo
            ),
            stato_json
        ))

        conn.commit()

        elimina_snapshot_eccessivi(
            conn
        )

        try:
            elenco_snapshot.clear()
        except Exception:
            pass

        return True

    finally:

        chiudi_connessione(conn)


@st.cache_data(show_spinner=False)
def elenco_snapshot(
    profilo_cache
):

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                motivo,
                data_creazione

            FROM snapshot_archivio

            ORDER BY id DESC

            LIMIT ?
        """, (
            MAX_SNAPSHOT,
        ))

        righe = cur.fetchall()

        risultato = []

        for riga in righe:

            snapshot_id = (
                riga[0]
            )

            motivo = str(
                riga[1]
                or "SNAPSHOT"
            )

            data_raw = str(
                riga[2]
                or ""
            )

            data_testo = (
                data_raw
            )

            try:

                data_ora = (
                    datetime.fromisoformat(
                        data_raw.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                data_testo = (
                    data_ora.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                )

            except Exception:

                pass

            risultato.append({
                "id":
                    snapshot_id,

                "path":
                    snapshot_id,

                "file":
                    f"snapshot_{snapshot_id}",

                "data":
                    data_testo,

                "motivo":
                    motivo.replace(
                        "_",
                        " "
                    )
            })

        return risultato

    finally:

        chiudi_connessione(conn)


def ripristina_snapshot_database(
    snapshot_id
):

    # Prima salviamo sempre lo stato corrente.
    crea_snapshot_database(
        "PRIMA_DEL_RIPRISTINO"
    )

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute("""
            SELECT contenuto_json
            FROM snapshot_archivio
            WHERE id = ?
        """, (
            int(
                snapshot_id
            ),
        ))

        riga = cur.fetchone()

        if riga is None:

            raise FileNotFoundError(
                "Snapshot non trovato."
            )

        contenuto = json.loads(
            riga[0]
        )

        tabelle = contenuto.get(
            "tabelle",
            {}
        )

        # Svuotiamo prima le tabelle operative.
        # L'archivio snapshot NON viene cancellato.
        for nome_tabella in [
            "costi_svincoli",
            "operazioni",
            "giocatori"
        ]:

            cur.execute(
                f"DELETE FROM {nome_tabella}"
            )

        # Ripristino dei dati.
        for nome_tabella in (
            TABELLE_SNAPSHOT
        ):

            dati = tabelle.get(
                nome_tabella
            )

            if not dati:

                continue

            colonne = dati.get(
                "colonne",
                []
            )

            righe = dati.get(
                "righe",
                []
            )

            if (
                not colonne
                or not righe
            ):

                continue

            elenco_colonne = (
                ", ".join(
                    colonne
                )
            )

            placeholders = (
                ", ".join(
                    [
                        "?"
                        for _ in colonne
                    ]
                )
            )

            query = (
                f"INSERT INTO "
                f"{nome_tabella} "
                f"({elenco_colonne}) "
                f"VALUES "
                f"({placeholders})"
            )

            for valori in righe:

                cur.execute(
                    query,
                    tuple(
                        valori
                    )
                )

        conn.commit()

        invalida_cache_dati()

        return True

    finally:

        chiudi_connessione(conn)


def crea_backup_logico_bytes():

    conn = get_connection()

    try:

        contenuto = (
            serializza_stato_database(
                conn
            )
        )

        return contenuto.encode(
            "utf-8"
        )

    finally:

        chiudi_connessione(conn)


# ============================================================
# DATABASE
# ============================================================

TABELLE_SEPARATE_PER_PROFILO = [
    "giocatori",
    "costi_svincoli",
    "operazioni",
    "snapshot_archivio",
    "configurazione_app"
]


def _riscrivi_sql_per_profilo(
    sql
):

    testo = str(
        sql
    )

    if not SUFFIX_PROFILO:
        return testo

    # Sostituisce solo identificatori completi.
    # In questo modo tutto il codice esistente continua a usare
    # i nomi standard delle tabelle, ma GOSTOBAR lavora su copie
    # completamente separate.
    for nome_base in sorted(
        TABELLE_SEPARATE_PER_PROFILO,
        key=len,
        reverse=True
    ):

        testo = re.sub(
            rf"\b{re.escape(nome_base)}\b",
            nome_tabella_profilo(
                nome_base
            ),
            testo
        )

    return testo


class _CursorProfilo:

    def __init__(
        self,
        cursor
    ):

        self._cursor = cursor


    @property
    def description(
        self
    ):

        return self._cursor.description


    @property
    def lastrowid(
        self
    ):

        return getattr(
            self._cursor,
            "lastrowid",
            None
        )


    def execute(
        self,
        sql,
        parametri=()
    ):

        self._cursor.execute(
            _riscrivi_sql_per_profilo(
                sql
            ),
            parametri
        )

        return self


    def executemany(
        self,
        sql,
        seq_parametri
    ):

        self._cursor.executemany(
            _riscrivi_sql_per_profilo(
                sql
            ),
            seq_parametri
        )

        return self


    def fetchone(
        self
    ):

        return self._cursor.fetchone()


    def fetchall(
        self
    ):

        return self._cursor.fetchall()


    def __iter__(
        self
    ):

        return iter(
            self._cursor
        )


    def __getattr__(
        self,
        nome
    ):

        return getattr(
            self._cursor,
            nome
        )


class _ConnessioneProfilo:

    def __init__(
        self,
        connessione
    ):

        self._connessione = connessione


    def cursor(
        self
    ):

        return _CursorProfilo(
            self._connessione.cursor()
        )


    def execute(
        self,
        sql,
        parametri=()
    ):

        cursore = self.cursor()

        return cursore.execute(
            sql,
            parametri
        )


    def executemany(
        self,
        sql,
        seq_parametri
    ):

        cursore = self.cursor()

        return cursore.executemany(
            sql,
            seq_parametri
        )


    def commit(
        self
    ):

        return self._connessione.commit()


    def rollback(
        self
    ):

        return self._connessione.rollback()


    def close(
        self
    ):

        return self._connessione.close()


    def __enter__(
        self
    ):

        return self


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        if exc_type is None:

            try:
                self.commit()
            except Exception:
                pass

        return False


    def __getattr__(
        self,
        nome
    ):

        return getattr(
            self._connessione,
            nome
        )


def _get_raw_connection():

    if USA_DATABASE_CLOUD:

        try:

            import libsql

        except ImportError as errore:

            raise RuntimeError(
                "La modalità Cloud richiede il pacchetto libsql. "
                "Installa le dipendenze da requirements.txt."
            ) from errore

        chiave = "_turso_connessione_raw"

        conn = st.session_state.get(
            chiave
        )

        if conn is None:

            conn = libsql.connect(
                database=(
                    TURSO_DATABASE_URL
                ),
                auth_token=(
                    TURSO_AUTH_TOKEN
                )
            )

            st.session_state[
                chiave
            ] = conn

        return conn

    return sqlite3.connect(
        DB_PATH
    )


def get_connection():

    return _ConnessioneProfilo(
        _get_raw_connection()
    )

def chiudi_connessione(
    conn
):

    # In Cloud la connessione viene mantenuta viva per tutta
    # la sessione: evita handshake e riconnessioni ripetute.
    if USA_DATABASE_CLOUD:
        return

    try:
        conn.close()
    except Exception:
        pass


@st.cache_resource(show_spinner=False)
def inizializza_database(
    profilo_cache
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS giocatori (

            id INTEGER PRIMARY KEY,

            ruolo_classico TEXT,
            ruolo_mantra TEXT,

            nome TEXT NOT NULL,
            squadra TEXT,

            quotazione_attuale REAL,
            quotazione_iniziale REAL,
            differenza REAL,

            quotazione_attuale_mantra REAL,
            quotazione_iniziale_mantra REAL,
            differenza_mantra REAL,

            fvm REAL,
            fvm_mantra REAL,

            stato TEXT
                DEFAULT 'DISPONIBILE',

            prezzo_acquisto REAL
                DEFAULT NULL,

            ultimo_aggiornamento TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS costi_svincoli (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            operazione_id INTEGER,

            giocatore_id INTEGER,

            nome_giocatore TEXT,

            importo REAL NOT NULL,

            data_operazione TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS operazioni (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            tipo TEXT NOT NULL,

            giocatore_id INTEGER NOT NULL,

            nome_giocatore TEXT,

            stato_prima TEXT,

            prezzo_prima REAL,

            stato_dopo TEXT,

            prezzo_dopo REAL,

            costo_svincolo REAL
                DEFAULT 0,

            data_operazione TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_archivio (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            motivo TEXT NOT NULL,

            contenuto_json TEXT NOT NULL,

            data_creazione TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)


    cur.execute("""
        CREATE TABLE IF NOT EXISTS configurazione_app (

            chiave TEXT PRIMARY KEY,

            valore TEXT
        )
    """)


    # La cronologia viene gestita direttamente in Python.
    # Rimuoviamo l'eventuale trigger creato dalle release precedenti:
    # su Turso/libsql può generare ValueError durante alcuni ripristini.
    cur.execute("""
        DROP TRIGGER IF EXISTS trg_operazioni_post_insert
    """)

    colonne = {
        r[1]
        for r in cur.execute(
            "PRAGMA table_info(giocatori)"
        ).fetchall()
    }

    if "stato" not in colonne:

        cur.execute("""
            ALTER TABLE giocatori
            ADD COLUMN stato TEXT
            DEFAULT 'DISPONIBILE'
        """)

    if "prezzo_acquisto" not in colonne:

        cur.execute("""
            ALTER TABLE giocatori
            ADD COLUMN prezzo_acquisto REAL
            DEFAULT NULL
        """)

    cur.execute("""
        UPDATE giocatori

        SET stato = 'DISPONIBILE'

        WHERE stato IS NULL
           OR TRIM(stato) = ''
    """)

    conn.commit()
    chiudi_connessione(conn)

    # --------------------------------------------------------
    # PRIMA APERTURA DI GOSTOBAR
    # --------------------------------------------------------
    # Clona il listone di IBBINI IDIOTA ma NON il suo stato d'asta.
    # Quindi GOSTOBAR parte con tutti i giocatori DISPONIBILI,
    # rosa vuota, prezzi vuoti e cronologia vuota.
    if PROFILO_ATTIVO == "GOSTOBAR":

        raw_conn = _get_raw_connection()
        raw_cur = raw_conn.cursor()

        try:

            raw_cur.execute("""
                SELECT COUNT(*)
                FROM giocatori_gostobar
            """)

            quanti_gostobar = int(
                raw_cur.fetchone()[0]
                or 0
            )

            if quanti_gostobar == 0:

                raw_cur.execute("""
                    SELECT COUNT(*)
                    FROM giocatori
                """)

                quanti_base = int(
                    raw_cur.fetchone()[0]
                    or 0
                )

                if quanti_base > 0:

                    raw_cur.execute("""
                        INSERT INTO giocatori_gostobar (
                            id,
                            ruolo_classico,
                            ruolo_mantra,
                            nome,
                            squadra,
                            quotazione_attuale,
                            quotazione_iniziale,
                            differenza,
                            quotazione_attuale_mantra,
                            quotazione_iniziale_mantra,
                            differenza_mantra,
                            fvm,
                            fvm_mantra,
                            stato,
                            prezzo_acquisto,
                            ultimo_aggiornamento
                        )

                        SELECT
                            id,
                            ruolo_classico,
                            ruolo_mantra,
                            nome,
                            squadra,
                            quotazione_attuale,
                            quotazione_iniziale,
                            differenza,
                            quotazione_attuale_mantra,
                            quotazione_iniziale_mantra,
                            differenza_mantra,
                            fvm,
                            fvm_mantra,
                            'DISPONIBILE',
                            NULL,
                            CURRENT_TIMESTAMP

                        FROM giocatori
                    """)

                    raw_conn.commit()

        finally:

            if not USA_DATABASE_CLOUD:

                try:
                    raw_conn.close()
                except Exception:
                    pass



# ============================================================
# MULTILEGA 0.1 - DATABASE FOUNDATION
# ============================================================
#
# Questa release NON sostituisce ancora le tabelle legacy:
# l'app continua a funzionare esattamente come V82.
#
# Le nuove tabelle sono additive e preparano:
# UTENTE -> LEGA -> RUOLO -> SQUADRA -> ROSA
#
# La V82 congelata resta la baseline di sicurezza.
# ============================================================

MULTILEGA_SCHEMA_VERSION = "2.0"

LEGA_LEGACY_NOME = "FANTAELEGANZA 26/27"


def _ml_fetch_id(
    cur,
    query,
    parametri
):
    cur.execute(
        query,
        parametri
    )
    riga = cur.fetchone()

    if not riga:
        return None

    return int(
        riga[0]
    )


def inizializza_database_multilega():
    """
    Crea lo schema MULTILEGA senza alterare il funzionamento legacy.

    Le tabelle create qui NON rientrano in
    TABELLE_SEPARATE_PER_PROFILO: sono globali e condivise.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS multilega_meta (
                chiave TEXT PRIMARY KEY,
                valore TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password_hash TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS leagues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                stagione TEXT,
                modalita TEXT NOT NULL DEFAULT 'MANTRA',
                stato TEXT NOT NULL DEFAULT 'DRAFT',
                created_by_user_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                owner_user_id INTEGER,
                posizione INTEGER,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, nome)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS league_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                team_id INTEGER,
                is_admin INTEGER NOT NULL DEFAULT 0,
                is_auctioneer INTEGER NOT NULL DEFAULT 0,
                is_team_member INTEGER NOT NULL DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, user_id, team_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS league_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL UNIQUE,
                partecipanti INTEGER NOT NULL DEFAULT 10,
                max_giocatori INTEGER NOT NULL DEFAULT 30,
                min_portieri INTEGER NOT NULL DEFAULT 2,
                budget_iniziale REAL NOT NULL DEFAULT 500,
                incremento_minimo REAL NOT NULL DEFAULT 1,
                soglia_budget REAL NOT NULL DEFAULT 500,
                moltiplicatore_oltre_soglia REAL NOT NULL DEFAULT 3,
                tipo_asta TEXT NOT NULL DEFAULT 'CHIAMATA',
                fonte_listone TEXT NOT NULL DEFAULT 'Fantacalcio.it',
                regolamento_bloccato INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                budget_impostato REAL NOT NULL DEFAULT 500,
                valore_acquisti REAL NOT NULL DEFAULT 0,
                spesa_effettiva REAL NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, team_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS rosters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                prezzo_acquisto REAL,
                fonte TEXT NOT NULL DEFAULT 'LEGACY',
                assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, team_id, player_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS league_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                stato TEXT NOT NULL DEFAULT 'DISPONIBILE',
                assigned_team_id INTEGER,
                prezzo_assegnazione REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league_id, player_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                user_id INTEGER,
                team_id INTEGER,
                azione TEXT NOT NULL,
                entita TEXT,
                entita_id TEXT,
                dettagli_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            INSERT INTO multilega_meta (
                chiave,
                valore
            )
            VALUES (
                'schema_version',
                ?
            )
            ON CONFLICT(chiave)
            DO UPDATE SET
                valore = excluded.valore
        """, (
            MULTILEGA_SCHEMA_VERSION,
        ))

        conn.commit()

    finally:

        chiudi_connessione(
            conn
        )


def migra_profili_legacy_in_multilega():
    """
    Registra IBBINI IDIOTA e GOSTOBAR nel nuovo schema.

    Non cambia il comportamento dell'app:
    crea solamente la mappatura multilega necessaria
    alle release successive.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        # ----------------------------------------------------
        # UTENTI LEGACY
        # ----------------------------------------------------
        for username in PROFILI_APP:

            cur.execute("""
                INSERT INTO users (
                    username,
                    is_active
                )
                VALUES (?, 1)
                ON CONFLICT(username)
                DO UPDATE SET
                    is_active = 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                username,
            ))

        # ----------------------------------------------------
        # LEGA LEGACY
        # ----------------------------------------------------
        admin_id = _ml_fetch_id(
            cur,
            "SELECT id FROM users WHERE username = ?",
            (
                "IBBINI IDIOTA",
            )
        )

        cur.execute("""
            SELECT id
            FROM leagues
            WHERE nome = ?
            ORDER BY id
            LIMIT 1
        """, (
            LEGA_LEGACY_NOME,
        ))

        riga_lega = cur.fetchone()

        if riga_lega:

            league_id = int(
                riga_lega[0]
            )

        else:

            cur.execute("""
                INSERT INTO leagues (
                    nome,
                    stagione,
                    modalita,
                    stato,
                    created_by_user_id
                )
                VALUES (
                    ?,
                    '2026/27',
                    'MANTRA',
                    'LEGACY_MIGRATION',
                    ?
                )
            """, (
                LEGA_LEGACY_NOME,
                admin_id
            ))

            league_id = int(
                cur.lastrowid
            )

        # ----------------------------------------------------
        # REGOLAMENTO BASE
        # ----------------------------------------------------
        cur.execute("""
            INSERT INTO league_rules (
                league_id,
                partecipanti,
                max_giocatori,
                min_portieri,
                budget_iniziale,
                incremento_minimo,
                soglia_budget,
                moltiplicatore_oltre_soglia,
                tipo_asta,
                fonte_listone
            )
            VALUES (
                ?,
                2,
                30,
                2,
                500,
                1,
                500,
                3,
                'CHIAMATA',
                'Fantacalcio.it'
            )
            ON CONFLICT(league_id)
            DO NOTHING
        """, (
            league_id,
        ))

        # ----------------------------------------------------
        # SQUADRE + MEMBERSHIP
        # ----------------------------------------------------
        for posizione, username in enumerate(
            PROFILI_APP,
            start=1
        ):

            user_id = _ml_fetch_id(
                cur,
                "SELECT id FROM users WHERE username = ?",
                (
                    username,
                )
            )

            cur.execute("""
                INSERT INTO teams (
                    league_id,
                    nome,
                    owner_user_id,
                    posizione,
                    is_active
                )
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(league_id, nome)
                DO UPDATE SET
                    owner_user_id = excluded.owner_user_id,
                    posizione = excluded.posizione,
                    is_active = 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                league_id,
                username,
                user_id,
                posizione
            ))

            team_id = _ml_fetch_id(
                cur,
                """
                SELECT id
                FROM teams
                WHERE league_id = ?
                  AND nome = ?
                """,
                (
                    league_id,
                    username
                )
            )

            cur.execute("""
                INSERT INTO league_members (
                    league_id,
                    user_id,
                    team_id,
                    is_admin,
                    is_auctioneer,
                    is_team_member,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, 1, 1)
                ON CONFLICT(league_id, user_id, team_id)
                DO UPDATE SET
                    is_admin = excluded.is_admin,
                    is_auctioneer = excluded.is_auctioneer,
                    is_team_member = 1,
                    is_active = 1
            """, (
                league_id,
                user_id,
                team_id,
                1 if username == "IBBINI IDIOTA" else 0,
                1 if username == "IBBINI IDIOTA" else 0
            ))

        conn.commit()

        return league_id

    finally:

        chiudi_connessione(
            conn
        )


def sincronizza_legacy_in_multilega():
    """
    Copia nel nuovo schema una fotografia dei dati legacy correnti.

    In V83 il sistema legacy resta la fonte autorevole.
    Le nuove tabelle servono a verificare e preparare
    l'isolamento league_id/team_id.
    """

    league_id = migra_profili_legacy_in_multilega()

    raw_conn = _get_raw_connection()
    raw_cur = raw_conn.cursor()

    try:

        for username in PROFILI_APP:

            raw_cur.execute(
                "SELECT id FROM users WHERE username = ?",
                (
                    username,
                )
            )
            r_user = raw_cur.fetchone()

            if not r_user:
                continue

            user_id = int(
                r_user[0]
            )

            raw_cur.execute("""
                SELECT id
                FROM teams
                WHERE league_id = ?
                  AND nome = ?
            """, (
                league_id,
                username
            ))
            r_team = raw_cur.fetchone()

            if not r_team:
                continue

            team_id = int(
                r_team[0]
            )

            tabella_giocatori = (
                "giocatori"
                if username == "IBBINI IDIOTA"
                else "giocatori_gostobar"
            )

            tabella_config = (
                "configurazione_app"
                if username == "IBBINI IDIOTA"
                else "configurazione_app_gostobar"
            )

            # Budget legacy
            budget = 500.0

            try:

                raw_cur.execute(
                    f"""
                    SELECT valore
                    FROM {tabella_config}
                    WHERE chiave = 'budget_asta'
                    """
                )

                r_budget = raw_cur.fetchone()

                if r_budget and r_budget[0] not in (
                    None,
                    ""
                ):
                    budget = float(
                        r_budget[0]
                    )

            except Exception:
                budget = 500.0

            # Rosa legacy
            try:

                raw_cur.execute(
                    f"""
                    SELECT
                        id,
                        COALESCE(prezzo_acquisto, 0)
                    FROM {tabella_giocatori}
                    WHERE stato = 'MIO'
                    """
                )

                rosa_legacy = (
                    raw_cur.fetchall()
                    or []
                )

            except Exception:
                rosa_legacy = []

            # La fotografia viene ricostruita ad ogni avvio V83.
            raw_cur.execute("""
                DELETE FROM rosters
                WHERE league_id = ?
                  AND team_id = ?
                  AND fonte = 'LEGACY'
            """, (
                league_id,
                team_id
            ))

            valore_acquisti = 0.0

            for player_id, prezzo in rosa_legacy:

                prezzo = float(
                    prezzo
                    or 0
                )

                valore_acquisti += prezzo

                raw_cur.execute("""
                    INSERT INTO rosters (
                        league_id,
                        team_id,
                        player_id,
                        prezzo_acquisto,
                        fonte,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, 'LEGACY', CURRENT_TIMESTAMP)
                    ON CONFLICT(league_id, team_id, player_id)
                    DO UPDATE SET
                        prezzo_acquisto = excluded.prezzo_acquisto,
                        fonte = 'LEGACY',
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    league_id,
                    team_id,
                    int(
                        player_id
                    ),
                    prezzo
                ))

            raw_cur.execute("""
                INSERT INTO team_budgets (
                    league_id,
                    team_id,
                    budget_impostato,
                    valore_acquisti,
                    spesa_effettiva,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(league_id, team_id)
                DO UPDATE SET
                    budget_impostato = excluded.budget_impostato,
                    valore_acquisti = excluded.valore_acquisti,
                    spesa_effettiva = excluded.spesa_effettiva,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                league_id,
                team_id,
                budget,
                valore_acquisti,
                valore_acquisti
            ))

        raw_conn.commit()

        return league_id

    finally:

        if not USA_DATABASE_CLOUD:

            try:
                raw_conn.close()
            except Exception:
                pass


def imposta_contesto_multilega_sessione(
    league_id
):
    """
    Espone nel session_state il contesto multilega corrente.
    L'interfaccia V83 continua comunque a utilizzare il legacy.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            "SELECT id FROM users WHERE username = ?",
            (
                PROFILO_ATTIVO,
            )
        )
        r_user = cur.fetchone()

        cur.execute("""
            SELECT id
            FROM teams
            WHERE league_id = ?
              AND nome = ?
        """, (
            league_id,
            PROFILO_ATTIVO
        ))
        r_team = cur.fetchone()

        st.session_state[
            "ml_schema_version"
        ] = MULTILEGA_SCHEMA_VERSION

        st.session_state[
            "ml_league_id"
        ] = int(
            league_id
        )

        st.session_state[
            "ml_user_id"
        ] = (
            int(
                r_user[0]
            )
            if r_user
            else None
        )

        st.session_state[
            "ml_team_id"
        ] = (
            int(
                r_team[0]
            )
            if r_team
            else None
        )

    finally:

        chiudi_connessione(
            conn
        )




# ============================================================
# MULTILEGA 0.2 - ACCESSI UTENTE -> LEGA -> SQUADRA
# ============================================================

def elenca_accessi_multilega(
    username
):
    """
    Restituisce tutte le membership attive dell'utente.

    Un accesso è definito dalla relazione:
        user -> league_members -> league -> team

    I ruoli appartengono alla membership nella lega,
    non all'utente in senso assoluto.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                u.id,
                l.id,
                l.nome,
                COALESCE(l.stagione, ''),
                COALESCE(l.modalita, ''),
                COALESCE(l.stato, ''),
                t.id,
                COALESCE(t.nome, ''),
                lm.is_admin,
                lm.is_auctioneer,
                lm.is_team_member
            FROM users u

            JOIN league_members lm
              ON lm.user_id = u.id
             AND lm.is_active = 1

            JOIN leagues l
              ON l.id = lm.league_id

            LEFT JOIN teams t
              ON t.id = lm.team_id
             AND t.is_active = 1

            WHERE u.username = ?
              AND u.is_active = 1

            ORDER BY
                l.nome,
                t.posizione,
                t.nome
        """, (
            username,
        ))

        righe = (
            cur.fetchall()
            or []
        )

        accessi = []

        for riga in righe:

            (
                user_id,
                league_id,
                league_nome,
                stagione,
                modalita,
                league_stato,
                team_id,
                team_nome,
                is_admin,
                is_auctioneer,
                is_team_member
            ) = riga

            ruoli = []

            if int(is_admin or 0) == 1:
                ruoli.append(
                    "ADMIN"
                )

            if int(is_auctioneer or 0) == 1:
                ruoli.append(
                    "BANDITORE"
                )

            if int(is_team_member or 0) == 1:
                ruoli.append(
                    "SQUADRA"
                )

            accessi.append({
                "user_id":
                    int(user_id),

                "league_id":
                    int(league_id),

                "league_nome":
                    str(league_nome),

                "stagione":
                    str(stagione or ""),

                "modalita":
                    str(modalita or ""),

                "league_stato":
                    str(league_stato or ""),

                "team_id":
                    (
                        int(team_id)
                        if team_id is not None
                        else None
                    ),

                "team_nome":
                    str(team_nome or ""),

                "ruoli":
                    ruoli
            })

        return accessi

    finally:

        chiudi_connessione(
            conn
        )


def accesso_multilega_corrente():
    """
    Verifica che il contesto salvato in sessione appartenga davvero
    all'utente attivo. Nessun team_id viene accettato solo perché
    presente nel browser/session_state.
    """

    league_id = st.session_state.get(
        "ml_league_id"
    )

    team_id = st.session_state.get(
        "ml_team_id"
    )

    user_id = st.session_state.get(
        "ml_user_id"
    )

    if (
        league_id is None
        or user_id is None
    ):
        return None

    accessi = elenca_accessi_multilega(
        PROFILO_ATTIVO
    )

    for accesso in accessi:

        if (
            int(accesso["league_id"])
            == int(league_id)
            and int(accesso["user_id"])
            == int(user_id)
            and (
                accesso["team_id"]
                == team_id
            )
        ):

            return accesso

    return None


def applica_accesso_multilega(
    accesso
):
    """
    Imposta il contesto autorevole della lega selezionata.
    """

    st.session_state[
        "ml_schema_version"
    ] = MULTILEGA_SCHEMA_VERSION

    st.session_state[
        "ml_user_id"
    ] = int(
        accesso[
            "user_id"
        ]
    )

    st.session_state[
        "ml_league_id"
    ] = int(
        accesso[
            "league_id"
        ]
    )

    st.session_state[
        "ml_team_id"
    ] = (
        int(
            accesso[
                "team_id"
            ]
        )
        if accesso[
            "team_id"
        ] is not None
        else None
    )

    st.session_state[
        "ml_league_nome"
    ] = accesso[
        "league_nome"
    ]

    st.session_state[
        "ml_team_nome"
    ] = accesso[
        "team_nome"
    ]

    st.session_state[
        "ml_ruoli"
    ] = list(
        accesso[
            "ruoli"
        ]
    )

    st.session_state[
        "ml_stagione"
    ] = accesso[
        "stagione"
    ]

    st.session_state[
        "ml_modalita"
    ] = accesso[
        "modalita"
    ]


def azzera_contesto_multilega():
    """
    Torna alla schermata LE MIE LEGHE senza scollegare l'utente.
    """

    for chiave in [
        "ml_user_id",
        "ml_league_id",
        "ml_team_id",
        "ml_league_nome",
        "ml_team_nome",
        "ml_ruoli",
        "ml_stagione",
        "ml_modalita",
        "ml_accesso_validato",
        "ml_workspace_suffix",
        "ml_runtime_workspace_key"
    ]:

        st.session_state.pop(
            chiave,
            None
        )


def schermata_le_mie_leghe(
    accessi
):
    """
    Schermata MULTILEGA 0.2.

    È volutamente separata dall'interfaccia operativa:
    prima si identifica l'utente, poi si sceglie il contesto
    Lega/Squadra, soltanto dopo si entra in FANTAELEGANZA.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 1.4rem !important;
        }

        .ml02-wrap {
            max-width: 900px;
            margin: 0 auto;
        }

        .ml02-header {
            background:
                linear-gradient(
                    110deg,
                    #061f3a 0%,
                    #0b3158 100%
                );
            border: 2px solid #ffc21c;
            border-radius: 18px;
            padding: 22px 26px;
            margin-bottom: 20px;
            color: white;
        }

        .ml02-title {
            font-size: 28px;
            font-weight: 950;
            line-height: 1;
        }

        .ml02-title span {
            color: #ffc21c;
        }

        .ml02-user {
            margin-top: 8px;
            color: #cbd5e1;
            font-size: 14px;
        }

        .ml02-card {
            background: white;
            border: 1px solid #dbe3ec;
            border-radius: 14px;
            padding: 17px 19px;
            margin: 0 0 10px 0;
            box-shadow: 0 3px 12px rgba(15,23,42,.05);
        }

        .ml02-league {
            color: #071a2f;
            font-size: 19px;
            line-height: 1.1;
            font-weight: 950;
        }

        .ml02-meta {
            color: #64748b;
            font-size: 12px;
            margin-top: 5px;
        }

        .ml02-team {
            color: #071a2f;
            font-size: 14px;
            font-weight: 850;
            margin-top: 10px;
        }

        .ml02-role {
            display: inline-block;
            margin: 7px 5px 0 0;
            padding: 4px 8px;
            border-radius: 999px;
            background: #eef4fb;
            border: 1px solid #c9d9e9;
            color: #0b3158;
            font-size: 10px;
            font-weight: 900;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        (
            '<div class="ml02-wrap">'
            '<div class="ml02-header">'
            '<div class="ml02-title">'
            'FANTAELEGANZA <span>MULTILEGA</span>'
            '</div>'
            '<div class="ml02-user">'
            'Le mie leghe · '
            + html.escape(
                PROFILO_ATTIVO
            )
            + '</div>'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    if not accessi:

        st.error(
            "Questo utente non è associato ad alcuna lega attiva."
        )

        if st.button(
            "← TORNA ALLA SCELTA UTENTE",
            use_container_width=False,
            key="ml02_logout_senza_leghe"
        ):

            azzera_contesto_multilega()

            st.session_state.pop(
                "profilo_attivo",
                None
            )

            st.session_state.pop(
                "profilo_login_select",
                None
            )

            st.rerun()

        st.stop()

    for indice, accesso in enumerate(
        accessi
    ):

        ruoli_html = "".join(
            (
                '<span class="ml02-role">'
                + html.escape(
                    ruolo
                )
                + '</span>'
            )
            for ruolo in accesso[
                "ruoli"
            ]
        )

        team_testo = (
            accesso[
                "team_nome"
            ]
            or "Nessuna squadra associata"
        )

        stagione_modalita = " · ".join(
            [
                valore
                for valore in [
                    accesso[
                        "stagione"
                    ],
                    accesso[
                        "modalita"
                    ]
                ]
                if valore
            ]
        )

        col_card, col_enter = st.columns(
            [
                4.7,
                1.3
            ],
            vertical_alignment="center"
        )

        with col_card:

            st.markdown(
                (
                    '<div class="ml02-card">'
                    '<div class="ml02-league">'
                    + html.escape(
                        accesso[
                            "league_nome"
                        ]
                    )
                    + '</div>'
                    '<div class="ml02-meta">'
                    + html.escape(
                        stagione_modalita
                    )
                    + '</div>'
                    '<div class="ml02-team">'
                    'Squadra: '
                    + html.escape(
                        team_testo
                    )
                    + '</div>'
                    + ruoli_html
                    + '</div>'
                ),
                unsafe_allow_html=True
            )

        with col_enter:

            if st.button(
                "ENTRA",
                type="primary",
                use_container_width=True,
                key=(
                    "ml02_entra_"
                    + str(
                        accesso[
                            "league_id"
                        ]
                    )
                    + "_"
                    + str(
                        accesso[
                            "team_id"
                        ]
                    )
                )
            ):

                applica_accesso_multilega(
                    accesso
                )

                st.session_state[
                    "ml_accesso_validato"
                ] = dict(
                    accesso
                )

                st.session_state[
                    "pagina"
                ] = (
                    "DASHBOARD"
                    if accesso.get(
                        "team_id"
                    ) is not None
                    else "GESTIONE LEGA"
                )

                # Elimina soltanto cache operative che potrebbero
                # appartenere al contesto precedente.
                for chiave_sessione in list(
                    st.session_state.keys()
                ):

                    if (
                        chiave_sessione.startswith(
                            "_df_"
                        )
                        or chiave_sessione.startswith(
                            "_ultime_"
                        )
                        or chiave_sessione.startswith(
                            "_costi_"
                        )
                        or chiave_sessione.startswith(
                            "pdf_"
                        )
                    ):

                        st.session_state.pop(
                            chiave_sessione,
                            None
                        )

                st.rerun()

    st.markdown(
        "---"
    )

    if st.button(
        "← CAMBIA UTENTE",
        use_container_width=False,
        key="ml02_cambia_utente"
    ):

        azzera_contesto_multilega()

        st.session_state.pop(
            "profilo_attivo",
            None
        )

        st.session_state.pop(
            "profilo_login_select",
            None
        )

        st.rerun()

    st.caption(
        "MULTILEGA 0.2 · La lega e la squadra vengono determinate "
        "dalle membership registrate nel database."
    )

    st.stop()




# ============================================================
# MULTILEGA 0.3 - ADMIN LEGA
# ============================================================

def crea_lega_multilega(
    nome,
    stagione,
    modalita,
    partecipanti,
    max_giocatori,
    min_portieri,
    budget_iniziale,
    incremento_minimo,
    soglia_budget,
    moltiplicatore_oltre_soglia,
    tipo_asta,
    fonte_listone
):
    """
    Crea atomicamente:
    - league
    - league_rules
    - N squadre placeholder
    - membership ADMIN del creatore
    - audit log
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            "SELECT id FROM users WHERE username = ?",
            (
                PROFILO_ATTIVO,
            )
        )

        r_user = cur.fetchone()

        if not r_user:
            raise ValueError(
                "Utente multilega non trovato."
            )

        user_id = int(
            r_user[0]
        )

        cur.execute("""
            INSERT INTO leagues (
                nome,
                stagione,
                modalita,
                stato,
                created_by_user_id,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, 'DRAFT', ?,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """, (
            nome.strip(),
            stagione.strip(),
            modalita,
            user_id
        ))

        league_id = int(
            cur.lastrowid
        )

        cur.execute("""
            INSERT INTO league_rules (
                league_id,
                partecipanti,
                max_giocatori,
                min_portieri,
                budget_iniziale,
                incremento_minimo,
                soglia_budget,
                moltiplicatore_oltre_soglia,
                tipo_asta,
                fonte_listone,
                regolamento_bloccato,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            league_id,
            int(partecipanti),
            int(max_giocatori),
            int(min_portieri),
            float(budget_iniziale),
            float(incremento_minimo),
            float(soglia_budget),
            float(moltiplicatore_oltre_soglia),
            tipo_asta,
            fonte_listone.strip()
        ))

        # L'Admin inizialmente appartiene alla lega senza essere
        # obbligatoriamente proprietario di una squadra.
        cur.execute("""
            INSERT INTO league_members (
                league_id,
                user_id,
                team_id,
                is_admin,
                is_auctioneer,
                is_team_member,
                is_active,
                joined_at
            )
            VALUES (?, ?, NULL, 1, 0, 0, 1, CURRENT_TIMESTAMP)
        """, (
            league_id,
            user_id
        ))

        for posizione in range(
            1,
            int(partecipanti) + 1
        ):

            cur.execute("""
                INSERT INTO teams (
                    league_id,
                    nome,
                    owner_user_id,
                    posizione,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, NULL, ?, 1,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                league_id,
                f"Squadra {posizione}",
                posizione
            ))

        cur.execute("""
            INSERT INTO audit_log (
                league_id,
                user_id,
                team_id,
                azione,
                entita,
                entita_id,
                dettagli_json,
                created_at
            )
            VALUES (?, ?, NULL, 'LEAGUE_CREATED',
                    'LEAGUE', ?, ?, CURRENT_TIMESTAMP)
        """, (
            league_id,
            user_id,
            str(league_id),
            json.dumps(
                {
                    "nome":
                        nome.strip(),

                    "partecipanti":
                        int(partecipanti),

                    "budget":
                        float(budget_iniziale),

                    "modalita":
                        modalita
                },
                ensure_ascii=False
            )
        ))

        conn.commit()

        return league_id

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        chiudi_connessione(
            conn
        )



def invalida_cache_admin_multilega():
    for chiave in list(st.session_state.keys()):
        if chiave.startswith((
            "_ml16_admin_leghe_",
            "_ml16_admin_rules_",
            "_ml16_admin_teams_",
            "_ml16_admin_teamdetails_"
        )):
            st.session_state.pop(chiave, None)


def leghe_amministrate_multilega():
    """
    Elenco compatto delle leghe in cui l'utente corrente è ADMIN.
    Una sola query.
    """

    cache_key="_ml16_admin_leghe_"+str(st.session_state.get("auth_user_id",""))
    cached=st.session_state.get(cache_key)
    if isinstance(cached,list):
        return [dict(x) for x in cached]

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                l.id,
                l.nome,
                COALESCE(l.stagione, ''),
                COALESCE(l.modalita, ''),
                COALESCE(l.stato, ''),
                r.partecipanti,
                r.max_giocatori,
                r.min_portieri,
                r.budget_iniziale,
                r.incremento_minimo,
                r.soglia_budget,
                r.moltiplicatore_oltre_soglia,
                COALESCE(r.tipo_asta, ''),
                COALESCE(r.fonte_listone, ''),
                r.regolamento_bloccato,
                (
                    SELECT COUNT(*)
                    FROM teams t
                    WHERE t.league_id = l.id
                      AND t.is_active = 1
                ) AS squadre_attive
            FROM league_members lm

            JOIN users u
              ON u.id = lm.user_id

            JOIN leagues l
              ON l.id = lm.league_id

            JOIN league_rules r
              ON r.league_id = l.id

            WHERE u.username = ?
              AND lm.is_admin = 1
              AND lm.is_active = 1

            ORDER BY l.id DESC
        """, (
            PROFILO_ATTIVO,
        ))

        colonne = [
            "league_id",
            "nome",
            "stagione",
            "modalita",
            "stato",
            "partecipanti",
            "max_giocatori",
            "min_portieri",
            "budget_iniziale",
            "incremento_minimo",
            "soglia_budget",
            "moltiplicatore",
            "tipo_asta",
            "fonte_listone",
            "regolamento_bloccato",
            "squadre_attive"
        ]

        risultato = [
            dict(zip(colonne, riga))
            for riga in (cur.fetchall() or [])
        ]
        st.session_state[cache_key]=[dict(x) for x in risultato]
        return risultato

    finally:

        chiudi_connessione(
            conn
        )


def squadre_lega_multilega(
    league_id
):
    cache_key="_ml16_admin_teams_"+str(int(league_id))
    cached=st.session_state.get(cache_key)
    if isinstance(cached,list):
        return [dict(x) for x in cached]

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                nome,
                posizione,
                owner_user_id
            FROM teams
            WHERE league_id = ?
              AND is_active = 1
            ORDER BY posizione, id
        """, (
            int(league_id),
        ))

        risultato = [
            {
                "team_id": int(r[0]),
                "nome": str(r[1]),
                "posizione": int(r[2] or 0),
                "owner_user_id": int(r[3]) if r[3] is not None else None
            }
            for r in (cur.fetchall() or [])
        ]
        st.session_state[cache_key]=[dict(x) for x in risultato]
        return risultato

    finally:

        chiudi_connessione(
            conn
        )



def dettagli_squadre_lega_multilega(league_id):
    """
    Restituisce squadre, proprietari e ruoli correnti.
    I ruoli sono sempre letti dal DB, non dalla sessione browser.
    """
    league_id = int(league_id)
    cache_key="_ml16_admin_teamdetails_"+str(league_id)
    cached=st.session_state.get(cache_key)
    if isinstance(cached,list):
        return [dict(x) for x in cached]

    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                t.id,
                t.nome,
                t.posizione,
                t.owner_user_id,
                COALESCE(u.username, ''),
                COALESCE(lm.is_admin, 0),
                COALESCE(lm.is_auctioneer, 0),
                COALESCE(lm.is_team_member, 1),
                COALESCE(lm.is_active, 1)
            FROM teams t
            LEFT JOIN users u
              ON u.id = t.owner_user_id
            LEFT JOIN league_members lm
              ON lm.league_id = t.league_id
             AND lm.team_id = t.id
             AND lm.user_id = t.owner_user_id
            WHERE t.league_id = ?
              AND t.is_active = 1
            ORDER BY t.posizione, t.id
        """, (league_id,))
        risultato = [
            {
                "team_id": int(r[0]),
                "nome": str(r[1] or ""),
                "posizione": int(r[2] or 0),
                "owner_user_id": int(r[3]) if r[3] is not None else None,
                "username": str(r[4] or ""),
                "is_admin": bool(r[5]),
                "is_auctioneer": bool(r[6]),
                "is_team_member": bool(r[7]),
                "is_active": bool(r[8]),
            }
            for r in (cur.fetchall() or [])
        ]
        st.session_state[cache_key]=[dict(x) for x in risultato]
        return risultato
    finally:
        _portal_close(conn)


def aggiorna_ruoli_squadra_multilega(league_id, team_id, is_admin, is_auctioneer):
    """
    Modifica i ruoli ADMIN/BANDITORE della squadra.
    TEAM resta sempre attivo per le squadre operative.
    Non consente di eliminare l'ultimo Admin della lega.
    """
    league_id = int(league_id)
    team_id = int(team_id)
    current_admin = int(st.session_state.get("auth_user_id") or 0)

    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM league_members
            WHERE league_id = ?
              AND user_id = ?
              AND is_admin = 1
              AND is_active = 1
        """, (league_id, current_admin))
        if int(cur.fetchone()[0] or 0) == 0:
            raise PermissionError("Operazione riservata all'Admin della lega.")

        cur.execute("""
            SELECT t.owner_user_id, t.nome, COALESCE(lm.is_admin,0), COALESCE(lm.is_auctioneer,0)
            FROM teams t
            LEFT JOIN league_members lm
              ON lm.league_id=t.league_id
             AND lm.team_id=t.id
             AND lm.user_id=t.owner_user_id
            WHERE t.league_id=? AND t.id=? AND t.is_active=1
            LIMIT 1
        """, (league_id, team_id))
        r = cur.fetchone()
        if not r:
            raise ValueError("Squadra non trovata.")

        owner_user_id = int(r[0]) if r[0] is not None else None
        nome = str(r[1] or "")
        old_admin = bool(r[2])
        old_auctioneer = bool(r[3])

        if owner_user_id is None:
            raise ValueError("La squadra non ha un account proprietario associato.")

        if old_admin and not bool(is_admin):
            cur.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM league_members
                WHERE league_id=?
                  AND is_admin=1
                  AND is_active=1
                  AND user_id<>?
            """, (league_id, owner_user_id))
            if int(cur.fetchone()[0] or 0) == 0:
                raise ValueError(
                    "Non puoi togliere il ruolo Admin all'unico Admin della lega. "
                    "Assegna prima il ruolo Admin a un'altra squadra."
                )

        cur.execute("""
            UPDATE league_members
            SET is_admin=?,
                is_auctioneer=?,
                is_team_member=1,
                is_active=1
            WHERE league_id=?
              AND team_id=?
              AND user_id=?
        """, (
            1 if is_admin else 0,
            1 if is_auctioneer else 0,
            league_id,
            team_id,
            owner_user_id
        ))

        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO league_members
                (league_id,user_id,team_id,is_admin,is_auctioneer,is_team_member,is_active,joined_at)
                VALUES (?,?,?,?,?,1,1,CURRENT_TIMESTAMP)
            """, (
                league_id,
                owner_user_id,
                team_id,
                1 if is_admin else 0,
                1 if is_auctioneer else 0
            ))

        cur.execute("""
            INSERT INTO audit_log
            (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
            VALUES (?,?,?,'ROLES_UPDATED','TEAM',?,?,CURRENT_TIMESTAMP)
        """, (
            league_id,
            current_admin,
            team_id,
            str(team_id),
            json.dumps({
                "team": nome,
                "admin_prima": old_admin,
                "admin_dopo": bool(is_admin),
                "banditore_prima": old_auctioneer,
                "banditore_dopo": bool(is_auctioneer)
            }, ensure_ascii=False)
        ))

        conn.commit()
        invalida_cache_admin_multilega()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        _portal_close(conn)


def reset_password_squadra_multilega(league_id, team_id, nuova_password):
    """
    Reset amministrativo: l'Admin imposta una nuova password.
    La password non viene mai salvata nell'audit.
    """
    league_id = int(league_id)
    team_id = int(team_id)
    nuova_password = str(nuova_password)

    if len(nuova_password) < 8:
        raise ValueError("La nuova password deve contenere almeno 8 caratteri.")

    current_admin = int(st.session_state.get("auth_user_id") or 0)
    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM league_members
            WHERE league_id=? AND user_id=? AND is_admin=1 AND is_active=1
        """, (league_id, current_admin))
        if int(cur.fetchone()[0] or 0) == 0:
            raise PermissionError("Operazione riservata all'Admin della lega.")

        cur.execute("""
            SELECT t.owner_user_id, t.nome, COALESCE(u.username,'')
            FROM teams t
            LEFT JOIN users u ON u.id=t.owner_user_id
            WHERE t.league_id=? AND t.id=? AND t.is_active=1
            LIMIT 1
        """, (league_id, team_id))
        r = cur.fetchone()
        if not r or r[0] is None:
            raise ValueError("Account della squadra non trovato.")

        owner_user_id = int(r[0])
        nome = str(r[1] or "")
        username = str(r[2] or "")

        cur.execute("""
            UPDATE users
            SET password_hash=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=? AND is_active=1
        """, (password_hash_sicuro(nuova_password), owner_user_id))

        cur.execute("""
            INSERT INTO audit_log
            (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
            VALUES (?,?,?,'PASSWORD_RESET','USER',?,?,CURRENT_TIMESTAMP)
        """, (
            league_id,
            current_admin,
            team_id,
            str(owner_user_id),
            json.dumps({"team": nome, "username": username}, ensure_ascii=False)
        ))
        conn.commit()
        invalida_cache_admin_multilega()
        return username
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        _portal_close(conn)


def collega_utente_esistente_lega(
    league_id, username, nome_squadra, is_admin=False, is_auctioneer=False
):
    """
    Collega alla lega un account globale già esistente creando per esso
    una nuova squadra. Non modifica password o dati dell'account.
    """
    league_id = int(league_id)
    username = str(username).strip()
    nome_squadra = str(nome_squadra).strip()

    if not username:
        raise ValueError("Inserisci lo username dell'account esistente.")
    if not nome_squadra:
        raise ValueError("Inserisci il nome della squadra.")

    current_admin = int(st.session_state.get("auth_user_id") or 0)
    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*) FROM league_members
            WHERE league_id=? AND user_id=? AND is_admin=1 AND is_active=1
        """, (league_id, current_admin))
        if int(cur.fetchone()[0] or 0) == 0:
            raise PermissionError("Operazione riservata all'Admin della lega.")

        cur.execute("""
            SELECT id, username FROM users
            WHERE LOWER(username)=LOWER(?) AND is_active=1
            LIMIT 1
        """, (username,))
        r = cur.fetchone()
        if not r:
            raise ValueError("Account esistente non trovato.")
        user_id = int(r[0])
        username_db = str(r[1])

        cur.execute("""
            SELECT COUNT(*) FROM league_members
            WHERE league_id=? AND user_id=? AND is_active=1
        """, (league_id, user_id))
        if int(cur.fetchone()[0] or 0) > 0:
            raise ValueError("Questo account è già associato alla lega.")

        cur.execute("""
            SELECT COUNT(*) FROM teams
            WHERE league_id=? AND LOWER(nome)=LOWER(?) AND is_active=1
        """, (league_id, nome_squadra))
        if int(cur.fetchone()[0] or 0) > 0:
            raise ValueError("Esiste già una squadra con questo nome nella lega.")

        cur.execute("""
            SELECT COALESCE(MAX(posizione),0)+1
            FROM teams WHERE league_id=?
        """, (league_id,))
        posizione = int(cur.fetchone()[0] or 1)

        cur.execute("""
            INSERT INTO teams
            (league_id,nome,owner_user_id,posizione,is_active,created_at,updated_at)
            VALUES (?,?,?,?,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
        """, (league_id, nome_squadra, user_id, posizione))
        team_id = int(cur.lastrowid)

        cur.execute("""
            INSERT INTO league_members
            (league_id,user_id,team_id,is_admin,is_auctioneer,is_team_member,is_active,joined_at)
            VALUES (?,?,?,?,?,1,1,CURRENT_TIMESTAMP)
        """, (
            league_id, user_id, team_id,
            1 if is_admin else 0,
            1 if is_auctioneer else 0
        ))

        cur.execute("""
            UPDATE league_rules
            SET partecipanti=(
                SELECT COUNT(*) FROM teams
                WHERE league_id=? AND is_active=1
            ),
            updated_at=CURRENT_TIMESTAMP
            WHERE league_id=?
        """, (league_id, league_id))

        cur.execute("""
            INSERT INTO audit_log
            (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
            VALUES (?,?,?,'EXISTING_USER_LINKED','TEAM',?,?,CURRENT_TIMESTAMP)
        """, (
            league_id,
            current_admin,
            team_id,
            str(team_id),
            json.dumps({
                "username": username_db,
                "team": nome_squadra,
                "admin": bool(is_admin),
                "auctioneer": bool(is_auctioneer)
            }, ensure_ascii=False)
        ))

        conn.commit()
        invalida_cache_admin_multilega()
        return team_id
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        _portal_close(conn)


STATI_LEGA_AMMESSI = [
    "DRAFT",
    "CONFIGURAZIONE",
    "PRONTA",
    "ASTA",
    "CHIUSA"
]


def aggiorna_stato_lega_multilega(league_id, nuovo_stato):
    league_id = int(league_id)
    nuovo_stato = str(nuovo_stato).strip().upper()
    if nuovo_stato not in STATI_LEGA_AMMESSI:
        raise ValueError("Stato lega non valido.")

    current_admin = int(st.session_state.get("auth_user_id") or 0)
    conn = _portal_raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*) FROM league_members
            WHERE league_id=? AND user_id=? AND is_admin=1 AND is_active=1
        """, (league_id, current_admin))
        if int(cur.fetchone()[0] or 0) == 0:
            raise PermissionError("Operazione riservata all'Admin della lega.")

        cur.execute("SELECT stato FROM leagues WHERE id=? LIMIT 1", (league_id,))
        r = cur.fetchone()
        if not r:
            raise ValueError("Lega non trovata.")
        stato_prima = str(r[0] or "")

        cur.execute("""
            UPDATE leagues SET stato=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (nuovo_stato, league_id))

        cur.execute("""
            INSERT INTO audit_log
            (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
            VALUES (?,?,NULL,'LEAGUE_STATUS_UPDATED','LEAGUE',?,?,CURRENT_TIMESTAMP)
        """, (
            league_id,
            current_admin,
            str(league_id),
            json.dumps({"prima": stato_prima, "dopo": nuovo_stato}, ensure_ascii=False)
        ))
        conn.commit()
        invalida_cache_admin_multilega()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        _portal_close(conn)


def rinomina_squadra_multilega(
    league_id,
    team_id,
    nuovo_nome
):
    nuovo_nome = nuovo_nome.strip()

    if not nuovo_nome:
        raise ValueError(
            "Il nome squadra non può essere vuoto."
        )

    conn = get_connection()
    cur = conn.cursor()

    try:

        # Autorizzazione server-side: utente corrente deve essere Admin.
        cur.execute("""
            SELECT COUNT(*)
            FROM league_members lm
            JOIN users u
              ON u.id = lm.user_id
            WHERE lm.league_id = ?
              AND u.username = ?
              AND lm.is_admin = 1
              AND lm.is_active = 1
        """, (
            int(league_id),
            PROFILO_ATTIVO
        ))

        autorizzato = int(
            cur.fetchone()[0]
            or 0
        ) > 0

        if not autorizzato:
            raise PermissionError(
                "Operazione riservata all'Admin della lega."
            )

        cur.execute("""
            UPDATE teams
            SET nome = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND league_id = ?
        """, (
            nuovo_nome,
            int(team_id),
            int(league_id)
        ))

        if cur.rowcount == 0:
            raise ValueError(
                "Squadra non trovata."
            )

        conn.commit()
        invalida_cache_admin_multilega()

    finally:

        chiudi_connessione(
            conn
        )




def aggiungi_squadra_multilega(league_id, username, password, is_admin=False, is_auctioneer=False):
    league_id=int(league_id)
    username=str(username).strip()
    password=str(password)
    if not username:
        raise ValueError("Inserisci il nome squadra / username.")
    if len(password)<8:
        raise ValueError("La password iniziale deve contenere almeno 8 caratteri.")

    user_admin=int(st.session_state.get("auth_user_id"))
    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        cur.execute("""SELECT COUNT(*) FROM league_members
                       WHERE league_id=? AND user_id=? AND is_admin=1 AND is_active=1""",
                    (league_id,user_admin))
        if int(cur.fetchone()[0] or 0)==0:
            raise PermissionError("Operazione riservata all'Admin della lega.")

        cur.execute("SELECT id FROM users WHERE LOWER(username)=LOWER(?) LIMIT 1",(username,))
        if cur.fetchone():
            raise ValueError("Questo username è già utilizzato. Usa un nome squadra diverso.")

        cur.execute("SELECT COALESCE(MAX(posizione),0)+1 FROM teams WHERE league_id=?",(league_id,))
        posizione=int(cur.fetchone()[0] or 1)

        cur.execute("""INSERT INTO users
                       (username,password_hash,is_active,created_at,updated_at)
                       VALUES (?,?,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)""",
                    (username,password_hash_sicuro(password)))
        new_user_id=int(cur.lastrowid)

        cur.execute("""INSERT INTO teams
                       (league_id,nome,owner_user_id,posizione,is_active,created_at,updated_at)
                       VALUES (?,?,?,?,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)""",
                    (league_id,username,new_user_id,posizione))
        team_id=int(cur.lastrowid)

        cur.execute("""INSERT INTO league_members
                       (league_id,user_id,team_id,is_admin,is_auctioneer,is_team_member,is_active,joined_at)
                       VALUES (?,?,?,?,?,1,1,CURRENT_TIMESTAMP)""",
                    (league_id,new_user_id,team_id,1 if is_admin else 0,1 if is_auctioneer else 0))

        # Mantiene il numero partecipanti coerente con le squadre attive.
        cur.execute("""UPDATE league_rules
                       SET partecipanti=(SELECT COUNT(*) FROM teams
                                         WHERE league_id=? AND is_active=1),
                           updated_at=CURRENT_TIMESTAMP
                       WHERE league_id=?""",(league_id,league_id))

        cur.execute("""INSERT INTO audit_log
                       (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
                       VALUES (?,?,?,'TEAM_ADDED','TEAM',?,?,CURRENT_TIMESTAMP)""",
                    (league_id,user_admin,team_id,str(team_id),
                     json.dumps({"username":username,"admin":bool(is_admin),
                                 "auctioneer":bool(is_auctioneer)},ensure_ascii=False)))
        conn.commit()
        invalida_cache_admin_multilega()
        return team_id
    except Exception:
        try: conn.rollback()
        except Exception: pass
        raise
    finally:
        _portal_close(conn)


def rimuovi_squadra_multilega(league_id, team_id):
    league_id=int(league_id); team_id=int(team_id)
    user_admin=int(st.session_state.get("auth_user_id"))
    conn=_portal_raw_connection(); cur=conn.cursor()
    try:
        cur.execute("""SELECT COUNT(*) FROM league_members
                       WHERE league_id=? AND user_id=? AND is_admin=1 AND is_active=1""",
                    (league_id,user_admin))
        if int(cur.fetchone()[0] or 0)==0:
            raise PermissionError("Operazione riservata all'Admin della lega.")

        cur.execute("""SELECT nome,owner_user_id FROM teams
                       WHERE id=? AND league_id=? AND is_active=1 LIMIT 1""",(team_id,league_id))
        r=cur.fetchone()
        if not r: raise ValueError("Squadra non trovata.")
        nome=str(r[0] or "")
        owner_user_id=int(r[1]) if r[1] is not None else None

        # Impedisce di lasciare la lega senza alcun Admin.
        if owner_user_id is not None:
            cur.execute("""SELECT is_admin FROM league_members
                           WHERE league_id=? AND team_id=? AND user_id=? AND is_active=1 LIMIT 1""",
                        (league_id,team_id,owner_user_id))
            m=cur.fetchone()
            if m and int(m[0] or 0)==1:
                cur.execute("""SELECT COUNT(DISTINCT user_id) FROM league_members
                               WHERE league_id=? AND is_admin=1 AND is_active=1
                                 AND user_id<>?""",(league_id,owner_user_id))
                if int(cur.fetchone()[0] or 0)==0:
                    raise ValueError("Non puoi rimuovere l'unico Admin della lega. Assegna prima il ruolo Admin a un'altra squadra.")

        # Pulisce dati team-scoped presenti nello schema.
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        presenti={str(x[0]) for x in cur.fetchall()}
        for tabella in ["bids","assignments","player_evaluations","iqr_profiles","rosters","team_budgets"]:
            if tabella not in presenti: continue
            cur.execute(f"PRAGMA table_info({tabella})")
            cols={str(x[1]) for x in cur.fetchall()}
            if "league_id" in cols and "team_id" in cols:
                cur.execute(f"DELETE FROM {tabella} WHERE league_id=? AND team_id=?",(league_id,team_id))

        cur.execute("DELETE FROM league_members WHERE league_id=? AND team_id=?",(league_id,team_id))
        cur.execute("DELETE FROM teams WHERE league_id=? AND id=?",(league_id,team_id))

        cur.execute("""UPDATE league_rules
                       SET partecipanti=(SELECT COUNT(*) FROM teams
                                         WHERE league_id=? AND is_active=1),
                           updated_at=CURRENT_TIMESTAMP
                       WHERE league_id=?""",(league_id,league_id))

        cur.execute("""INSERT INTO audit_log
                       (league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at)
                       VALUES (?,?,NULL,'TEAM_REMOVED','TEAM',?,?,CURRENT_TIMESTAMP)""",
                    (league_id,user_admin,str(team_id),
                     json.dumps({"nome":nome},ensure_ascii=False)))
        conn.commit()
        invalida_cache_admin_multilega()
        return nome
    except Exception:
        try: conn.rollback()
        except Exception: pass
        raise
    finally:
        _portal_close(conn)



def elimina_lega_multilega(
    league_id
):
    """
    Elimina definitivamente una lega e tutti i dati ad essa collegati.

    Sicurezza:
    - l'utente autenticato deve essere ADMIN attivo della lega;
    - gli account USERS globali NON vengono eliminati;
    - la cancellazione è transazionale;
    - supporta anche tabelle multilega future se già presenti.
    """

    league_id = int(
        league_id
    )

    user_id = int(
        st.session_state.get(
            "auth_user_id"
        )
    )

    conn = _portal_raw_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                l.nome
            FROM leagues l
            JOIN league_members lm
              ON lm.league_id = l.id
            WHERE l.id = ?
              AND lm.user_id = ?
              AND lm.is_admin = 1
              AND lm.is_active = 1
            LIMIT 1
        """, (
            league_id,
            user_id
        ))

        riga = cur.fetchone()

        if not riga:
            raise PermissionError(
                "Non sei autorizzato a eliminare questa lega."
            )

        nome_lega = str(
            riga[0]
            or ""
        )

        # Rileva le tabelle realmente presenti.
        cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """)

        tabelle_presenti = {
            str(
                r[0]
            )
            for r in cur.fetchall()
        }

        # Prima le tabelle figlie, poi la lega.
        # L'elenco comprende anche le strutture previste per
        # le prossime fasi dell'asta live.
        tabelle_legate = [
            "bids",
            "assignments",
            "auction_lots",
            "auction_sessions",
            "player_evaluations",
            "iqr_profiles",
            "rosters",
            "team_budgets",
            "league_players",
            "league_members",
            "teams",
            "league_rules",
            "audit_log",
        ]

        for tabella in tabelle_legate:

            if tabella not in tabelle_presenti:
                continue

            cur.execute(
                f"PRAGMA table_info({tabella})"
            )

            colonne = {
                str(
                    r[1]
                )
                for r in cur.fetchall()
            }

            if "league_id" in colonne:

                cur.execute(
                    f"DELETE FROM {tabella} WHERE league_id = ?",
                    (
                        league_id,
                    )
                )

        cur.execute("""
            DELETE FROM leagues
            WHERE id = ?
        """, (
            league_id,
        ))

        conn.commit()
        invalida_cache_admin_multilega()

        return nome_lega

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        _portal_close(
            conn
        )



def render_admin_multilega():
    """
    MULTILEGA 0.3:
    creazione lega, regolamento e squadre.
    """

    if "ADMIN" not in RUOLI_ATTIVI:

        st.error(
            "Questa sezione è riservata agli amministratori della lega."
        )
        return

    st.subheader(
        "⚙️ Gestione lega"
    )

    st.caption(
        "MULTILEGA 0.5 · La creazione di nuove leghe è stata spostata "
        "nel portale iniziale. Qui l'Admin gestisce le leghe esistenti."
    )

    tab_nuova, tab_esistenti = st.tabs(
        [
            "ℹ️ Creazione lega",
            "🏆 Le mie leghe"
        ]
    )

    with tab_nuova:

        st.info(
            "Per creare una nuova lega esci dall'account e usa "
            "«CREA LA TUA LEGA» nella schermata iniziale."
        )

        st.markdown(
            "<div style='display:none'>",
            unsafe_allow_html=True
        )


        with st.form(
            "ml03_crea_lega",
            clear_on_submit=False
        ):

            c1, c2, c3 = st.columns(3)

            with c1:

                nome = st.text_input(
                    "Nome lega",
                    value="FANTAELEGANZA 26/27"
                )

                stagione = st.text_input(
                    "Stagione",
                    value="2026/27"
                )

                modalita = st.selectbox(
                    "Modalità",
                    [
                        "MANTRA",
                        "CLASSIC"
                    ],
                    index=0
                )

                partecipanti = st.number_input(
                    "Partecipanti",
                    min_value=2,
                    max_value=30,
                    value=10,
                    step=1
                )

            with c2:

                max_giocatori = st.number_input(
                    "Rosa massima",
                    min_value=1,
                    max_value=60,
                    value=30,
                    step=1
                )

                min_portieri = st.number_input(
                    "Portieri minimi",
                    min_value=0,
                    max_value=10,
                    value=2,
                    step=1
                )

                budget_iniziale = st.number_input(
                    "Budget iniziale",
                    min_value=1.0,
                    max_value=10000.0,
                    value=500.0,
                    step=10.0
                )

                incremento_minimo = st.number_input(
                    "Incremento minimo asta",
                    min_value=0.1,
                    max_value=100.0,
                    value=1.0,
                    step=0.5
                )

            with c3:

                soglia_budget = st.number_input(
                    "Soglia budget",
                    min_value=0.0,
                    max_value=10000.0,
                    value=500.0,
                    step=10.0
                )

                moltiplicatore = st.number_input(
                    "Moltiplicatore oltre soglia",
                    min_value=1,
                    max_value=10,
                    value=1,
                    step=1,
                    format="%d"
                )

                tipo_asta = st.selectbox(
                    "Tipologia asta",
                    TIPI_ASTA_FANTA_LIVE,
                    index=0
                )

                fonte_listone = st.text_input(
                    "Fonte listone",
                    value="Fantacalcio.it"
                )

            crea = st.form_submit_button(
                "CREA LEGA",
                type="primary",
                use_container_width=True
            )

            if crea:

                if not nome.strip():

                    st.error(
                        "Inserisci il nome della lega."
                    )

                elif int(min_portieri) > int(max_giocatori):

                    st.error(
                        "I portieri minimi non possono superare "
                        "la dimensione massima della rosa."
                    )

                else:

                    try:

                        nuova_lega_id = (
                            crea_lega_multilega(
                                nome,
                                stagione,
                                modalita,
                                partecipanti,
                                max_giocatori,
                                min_portieri,
                                budget_iniziale,
                                incremento_minimo,
                                soglia_budget,
                                moltiplicatore,
                                tipo_asta,
                                fonte_listone
                            )
                        )

                        st.session_state[
                            "ml03_lega_creata"
                        ] = (
                            f"Lega creata correttamente "
                            f"(ID {nuova_lega_id}). "
                            f"Sono state predisposte "
                            f"{int(partecipanti)} squadre."
                        )

                        # Gli accessi vanno riletti perché ora esiste
                        # una nuova membership ADMIN.
                        st.session_state.pop(
                            "ml_accesso_validato",
                            None
                        )

                        st.rerun()

                    except Exception as errore:

                        st.error(
                            f"Errore durante la creazione della lega: {errore}"
                        )

        if "ml03_lega_creata" in st.session_state:

            st.success(
                st.session_state.pop(
                    "ml03_lega_creata"
                )
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    with tab_esistenti:

        if "ml15_admin_message" in st.session_state:
            st.success(st.session_state.pop("ml15_admin_message"))

        if "ml09_team_message" in st.session_state:
            st.success(st.session_state.pop("ml09_team_message"))

        if "ml08_lega_eliminata" in st.session_state:

            st.success(
                st.session_state.pop(
                    "ml08_lega_eliminata"
                )
            )

        try:

            leghe = (
                leghe_amministrate_multilega()
            )

        except Exception as errore:

            st.error(
                f"Impossibile leggere le leghe: {errore}"
            )
            return

        if not leghe:

            st.info(
                "Non amministri ancora nessuna lega."
            )
            return

        for lega in leghe:

            with st.expander(
                (
                    f"🏆 {lega['nome']} "
                    f"· {lega['stagione']} "
                    f"· {int(lega['squadre_attive'])} squadre"
                ),
                expanded=(
                    int(
                        lega[
                            "league_id"
                        ]
                    )
                    == int(
                        st.session_state.get(
                            "ml_league_id",
                            -1
                        )
                    )
                )
            ):

                r1, r2, r3, r4 = st.columns(4)

                r1.metric(
                    "Partecipanti",
                    int(
                        lega[
                            "partecipanti"
                        ]
                    )
                )

                r2.metric(
                    "Rosa",
                    int(
                        lega[
                            "max_giocatori"
                        ]
                    )
                )

                r3.metric(
                    "Budget",
                    formatta_crediti(
                        lega[
                            "budget_iniziale"
                        ]
                    )
                )

                r4.metric(
                    "Incremento",
                    formatta_crediti(
                        lega[
                            "incremento_minimo"
                        ]
                    )
                )

                st.caption(
                    f"{lega['modalita']} · "
                    f"Asta {lega['tipo_asta']} · "
                    f"Listone {lega['fonte_listone']} · "
                    f"Oltre soglia ×{lega['moltiplicatore']}"
                )

                stato_corrente = str(lega.get("stato") or "DRAFT").upper()
                if stato_corrente not in STATI_LEGA_AMMESSI:
                    stato_corrente = "DRAFT"

                s1, s2 = st.columns([3, 1], vertical_alignment="bottom")
                with s1:
                    nuovo_stato_lega = st.selectbox(
                        "Stato lega",
                        STATI_LEGA_AMMESSI,
                        index=STATI_LEGA_AMMESSI.index(stato_corrente),
                        key="ml15_status_"+str(lega["league_id"])
                    )
                with s2:
                    if st.button(
                        "SALVA STATO",
                        key="ml15_status_save_"+str(lega["league_id"]),
                        use_container_width=True
                    ):
                        try:
                            aggiorna_stato_lega_multilega(
                                lega["league_id"],
                                nuovo_stato_lega
                            )
                            st.session_state["ml15_admin_message"] = (
                                "Stato della lega aggiornato a " + nuovo_stato_lega + "."
                            )
                            st.rerun()
                        except Exception as errore:
                            st.error(str(errore))

                reg_adv=carica_regolamento_avanzato(lega["league_id"])
                if reg_adv:
                    with st.expander("📝 Modifica regolamento e punteggi", expanded=False):
                        with st.container():
                            er1,er2,er3=st.columns(3)
                            with er1:
                                edit_mult=st.number_input("Moltiplicatore oltre soglia",min_value=1,
                                    value=int(reg_adv["moltiplicatore"]),step=1,format="%d",
                                    key="ml10_mult_"+str(lega["league_id"]))
                            with er2:
                                tipo_corrente=reg_adv["tipo_asta"] if reg_adv["tipo_asta"] in TIPI_ASTA_FANTA_LIVE else "A CHIAMATA"
                                edit_asta=st.selectbox("Tipo asta",TIPI_ASTA_FANTA_LIVE,
                                    index=TIPI_ASTA_FANTA_LIVE.index(tipo_corrente),
                                    key="ml10_asta_"+str(lega["league_id"]))
                            with er3:
                                edit_panchina=st.selectbox("Numero panchinari",list(range(6,11)),
                                    index=max(0,min(4,int(reg_adv["numero_panchinari"])-6)),
                                    key="ml10_panch_"+str(lega["league_id"]))

                            st.markdown("**Bonus / Malus**")
                            eb1,eb2,eb3=st.columns(3)
                            with eb1:
                                egf=st.number_input("GOL FATTO",value=reg_adv["gol_fatto"],step=0.5,format="%.2f",key="ml10_gf_"+str(lega["league_id"]))
                                egs=st.number_input("GOL SUBITO",value=reg_adv["gol_subito"],step=0.5,format="%.2f",key="ml10_gs_"+str(lega["league_id"]))
                            with eb2:
                                eam=st.number_input("AMMONIZIONE",value=reg_adv["ammonizione"],step=0.5,format="%.2f",key="ml10_am_"+str(lega["league_id"]))
                                eesp=st.number_input("ESPULSIONE",value=reg_adv["espulsione"],step=0.5,format="%.2f",key="ml10_es_"+str(lega["league_id"]))
                            with eb3:
                                ers=st.number_input("RIGORE SEGNATO",value=reg_adv["rigore_segnato"],step=0.5,format="%.2f",key="ml10_rs_"+str(lega["league_id"]))
                                ersub=st.number_input("RIGORE SUBITO",value=reg_adv["rigore_subito"],step=0.5,format="%.2f",key="ml10_rsub_"+str(lega["league_id"]))

                            st.markdown("**Modificatori**")

                            key_df="ml13_df_"+str(lega["league_id"])
                            key_rend="ml13_rend_"+str(lega["league_id"])

                            if key_df not in st.session_state:
                                st.session_state[key_df]=bool(reg_adv["d_factor"])
                            if key_rend not in st.session_state:
                                st.session_state[key_rend]=bool(reg_adv["rendimento"])

                            def _ml13_edit_df_changed(k_df=key_df,k_rend=key_rend):
                                if st.session_state.get(k_df):
                                    st.session_state[k_rend]=False

                            def _ml13_edit_rend_changed(k_df=key_df,k_rend=key_rend):
                                if st.session_state.get(k_rend):
                                    st.session_state[k_df]=False

                            em1,em2,em3,em4=st.columns(4)

                            with em1:
                                edf=st.toggle(
                                    "D-Factor",
                                    key=key_df,
                                    on_change=_ml13_edit_df_changed
                                )

                            with em2:
                                erend=st.toggle(
                                    "Fattore Rendimento",
                                    key=key_rend,
                                    on_change=_ml13_edit_rend_changed
                                )

                            with em3:
                                efp=st.toggle(
                                    "Fattore Fair Play",
                                    value=reg_adv["fair_play"],
                                    key="ml13_fp_"+str(lega["league_id"])
                                )

                            with em4:
                                ecap=st.toggle(
                                    "Fattore Capitano",
                                    value=reg_adv["capitano"],
                                    key="ml13_cap_"+str(lega["league_id"])
                                )

                            erend_tipo=reg_adv.get("rendimento_tipo","BONUS")
                            erend_fasce=reg_adv.get("rendimento_fasce",DEFAULT_RENDIMENTO_FASCE)

                            render_help_modificatori()
                            save_rules=st.button(
                                "SALVA REGOLAMENTO",
                                type="primary",
                                use_container_width=True,
                                key="ml12_save_rules_"+str(lega["league_id"])
                            )
                        if save_rules:
                            try:
                                salva_regolamento_avanzato(lega["league_id"],{
                                        "moltiplicatore":edit_mult,"tipo_asta":edit_asta,"fasce":reg_adv["fasce"],
                                        "gol_fatto":egf,"gol_subito":egs,"ammonizione":eam,"espulsione":eesp,
                                        "rigore_segnato":ers,"rigore_subito":ersub,"numero_panchinari":edit_panchina,
                                        "d_factor":edf,"rendimento":erend,"fair_play":efp,"capitano":ecap,
                                        "rendimento_tipo":erend_tipo,"rendimento_fasce":erend_fasce})
                                st.success("Regolamento aggiornato."); st.rerun()
                            except Exception as errore: st.error(str(errore))

                squadre = squadre_lega_multilega(
                    lega[
                        "league_id"
                    ]
                )

                st.markdown(
                    "**Squadre**"
                )

                for squadra in squadre:

                    c_nome, c_salva = st.columns(
                        [
                            5,
                            1
                        ],
                        vertical_alignment="bottom"
                    )

                    chiave = (
                        "ml03_nome_team_"
                        + str(
                            squadra[
                                "team_id"
                            ]
                        )
                    )

                    with c_nome:

                        nuovo_nome = st.text_input(
                            (
                                f"Squadra "
                                f"{squadra['posizione']}"
                            ),
                            value=squadra[
                                "nome"
                            ],
                            key=chiave
                        )

                    with c_salva:

                        if st.button(
                            "SALVA",
                            key=(
                                "ml03_salva_team_"
                                + str(
                                    squadra[
                                        "team_id"
                                    ]
                                )
                            ),
                            use_container_width=True
                        ):

                            try:

                                rinomina_squadra_multilega(
                                    lega[
                                        "league_id"
                                    ],
                                    squadra[
                                        "team_id"
                                    ],
                                    nuovo_nome
                                )

                                st.success(
                                    "Nome aggiornato."
                                )

                                st.rerun()

                            except Exception as errore:

                                st.error(
                                    str(
                                        errore
                                    )
                                )

                st.markdown("---")
                st.markdown("#### 👥 Accessi e ruoli")
                st.caption(
                    "Puoi modificare i ruoli di ogni squadra e reimpostare la password "
                    "del relativo account. TEAM rimane sempre attivo."
                )

                try:
                    dettagli_team = dettagli_squadre_lega_multilega(
                        lega["league_id"]
                    )
                except Exception as errore:
                    dettagli_team = []
                    st.error("Impossibile leggere ruoli e account: " + str(errore))

                for dt in dettagli_team:
                    badge = []
                    if dt["is_admin"]:
                        badge.append("ADMIN")
                    if dt["is_auctioneer"]:
                        badge.append("BANDITORE")
                    badge.append("TEAM")

                    with st.expander(
                        "👤 " + dt["nome"] + " · " + " / ".join(badge),
                        expanded=False
                    ):
                        st.caption(
                            "Username: " + (dt["username"] or "—")
                        )

                        rk_admin = "ml15_role_admin_" + str(dt["team_id"])
                        rk_band = "ml15_role_band_" + str(dt["team_id"])

                        rc1, rc2 = st.columns(2)
                        with rc1:
                            role_admin = st.toggle(
                                "Admin",
                                value=bool(dt["is_admin"]),
                                key=rk_admin
                            )
                        with rc2:
                            role_band = st.toggle(
                                "Banditore",
                                value=bool(dt["is_auctioneer"]),
                                key=rk_band
                            )

                        if st.button(
                            "SALVA RUOLI",
                            key="ml15_roles_save_"+str(dt["team_id"]),
                            use_container_width=True
                        ):
                            try:
                                aggiorna_ruoli_squadra_multilega(
                                    lega["league_id"],
                                    dt["team_id"],
                                    role_admin,
                                    role_band
                                )
                                st.session_state["ml15_admin_message"] = (
                                    "Ruoli di «" + dt["nome"] + "» aggiornati."
                                )
                                st.session_state.pop("ml_accesso_validato", None)
                                st.rerun()
                            except Exception as errore:
                                st.error(str(errore))

                        st.markdown("**Reset password**")
                        pw1, pw2 = st.columns(2)
                        with pw1:
                            nuova_pw = st.text_input(
                                "Nuova password",
                                type="password",
                                key="ml15_pw1_"+str(dt["team_id"])
                            )
                        with pw2:
                            conferma_pw = st.text_input(
                                "Conferma nuova password",
                                type="password",
                                key="ml15_pw2_"+str(dt["team_id"])
                            )

                        if st.button(
                            "REIMPOSTA PASSWORD",
                            key="ml15_pwreset_"+str(dt["team_id"]),
                            use_container_width=True
                        ):
                            if nuova_pw != conferma_pw:
                                st.error("Le due password non coincidono.")
                            else:
                                try:
                                    reset_password_squadra_multilega(
                                        lega["league_id"],
                                        dt["team_id"],
                                        nuova_pw
                                    )
                                    st.session_state["ml15_admin_message"] = (
                                        "Password di «" + dt["nome"] + "» reimpostata."
                                    )
                                    st.rerun()
                                except Exception as errore:
                                    st.error(str(errore))

                st.markdown("---")
                st.markdown("#### ➕ Aggiungi squadra")
                st.caption("Crea una nuova squadra con credenziali di primo accesso e, se necessario, assegna anche i ruoli Banditore o Admin.")

                with st.form("ml09_add_team_"+str(lega["league_id"])):
                    a1,a2=st.columns(2)
                    with a1:
                        add_username=st.text_input("Nome squadra / Username",key="ml09_user_"+str(lega["league_id"]))
                        add_password=st.text_input("Password iniziale",type="password",key="ml09_pass_"+str(lega["league_id"]))
                    with a2:
                        add_banditore=st.checkbox("Anche Banditore",key="ml09_band_"+str(lega["league_id"]))
                        add_admin=st.checkbox("Anche Admin",key="ml09_admin_"+str(lega["league_id"]))
                    add_submit=st.form_submit_button("➕ AGGIUNGI SQUADRA",type="primary",use_container_width=True)

                if add_submit:
                    try:
                        aggiungi_squadra_multilega(
                            lega["league_id"],add_username,add_password,
                            is_admin=add_admin,is_auctioneer=add_banditore)
                        st.session_state["ml09_team_message"]="Squadra «"+str(add_username).strip()+"» aggiunta correttamente."
                        st.session_state.pop("ml_accesso_validato",None)
                        st.rerun()
                    except Exception as errore:
                        st.error(str(errore))

                st.markdown("##### 🔗 Collega account esistente")
                st.caption(
                    "Usa questa funzione se l'utente possiede già un account FANTAELEGANZA. "
                    "La password esistente non viene modificata."
                )
                with st.form("ml15_link_existing_"+str(lega["league_id"])):
                    lx1, lx2 = st.columns(2)
                    with lx1:
                        link_username = st.text_input(
                            "Username esistente",
                            key="ml15_link_user_"+str(lega["league_id"])
                        )
                        link_team = st.text_input(
                            "Nome squadra",
                            key="ml15_link_team_"+str(lega["league_id"])
                        )
                    with lx2:
                        link_band = st.checkbox(
                            "Anche Banditore",
                            key="ml15_link_band_"+str(lega["league_id"])
                        )
                        link_admin = st.checkbox(
                            "Anche Admin",
                            key="ml15_link_admin_"+str(lega["league_id"])
                        )
                    link_submit = st.form_submit_button(
                        "🔗 COLLEGA ACCOUNT",
                        use_container_width=True
                    )

                if link_submit:
                    try:
                        collega_utente_esistente_lega(
                            lega["league_id"],
                            link_username,
                            link_team,
                            is_admin=link_admin,
                            is_auctioneer=link_band
                        )
                        st.session_state["ml15_admin_message"] = (
                            "Account «" + str(link_username).strip()
                            + "» collegato alla lega."
                        )
                        st.session_state.pop("ml_accesso_validato", None)
                        st.rerun()
                    except Exception as errore:
                        st.error(str(errore))

                st.markdown("---")
                st.markdown("#### ➖ Rimuovi squadra")
                st.caption("La rimozione cancella la squadra dalla lega e i suoi dati collegati. L'account utente globale viene conservato.")

                if len(squadre) <= 1:
                    st.info("Non puoi rimuovere l'ultima squadra della lega.")
                else:
                    opzioni={s["nome"]:s["team_id"] for s in squadre}
                    team_da_rimuovere=st.selectbox(
                        "Squadra da rimuovere",
                        list(opzioni.keys()),
                        key="ml09_remove_select_"+str(lega["league_id"]))
                    conferma_remove=st.checkbox(
                        "Confermo la rimozione definitiva della squadra selezionata",
                        key="ml09_remove_check_"+str(lega["league_id"]))
                    if st.button(
                        "➖ RIMUOVI SQUADRA",
                        disabled=not conferma_remove,
                        use_container_width=True,
                        key="ml09_remove_btn_"+str(lega["league_id"])):
                        try:
                            nome_rimosso=rimuovi_squadra_multilega(
                                lega["league_id"],opzioni[team_da_rimuovere])
                            st.session_state["ml09_team_message"]="Squadra «"+nome_rimosso+"» rimossa dalla lega."
                            if int(st.session_state.get("ml_team_id") or -1) == int(opzioni[team_da_rimuovere]):
                                azzera_contesto_multilega()
                            else:
                                st.session_state.pop("ml_accesso_validato",None)
                            st.rerun()
                        except Exception as errore:
                            st.error(str(errore))

                st.markdown(
                    "---"
                )

                st.markdown(
                    "#### ⚠️ Elimina lega"
                )

                st.caption(
                    "L'eliminazione è definitiva: vengono cancellati "
                    "regolamento, squadre, membership, rose, budget e "
                    "tutti i dati collegati alla lega. Gli account utente "
                    "restano disponibili."
                )

                conferma_testo = st.text_input(
                    (
                        "Per confermare scrivi esattamente: "
                        + str(
                            lega[
                                "nome"
                            ]
                        )
                    ),
                    key=(
                        "ml08_delete_confirm_"
                        + str(
                            lega[
                                "league_id"
                            ]
                        )
                    )
                )

                conferma_eliminazione = st.checkbox(
                    "Confermo di voler eliminare definitivamente questa lega",
                    key=(
                        "ml08_delete_check_"
                        + str(
                            lega[
                                "league_id"
                            ]
                        )
                    )
                )

                nome_corretto = (
                    str(
                        conferma_testo
                    ).strip()
                    == str(
                        lega[
                            "nome"
                        ]
                    ).strip()
                )

                if st.button(
                    "🗑️ ELIMINA DEFINITIVAMENTE LA LEGA",
                    type="secondary",
                    use_container_width=True,
                    disabled=not (
                        nome_corretto
                        and conferma_eliminazione
                    ),
                    key=(
                        "ml08_delete_league_"
                        + str(
                            lega[
                                "league_id"
                            ]
                        )
                    )
                ):

                    try:

                        lega_eliminata_id = int(
                            lega[
                                "league_id"
                            ]
                        )

                        nome_eliminato = (
                            elimina_lega_multilega(
                                lega_eliminata_id
                            )
                        )

                        st.session_state[
                            "ml08_lega_eliminata"
                        ] = (
                            "Lega «"
                            + nome_eliminato
                            + "» eliminata definitivamente."
                        )

                        # Se era la lega attualmente aperta, il contesto
                        # non deve più restare valido.
                        if int(
                            st.session_state.get(
                                "ml_league_id",
                                -1
                            )
                        ) == lega_eliminata_id:

                            azzera_contesto_multilega()

                        st.session_state.pop(
                            "ml_accesso_validato",
                            None
                        )

                        st.session_state.pop(
                            (
                                "ml03_boot_"
                                + str(
                                    PROFILO_ATTIVO
                                )
                            ),
                            None
                        )

                        st.rerun()

                    except Exception as errore:

                        st.error(
                            "Impossibile eliminare la lega: "
                            + str(
                                errore
                            )
                        )



# ============================================================
# IMPORT LISTONE
# ============================================================

def importa_listone_nel_database(df):

    """
    Importazione ottimizzata per database Cloud.

    Obiettivi:
    - evitare centinaia di round-trip verso Turso;
    - aggiornare solo i giocatori realmente cambiati;
    - eseguire UPSERT multi-riga a blocchi;
    - mantenere stato e prezzo dei giocatori già presenti.
    """

    # L'import del listone può coinvolgere centinaia di righe.
    # Per mantenere l'operazione veloce sul Cloud NON creiamo
    # automaticamente uno snapshot completo qui.
    #
    # Se serve un punto di sicurezza, usa il pulsante Snapshot
    # prima di caricare il nuovo listone.

    conn = get_connection()
    cur = conn.cursor()

    def pulisci_valore(
        valore
    ):

        if valore is None:
            return None

        try:
            if pd.isna(
                valore
            ):
                return None
        except Exception:
            pass

        return valore

    def normalizza_numero(
        valore
    ):

        valore = pulisci_valore(
            valore
        )

        if valore is None:
            return None

        try:
            return float(
                valore
            )
        except Exception:
            return valore

    try:

        # ----------------------------------------------------
        # 1. UNA SOLA LETTURA DELLO STATO ATTUALE
        # ----------------------------------------------------

        cur.execute("""
            SELECT
                id,
                ruolo_classico,
                ruolo_mantra,
                nome,
                squadra,
                quotazione_attuale,
                quotazione_iniziale,
                differenza,
                quotazione_attuale_mantra,
                quotazione_iniziale_mantra,
                differenza_mantra,
                fvm,
                fvm_mantra

            FROM giocatori
        """)

        esistenti = {}

        for riga in cur.fetchall():

            giocatore_id = int(
                riga[0]
            )

            esistenti[
                giocatore_id
            ] = (
                str(
                    riga[1]
                    or ""
                ).strip(),

                str(
                    riga[2]
                    or ""
                ).strip(),

                str(
                    riga[3]
                    or ""
                ).strip(),

                str(
                    riga[4]
                    or ""
                ).strip(),

                normalizza_numero(
                    riga[5]
                ),

                normalizza_numero(
                    riga[6]
                ),

                normalizza_numero(
                    riga[7]
                ),

                normalizza_numero(
                    riga[8]
                ),

                normalizza_numero(
                    riga[9]
                ),

                normalizza_numero(
                    riga[10]
                ),

                normalizza_numero(
                    riga[11]
                ),

                normalizza_numero(
                    riga[12]
                )
            )

        # ----------------------------------------------------
        # 2. PREPARAZIONE LOCALE: NESSUNA QUERY PER GIOCATORE
        # ----------------------------------------------------

        da_scrivere = []
        nuovi = 0
        aggiornati = 0

        for _, row in df.iterrows():

            try:

                giocatore_id = int(
                    row[
                        "Id"
                    ]
                )

            except Exception:

                continue

            nome = str(
                row.get(
                    "Nome",
                    ""
                )
                or ""
            ).strip()

            if not nome:
                continue

            dati_confronto = (
                str(
                    row.get(
                        "R",
                        ""
                    )
                    or ""
                ).strip(),

                str(
                    row.get(
                        "RM",
                        ""
                    )
                    or ""
                ).strip(),

                nome,

                str(
                    row.get(
                        "Squadra",
                        ""
                    )
                    or ""
                ).strip(),

                normalizza_numero(
                    row.get(
                        "Qt.A"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Qt.I"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Diff."
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Qt.A M"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Qt.I M"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Diff.M"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "FVM"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "FVM M"
                    )
                )
            )

            precedente = (
                esistenti.get(
                    giocatore_id
                )
            )

            if precedente is None:

                nuovi += 1

            elif precedente == dati_confronto:

                # Giocatore identico: nessuna scrittura Cloud.
                continue

            else:

                aggiornati += 1

            da_scrivere.append(
                (
                    giocatore_id,
                    *dati_confronto
                )
            )

        # ----------------------------------------------------
        # 3. UPSERT MULTI-RIGA A BLOCCHI
        # ----------------------------------------------------
        #
        # 13 parametri per giocatore.
        # 50 giocatori = 650 parametri per query:
        # abbastanza piccolo per restare compatibile e riduce
        # enormemente i round-trip verso Turso.

        DIMENSIONE_BLOCCO = 50

        colonne = """
            id,
            ruolo_classico,
            ruolo_mantra,
            nome,
            squadra,
            quotazione_attuale,
            quotazione_iniziale,
            differenza,
            quotazione_attuale_mantra,
            quotazione_iniziale_mantra,
            differenza_mantra,
            fvm,
            fvm_mantra
        """

        update_sql = """
            ruolo_classico = excluded.ruolo_classico,
            ruolo_mantra = excluded.ruolo_mantra,
            nome = excluded.nome,
            squadra = excluded.squadra,
            quotazione_attuale = excluded.quotazione_attuale,
            quotazione_iniziale = excluded.quotazione_iniziale,
            differenza = excluded.differenza,
            quotazione_attuale_mantra = excluded.quotazione_attuale_mantra,
            quotazione_iniziale_mantra = excluded.quotazione_iniziale_mantra,
            differenza_mantra = excluded.differenza_mantra,
            fvm = excluded.fvm,
            fvm_mantra = excluded.fvm_mantra,
            ultimo_aggiornamento = CURRENT_TIMESTAMP
        """

        for inizio in range(
            0,
            len(
                da_scrivere
            ),
            DIMENSIONE_BLOCCO
        ):

            blocco = da_scrivere[
                inizio:
                inizio
                + DIMENSIONE_BLOCCO
            ]

            if not blocco:
                continue

            placeholders_riga = (
                "("
                + ", ".join(
                    [
                        "?"
                        for _ in range(
                            13
                        )
                    ]
                )
                + ")"
            )

            placeholders = ", ".join(
                [
                    placeholders_riga
                    for _ in blocco
                ]
            )

            parametri = []

            for valori in blocco:

                parametri.extend(
                    valori
                )

            query = f"""
                INSERT INTO giocatori (
                    {colonne}
                )

                VALUES
                    {placeholders}

                ON CONFLICT(id) DO UPDATE SET
                    {update_sql}
            """

            cur.execute(
                query,
                tuple(
                    parametri
                )
            )

        # Un solo commit finale.
        conn.commit()

    finally:

        chiudi_connessione(
            conn
        )

    # Ricaricheremo i dati una sola volta dopo l'import.
    invalida_cache_dati()

    # Memorizza data e ora dell'ultimo upload completato con successo.
    st.session_state[
        "ultimo_upload_listone"
    ] = datetime.now(
        ZoneInfo(
            "Europe/Rome"
        )
    ).strftime(
        "%d/%m/%Y alle %H:%M:%S"
    )

    return (
        nuovi,
        aggiornati
    )


# ============================================================
# LETTURA DATABASE
# ============================================================

def carica_tutti_giocatori():

    chiave = "_df_giocatori_sessione"

    if chiave in st.session_state:

        # Il DataFrame è già mantenuto coerente dalle operazioni.
        # Restituiamo il riferimento per evitare copie da 500+ righe
        # a ogni rerun; le funzioni che devono modificarlo usano .copy().
        return st.session_state[
            chiave
        ]

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT

            id AS Id,

            ruolo_classico AS R,
            ruolo_mantra AS RM,

            nome AS Nome,
            squadra AS Squadra,

            quotazione_attuale
                AS "Qt.A",

            quotazione_iniziale
                AS "Qt.I",

            differenza
                AS "Diff.",

            quotazione_attuale_mantra
                AS "Qt.A M",

            quotazione_iniziale_mantra
                AS "Qt.I M",

            differenza_mantra
                AS "Diff.M",

            fvm AS FVM,

            fvm_mantra
                AS "FVM M",

            stato AS Stato,

            prezzo_acquisto
                AS Prezzo

        FROM giocatori
    """, conn)

    chiudi_connessione(
        conn
    )

    st.session_state[
        chiave
    ] = df.copy()

    return df


# ============================================================
# OPERAZIONI
# ============================================================

def esegui_operazione(
    giocatore_id,
    tipo,
    nuovo_stato,
    nuovo_prezzo=None,
    costo_svincolo=0
):

    # Recupera lo stato precedente dalla copia già in memoria.
    df_corrente = carica_tutti_giocatori()

    giocatore_id_db = int(
        giocatore_id
    )

    riga = df_corrente[
        df_corrente["Id"]
        == giocatore_id_db
    ]

    if riga.empty:
        return

    precedente = riga.iloc[0]

    # Tutti i parametri vengono convertiti in tipi Python nativi.
    # È importante con Turso/libsql perché valori pandas/numpy
    # possono produrre ValueError in alcuni percorsi operativi.
    nome = str(
        precedente.get(
            "Nome",
            ""
        )
    )

    stato_prima = str(
        precedente.get(
            "Stato",
            ""
        )
    )

    prezzo_prima_raw = precedente.get(
        "Prezzo"
    )

    prezzo_prima = (
        None
        if pd.isna(
            prezzo_prima_raw
        )
        else float(
            prezzo_prima_raw
        )
    )

    tipo_db = str(
        tipo
    )

    nuovo_stato_db = str(
        nuovo_stato
    )

    nuovo_prezzo_db = (
        None
        if nuovo_prezzo is None
        or pd.isna(
            nuovo_prezzo
        )
        else float(
            nuovo_prezzo
        )
    )

    costo_svincolo_db = float(
        costo_svincolo
        or 0
    )

    conn = get_connection()
    cur = conn.cursor()

    try:

        # ------------------------------------------------------
        # 1. REGISTRA OPERAZIONE
        # ------------------------------------------------------

        cur.execute("""
            INSERT INTO operazioni (

                tipo,
                giocatore_id,
                nome_giocatore,

                stato_prima,
                prezzo_prima,

                stato_dopo,
                prezzo_dopo,

                costo_svincolo
            )

            VALUES (
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?
            )
        """, (
            tipo_db,
            giocatore_id_db,
            nome,
            stato_prima,
            prezzo_prima,
            nuovo_stato_db,
            nuovo_prezzo_db,
            costo_svincolo_db
        ))

        # lastrowid non è sempre affidabile allo stesso modo
        # tra sqlite3 e libsql: recuperiamo esplicitamente l'id.
        cur.execute(
            "SELECT last_insert_rowid()"
        )

        riga_id = cur.fetchone()

        operazione_id = (
            int(
                riga_id[0]
            )
            if riga_id
            and riga_id[0] is not None
            else 0
        )

        # ------------------------------------------------------
        # 2. EVENTUALE COSTO SVINCOLO
        # ------------------------------------------------------

        if costo_svincolo_db > 0:

            cur.execute("""
                INSERT INTO costi_svincoli (
                    operazione_id,
                    giocatore_id,
                    nome_giocatore,
                    importo
                )
                VALUES (?, ?, ?, ?)
            """, (
                operazione_id,
                giocatore_id_db,
                nome,
                costo_svincolo_db
            ))

        # ------------------------------------------------------
        # 3. AGGIORNA STATO GIOCATORE
        # ------------------------------------------------------

        cur.execute("""
            UPDATE giocatori

            SET
                stato = ?,
                prezzo_acquisto = ?

            WHERE id = ?
        """, (
            nuovo_stato_db,
            nuovo_prezzo_db,
            giocatore_id_db
        ))

        # ------------------------------------------------------
        # 4. CRONOLOGIA: CONSERVA SOLO LE ULTIME 10 OPERAZIONI
        # ------------------------------------------------------

        cur.execute("""
            DELETE FROM operazioni

            WHERE id NOT IN (
                SELECT id
                FROM operazioni
                ORDER BY id DESC
                LIMIT ?
            )
        """, (
            int(
                MAX_UNDO
            ),
        ))

        conn.commit()

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        chiudi_connessione(
            conn
        )

    # ----------------------------------------------------------
    # AGGIORNAMENTO CACHE LOCALE
    # ----------------------------------------------------------

    maschera = (
        st.session_state[
            "_df_giocatori_sessione"
        ]["Id"]
        == giocatore_id_db
    )

    st.session_state[
        "_df_giocatori_sessione"
    ].loc[
        maschera,
        "Stato"
    ] = nuovo_stato_db

    st.session_state[
        "_df_giocatori_sessione"
    ].loc[
        maschera,
        "Prezzo"
    ] = nuovo_prezzo_db

    aggiorna_cronologia_locale_dopo_operazione(
        operazione_id,
        tipo_db,
        giocatore_id_db,
        nome,
        stato_prima,
        prezzo_prima,
        nuovo_stato_db,
        nuovo_prezzo_db,
        costo_svincolo_db
    )

    if costo_svincolo_db > 0:

        st.session_state[
            "_costi_svincoli_sessione"
        ] = round(
            calcola_costi_svincoli()
            + costo_svincolo_db,
            2
        )

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if "pdf_rosa_moduli" in st.session_state:
        st.session_state.pdf_rosa_moduli = None

def carica_ultime_operazioni():

    chiave = "_ultime_operazioni_sessione"

    if chiave in st.session_state:

        return st.session_state[chiave]

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT

            id AS Id,

            tipo AS Operazione,

            giocatore_id
                AS GiocatoreId,

            nome_giocatore
                AS Giocatore,

            stato_prima
                AS StatoPrima,

            prezzo_prima
                AS PrezzoPrima,

            stato_dopo
                AS StatoDopo,

            prezzo_dopo
                AS PrezzoDopo,

            costo_svincolo
                AS CostoSvincolo,

            data_operazione
                AS Data

        FROM operazioni

        ORDER BY id DESC

        LIMIT 10
    """, conn)

    chiudi_connessione(
        conn
    )

    st.session_state[
        chiave
    ] = df.copy()

    return df


def aggiorna_cronologia_locale_dopo_operazione(
    operazione_id,
    tipo,
    giocatore_id,
    nome,
    stato_prima,
    prezzo_prima,
    stato_dopo,
    prezzo_dopo,
    costo_svincolo
):

    chiave = "_ultime_operazioni_sessione"

    colonne = [
        "Id",
        "Operazione",
        "GiocatoreId",
        "Giocatore",
        "StatoPrima",
        "PrezzoPrima",
        "StatoDopo",
        "PrezzoDopo",
        "CostoSvincolo",
        "Data"
    ]

    nuova = pd.DataFrame(
        [
            {
                "Id": int(
                    operazione_id
                    or 0
                ),
                "Operazione": tipo,
                "GiocatoreId": int(
                    giocatore_id
                ),
                "Giocatore": nome,
                "StatoPrima": stato_prima,
                "PrezzoPrima": prezzo_prima,
                "StatoDopo": stato_dopo,
                "PrezzoDopo": prezzo_dopo,
                "CostoSvincolo": float(
                    costo_svincolo
                    or 0
                ),
                "Data": datetime.now(
                    ZoneInfo(
                        "Europe/Rome"
                    )
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        ],
        columns=colonne
    )

    precedente = (
        st.session_state.get(
            chiave
        )
    )

    if (
        precedente is None
        or precedente.empty
    ):

        storico = nuova

    else:

        storico = pd.concat(
            [
                nuova,
                precedente
            ],
            ignore_index=True
        ).head(
            MAX_UNDO
        )

    st.session_state[
        chiave
    ] = storico

def annulla_ultima_operazione():

    operazioni = (
        carica_ultime_operazioni()
    )

    if operazioni.empty:
        return False

    ultima = operazioni.iloc[0]

    operazione_id = int(
        ultima["Id"]
    )

    giocatore_id = int(
        ultima["GiocatoreId"]
    )

    stato_prima = ultima[
        "StatoPrima"
    ]

    prezzo_prima = ultima[
        "PrezzoPrima"
    ]

    costo_svincolo = float(
        ultima[
            "CostoSvincolo"
        ]
        or 0
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE giocatori

        SET
            stato = ?,
            prezzo_acquisto = ?

        WHERE id = ?
    """, (
        stato_prima,
        (
            None
            if pd.isna(
                prezzo_prima
            )
            else float(
                prezzo_prima
            )
        ),
        giocatore_id
    ))

    if costo_svincolo > 0:

        cur.execute("""
            DELETE FROM costi_svincoli

            WHERE operazione_id = ?
        """, (
            operazione_id,
        ))

    cur.execute("""
        DELETE FROM operazioni

        WHERE id = ?
    """, (
        operazione_id,
    ))

    conn.commit()

    chiudi_connessione(
        conn
    )

    # Aggiorna subito la copia in memoria.
    df_sessione = (
        carica_tutti_giocatori()
    )

    maschera = (
        df_sessione["Id"]
        == giocatore_id
    )

    df_sessione.loc[
        maschera,
        "Stato"
    ] = stato_prima

    df_sessione.loc[
        maschera,
        "Prezzo"
    ] = (
        None
        if pd.isna(
            prezzo_prima
        )
        else float(
            prezzo_prima
        )
    )

    st.session_state[
        "_df_giocatori_sessione"
    ] = df_sessione

    # Rimuove localmente l'operazione appena annullata.
    storico = st.session_state.get(
        "_ultime_operazioni_sessione"
    )

    if (
        storico is not None
        and not storico.empty
    ):

        st.session_state[
            "_ultime_operazioni_sessione"
        ] = (
            storico[
                storico["Id"]
                != operazione_id
            ]
            .reset_index(
                drop=True
            )
        )

    if costo_svincolo > 0:

        st.session_state[
            "_costi_svincoli_sessione"
        ] = round(
            max(
                0.0,
                calcola_costi_svincoli()
                - costo_svincolo
            ),
            2
        )

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if "pdf_rosa_moduli" in st.session_state:
        st.session_state.pdf_rosa_moduli = None

    return True



def ripristina_tutti_giocatori_avversari():
    """
    Rende nuovamente DISPONIBILI tutti i giocatori attualmente
    assegnati agli avversari del profilo attivo.

    Non modifica:
    - la propria rosa;
    - i prezzi dei propri acquisti;
    - i costi di svincolo.

    Elimina dalla cronologia UNDO solo le operazioni collegate
    allo stato AVVERSARIO, così non rimangono riferimenti incoerenti.
    """

    df_corrente = carica_tutti_giocatori()

    avversari = (
        df_corrente[
            df_corrente["Stato"] == "AVVERSARIO"
        ]
        .copy()
    )

    if avversari.empty:
        return 0

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE giocatori

            SET
                stato = 'DISPONIBILE',
                prezzo_acquisto = NULL

            WHERE stato = 'AVVERSARIO'
        """)

        # Rimuove soltanto le operazioni che coinvolgono lo stato
        # AVVERSARIO. Le operazioni della propria rosa restano intatte.
        cur.execute("""
            DELETE FROM operazioni

            WHERE stato_dopo = 'AVVERSARIO'
               OR stato_prima = 'AVVERSARIO'
        """)

        conn.commit()

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        chiudi_connessione(
            conn
        )

    # Aggiorna subito la copia in memoria.
    if "_df_giocatori_sessione" in st.session_state:

        df_sessione = (
            st.session_state[
                "_df_giocatori_sessione"
            ]
            .copy()
        )

        mask = (
            df_sessione["Stato"]
            == "AVVERSARIO"
        )

        df_sessione.loc[
            mask,
            "Stato"
        ] = "DISPONIBILE"

        df_sessione.loc[
            mask,
            "Prezzo"
        ] = None

        st.session_state[
            "_df_giocatori_sessione"
        ] = df_sessione

    # Forza il ricaricamento della cronologia.
    st.session_state.pop(
        "_ultime_operazioni_sessione",
        None
    )

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if "pdf_rosa_moduli" in st.session_state:
        st.session_state.pdf_rosa_moduli = None

    return int(
        len(
            avversari
        )
    )


def elimina_tutta_la_rosa():
    df_corrente = carica_tutti_giocatori()
    rosa = df_corrente[df_corrente["Stato"] == "MIO"].copy()
    if rosa.empty:
        return 0

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE giocatori
        SET stato = 'DISPONIBILE',
            prezzo_acquisto = NULL
        WHERE stato = 'MIO'
    """)
    cur.execute("DELETE FROM costi_svincoli")
    cur.execute("DELETE FROM operazioni")
    conn.commit()
    chiudi_connessione(conn)

    if "_df_giocatori_sessione" in st.session_state:
        df_sessione = st.session_state["_df_giocatori_sessione"]
        mask = df_sessione["Stato"] == "MIO"
        df_sessione.loc[mask, "Stato"] = "DISPONIBILE"
        df_sessione.loc[mask, "Prezzo"] = None
        st.session_state["_df_giocatori_sessione"] = df_sessione

    try:
        carica_ultime_operazioni.clear()
    except Exception:
        pass
    try:
        calcola_costi_svincoli.clear()
    except Exception:
        pass

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    return int(len(rosa))


# ============================================================
# ECONOMIA DATABASE
# ============================================================

def calcola_valore_acquisti_attivi():

    df = carica_tutti_giocatori()

    if (
        df is None
        or df.empty
        or "Stato" not in df.columns
        or "Prezzo" not in df.columns
    ):
        return 0.0

    prezzi = pd.to_numeric(
        df.loc[
            df["Stato"] == "MIO",
            "Prezzo"
        ],
        errors="coerce"
    ).fillna(0)

    return round(
        float(
            prezzi.sum()
        ),
        2
    )


def calcola_costi_svincoli():

    chiave = "_costi_svincoli_sessione"

    if chiave in st.session_state:

        return round(
            float(
                st.session_state[
                    chiave
                ]
                or 0
            ),
            2
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COALESCE(
                SUM(importo),
                0
            )

        FROM costi_svincoli
    """)

    riga = cur.fetchone()

    chiudi_connessione(
        conn
    )

    totale = round(
        float(
            (
                riga[0]
                if riga
                else 0
            )
            or 0
        ),
        2
    )

    st.session_state[
        chiave
    ] = totale

    return totale

def calcola_valore_acquisti_totale():

    return round(
        calcola_valore_acquisti_attivi()
        + calcola_costi_svincoli(),
        2
    )


# ============================================================
# CACHE DATI CLOUD
# ============================================================

def invalida_cache_dati():

    chiavi_sessione = [
        "backup_cloud_bytes",
        "pdf_rosa_moduli",
        "_df_giocatori_sessione",
        "_ultime_operazioni_sessione",
        "_costi_svincoli_sessione",
        "_ml16_sidebar_metrics"
    ]

    for chiave in chiavi_sessione:

        if chiave in st.session_state:

            if chiave in (
                "backup_cloud_bytes",
                "pdf_rosa_moduli"
            ):

                st.session_state[
                    chiave
                ] = None

            else:

                del st.session_state[
                    chiave
                ]

    try:
        elenco_snapshot.clear()
    except Exception:
        pass


# ============================================================
# PDF - ROSA E MODULI
# ============================================================

def genera_pdf_rosa_e_moduli(
    df_rosa,
    valore_attivi,
    costi_svincoli,
    valore_acquisti,
    spesa_effettiva
):
    """
    Genera un PDF scaricabile con:
    - rosa completa e tutti i dati disponibili;
    - riepilogo economico;
    - classifica dei moduli;
    - tutti i moduli Mantra con ruoli, copertura e giocatori compatibili.
    """

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            KeepTogether
        )
    except ImportError as errore:
        raise RuntimeError(
            "Per creare il PDF è necessario il pacchetto reportlab. "
            "Aggiungi 'reportlab>=4.0,<5' al file requirements.txt."
        ) from errore

    buffer = io.BytesIO()

    pagina = landscape(
        A4
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagina,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title="FANTAELEGANZA 26/27 - Rosa e Moduli",
        author="FANTAELEGANZA 26/27"
    )

    styles = getSampleStyleSheet()

    stile_titolo = ParagraphStyle(
        "TitoloFanta",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        textColor=colors.HexColor("#071a2f"),
        alignment=TA_CENTER,
        spaceAfter=7
    )

    stile_sottotitolo = ParagraphStyle(
        "SottotitoloFanta",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#071a2f"),
        spaceBefore=4,
        spaceAfter=5
    )

    stile_testo = ParagraphStyle(
        "TestoFanta",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#111827")
    )

    stile_piccolo = ParagraphStyle(
        "PiccoloFanta",
        parent=stile_testo,
        fontSize=6.7,
        leading=8
    )

    stile_slot = ParagraphStyle(
        "SlotFanta",
        parent=stile_piccolo,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827")
    )

    elementi = []

    # --------------------------------------------------------
    # TESTATA
    # --------------------------------------------------------

    elementi.append(
        Paragraph(
            "FANTAELEGANZA 26/27",
            stile_titolo
        )
    )

    elementi.append(
        Paragraph(
            "Rosa e moduli Mantra",
            ParagraphStyle(
                "SubTitle",
                parent=stile_testo,
                alignment=TA_CENTER,
                fontSize=10,
                leading=12,
                textColor=colors.HexColor("#64748b")
            )
        )
    )

    elementi.append(
        Paragraph(
            "Generato il "
            + datetime.now().strftime(
                "%d/%m/%Y alle %H:%M"
            ),
            ParagraphStyle(
                "DataPDF",
                parent=stile_piccolo,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#64748b")
            )
        )
    )

    elementi.append(
        Spacer(
            1,
            5 * mm
        )
    )

    # --------------------------------------------------------
    # RIEPILOGO ECONOMICO
    # --------------------------------------------------------

    elementi.append(
        Paragraph(
            "Riepilogo economico",
            stile_sottotitolo
        )
    )

    dati_economia = [
        [
            "Giocatori in rosa",
            "Valore acquisti attivi",
            "Costi svincoli",
            "Valore totale asta",
            "Spesa effettiva"
        ],
        [
            str(
                len(
                    df_rosa
                )
            ),
            f"{formatta_crediti(valore_attivi)} EUR",
            f"{formatta_crediti(costi_svincoli)} EUR",
            f"{formatta_crediti(valore_acquisti)} EUR",
            f"{formatta_crediti(spesa_effettiva)} EUR"
        ]
    ]

    tab_economia = Table(
        dati_economia,
        colWidths=[
            40 * mm,
            40 * mm,
            40 * mm,
            40 * mm,
            40 * mm
        ]
    )

    tab_economia.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#071a2f")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#cbd5e1")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.HexColor("#f8fafc")
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elementi.append(
        tab_economia
    )

    elementi.append(
        Spacer(
            1,
            5 * mm
        )
    )

    # --------------------------------------------------------
    # ROSA COMPLETA
    # --------------------------------------------------------

    elementi.append(
        Paragraph(
            "Rosa - dati completi",
            stile_sottotitolo
        )
    )

    colonne_pdf = [
        "Id",
        "R",
        "RM",
        "Nome",
        "Squadra",
        "Qt.A",
        "Qt.I",
        "Diff.",
        "Qt.A M",
        "Qt.I M",
        "Diff.M",
        "FVM",
        "FVM M",
        "Prezzo"
    ]

    intestazioni = [
        "ID",
        "R",
        "RM",
        "NOME",
        "SQUADRA",
        "QT.A",
        "QT.I",
        "DIFF",
        "QT.A M",
        "QT.I M",
        "DIFF.M",
        "FVM",
        "FVM M",
        "PREZZO"
    ]

    dati_rosa = [
        intestazioni
    ]

    if not df_rosa.empty:

        rosa_pdf = (
            df_rosa.copy()
        )

        rosa_pdf[
            "_ordine_ruolo"
        ] = (
            rosa_pdf["RM"]
            .apply(
                priorita_ruolo
            )
        )

        rosa_pdf = (
            rosa_pdf
            .sort_values(
                [
                    "_ordine_ruolo",
                    "Nome"
                ]
            )
        )

        for _, riga in (
            rosa_pdf.iterrows()
        ):

            riga_pdf = []

            for colonna in (
                colonne_pdf
            ):

                valore = (
                    riga.get(
                        colonna,
                        ""
                    )
                )

                if pd.isna(
                    valore
                ):
                    valore = ""

                if colonna == "Prezzo":
                    valore = (
                        formatta_crediti(
                            valore
                        )
                        if valore != ""
                        else ""
                    )

                elif colonna in (
                    "Qt.A",
                    "Qt.I",
                    "Diff.",
                    "Qt.A M",
                    "Qt.I M",
                    "Diff.M",
                    "FVM",
                    "FVM M"
                ):

                    try:
                        valore = (
                            f"{float(valore):g}"
                            if valore != ""
                            else ""
                        )
                    except Exception:
                        pass

                riga_pdf.append(
                    Paragraph(
                        html.escape(
                            str(
                                valore
                            )
                        ),
                        stile_piccolo
                    )
                )

            dati_rosa.append(
                riga_pdf
            )

    larghezze = [
        9 * mm,
        10 * mm,
        18 * mm,
        31 * mm,
        23 * mm,
        14 * mm,
        14 * mm,
        13 * mm,
        16 * mm,
        16 * mm,
        14 * mm,
        14 * mm,
        16 * mm,
        18 * mm
    ]

    tab_rosa = Table(
        dati_rosa,
        colWidths=larghezze,
        repeatRows=1
    )

    tab_rosa.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#071a2f")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                6
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.25,
                colors.HexColor("#cbd5e1")
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f8fafc")
                ]
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3
            )
        ])
    )

    elementi.append(
        tab_rosa
    )

    # --------------------------------------------------------
    # CLASSIFICA MODULI
    # --------------------------------------------------------

    elementi.append(
        PageBreak()
    )

    elementi.append(
        Paragraph(
            "Classifica moduli",
            stile_titolo
        )
    )

    classifica = (
        classifica_moduli(
            df_rosa
        )
    )

    dati_classifica = [[
        "POS.",
        "MODULO",
        "PUNTEGGIO",
        "COPERTURA MEDIA",
        "SCOPERTI",
        "SLOT DEBOLI",
        "AL 100%"
    ]]

    for riga in classifica:

        dati_classifica.append([
            riga[
                "Posizione"
            ],
            riga[
                "Modulo"
            ],
            f"{riga['Punteggio']}/100",
            f"{riga['Copertura media']}%",
            riga[
                "Scoperti"
            ],
            riga[
                "Deboli"
            ],
            riga[
                "Al 100%"
            ]
        ])

    tab_classifica = Table(
        dati_classifica,
        colWidths=[
            18 * mm,
            30 * mm,
            32 * mm,
            38 * mm,
            27 * mm,
            30 * mm,
            27 * mm
        ]
    )

    tab_classifica.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#071a2f")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.HexColor("#fef3c7")
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#cbd5e1")
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elementi.append(
        tab_classifica
    )

    # --------------------------------------------------------
    # TUTTI I MODULI
    # --------------------------------------------------------

    for nome_modulo in (
        MODULI.keys()
    ):

        elementi.append(
            PageBreak()
        )

        analisi = (
            analizza_modulo(
                df_rosa,
                nome_modulo
            )
        )

        ruoli_al_100, totale_slot, copertura_media = (
            calcola_copertura_modulo(
                df_rosa,
                nome_modulo
            )
        )

        elementi.append(
            Paragraph(
                f"Modulo {html.escape(nome_modulo)}",
                stile_titolo
            )
        )

        elementi.append(
            Paragraph(
                (
                    f"Punteggio strategico: "
                    f"<b>{analisi['Punteggio']}/100</b> &nbsp;&nbsp; "
                    f"Copertura media: "
                    f"<b>{round(copertura_media)}%</b> &nbsp;&nbsp; "
                    f"Ruoli al 100%: "
                    f"<b>{ruoli_al_100}/{totale_slot}</b> &nbsp;&nbsp; "
                    f"Slot scoperti: "
                    f"<b>{analisi['Scoperti']}</b>"
                ),
                ParagraphStyle(
                    "ModuloSummary",
                    parent=stile_testo,
                    alignment=TA_CENTER,
                    fontSize=8.5,
                    leading=11,
                    spaceAfter=5
                )
            )
        )

        contenuto_campo = []

        righe_modulo = (
            MODULI[
                nome_modulo
            ]
        )

        # Attacco in alto, portiere in basso.
        for _, posizioni in reversed(
            righe_modulo
        ):

            celle = []

            numero_posizioni = (
                len(
                    posizioni
                )
            )

            larghezza_cella = (
                247 * mm
                / max(
                    1,
                    numero_posizioni
                )
            )

            for _, ruolo_slot in (
                posizioni
            ):

                possibili = (
                    giocatori_compatibili(
                        df_rosa,
                        ruolo_slot
                    )
                )

                _, percentuale_ruolo = (
                    percentuale_copertura_ruolo(
                        df_rosa,
                        ruolo_slot
                    )
                )

                colore_percentuale = (
                    "#dc2626"
                    if percentuale_ruolo < 60
                    else "#111827"
                )

                parti = [
                    (
                        f"<b>{html.escape(str(ruolo_slot))}</b> "
                        f"<font color='{colore_percentuale}'>"
                        f"<b>{round(percentuale_ruolo)}%</b>"
                        f"</font>"
                    )
                ]

                if possibili.empty:

                    parti.append(
                        "<font color='#dc2626'>-</font>"
                    )

                else:

                    for _, giocatore in (
                        possibili.iterrows()
                    ):

                        nome = html.escape(
                            str(
                                giocatore.get(
                                    "Nome",
                                    ""
                                )
                            )
                        )

                        ruoli_testo = html.escape(
                            str(
                                giocatore.get(
                                    "RM",
                                    ""
                                )
                            )
                        )

                        colore_nome = (
                            colore_fvm_mantra(
                                giocatore.get(
                                    "RM",
                                    ""
                                ),
                                giocatore.get(
                                    "FVM M"
                                )
                            )
                        )

                        parti.append(
                            (
                                f"<font color='{colore_nome}'>"
                                f"{nome} ({ruoli_testo})"
                                f"</font>"
                            )
                        )

                celle.append(
                    Paragraph(
                        "<br/>".join(
                            parti
                        ),
                        stile_slot
                    )
                )

            tab_linea = Table(
                [
                    celle
                ],
                colWidths=[
                    larghezza_cella
                    for _ in celle
                ]
            )

            tab_linea.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#ffffff")
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.HexColor("#e2e8f0")
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#e2e8f0")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ])
            )

            contenuto_campo.append(
                tab_linea
            )

            contenuto_campo.append(
                Spacer(
                    1,
                    3 * mm
                )
            )

        campo = Table(
            [
                [
                    contenuto_campo
                ]
            ],
            colWidths=[
                260 * mm
            ]
        )

        campo.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#16833a")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1.2,
                    colors.white
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm
                )
            ])
        )

        elementi.append(
            campo
        )

    # --------------------------------------------------------
    # NUMERO PAGINA
    # --------------------------------------------------------

    def aggiungi_numero_pagina(
        canvas,
        documento
    ):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            7
        )

        canvas.setFillColor(
            colors.HexColor(
                "#64748b"
            )
        )

        canvas.drawRightString(
            pagina[0]
            - 10 * mm,
            5 * mm,
            f"FANTAELEGANZA 26/27 - Pagina {documento.page}"
        )

        canvas.restoreState()

    doc.build(
        elementi,
        onFirstPage=aggiungi_numero_pagina,
        onLaterPages=aggiungi_numero_pagina
    )

    buffer.seek(
        0
    )

    return buffer.getvalue()


# ============================================================
# REGOLE ROSA
# ============================================================

def conta_portieri(df_rosa):

    if df_rosa is None:
        return 0

    if df_rosa.empty:
        return 0

    if "RM" not in df_rosa.columns:
        return 0

    return int(
        df_rosa["RM"]
        .apply(
            e_portiere
        )
        .sum()
    )


def verifica_acquisto_regole(
    df_rosa,
    nuovo_ruolo
):

    numero_attuale = len(
        df_rosa
    )

    portieri_attuali = (
        conta_portieri(
            df_rosa
        )
    )

    if numero_attuale >= MAX_GIOCATORI:

        return (
            False,
            "La rosa ha già raggiunto "
            f"il limite di {MAX_GIOCATORI} giocatori."
        )

    nuovo_e_portiere = (
        e_portiere(
            nuovo_ruolo
        )
    )

    numero_dopo = (
        numero_attuale
        + 1
    )

    portieri_dopo = (
        portieri_attuali
        + (
            1
            if nuovo_e_portiere
            else 0
        )
    )

    slot_rimanenti = (
        MAX_GIOCATORI
        - numero_dopo
    )

    portieri_necessari = max(
        0,
        MIN_PORTIERI
        - portieri_dopo
    )

    if (
        slot_rimanenti
        < portieri_necessari
    ):

        return (
            False,
            "Gli slot rimanenti devono "
            "essere riservati ai portieri."
        )

    return (
        True,
        ""
    )


# ============================================================
# COPERTURA RUOLO / MODULO
# ============================================================

def percentuale_copertura_ruolo(
    df_rosa,
    ruolo_posizione
):
    """
    100% = almeno 4 giocatori compatibili con quel ruolo/slot.
    La percentuale cresce linearmente:
    0 giocatori = 0%
    1 giocatore  = 25%
    2 giocatori  = 50%
    3 giocatori  = 75%
    4 o più      = 100%
    """

    possibili = giocatori_compatibili(
        df_rosa,
        ruolo_posizione
    )

    numero = len(
        possibili
    )

    percentuale = min(
        100.0,
        (
            numero
            / 4
        )
        * 100.0
    )

    return (
        numero,
        percentuale
    )


def qualita_media_ruolo_slot(
    df_rosa,
    ruolo_posizione
):
    """
    Qualità media (0-100) dei giocatori compatibili con uno slot.

    Usa lo stesso punteggio individuale dell'IQR:
    Verde 100 / Blu 70 / Rosso 40 / Nero 0-20.
    Se non esistono giocatori compatibili, la qualità è 0%.
    """

    possibili = giocatori_compatibili(
        df_rosa,
        ruolo_posizione
    )

    if possibili.empty:
        return 0.0

    punteggi = []

    for _, giocatore in possibili.iterrows():

        punteggi.append(
            punteggio_qualita_giocatore(
                giocatore.get(
                    "RM",
                    ""
                ),
                giocatore.get(
                    "FVM M"
                )
            )
        )

    if not punteggi:
        return 0.0

    return round(
        sum(
            punteggi
        )
        / len(
            punteggi
        ),
        1
    )


def colore_percentuale_copertura(
    percentuale
):
    """
    Rosso sotto il 60%, nero dal 60% in su.
    """

    if float(
        percentuale
        or 0
    ) < 60:
        return "#dc2626"

    return "#111827"


def calcola_copertura_modulo(
    df_rosa,
    nome_modulo
):

    totale_ruoli = 0
    ruoli_al_100 = 0
    somma_percentuali = 0.0

    for _, posizioni in MODULI[
        nome_modulo
    ]:

        for _, ruolo_slot in posizioni:

            totale_ruoli += 1

            numero, percentuale = (
                percentuale_copertura_ruolo(
                    df_rosa,
                    ruolo_slot
                )
            )

            somma_percentuali += (
                percentuale
            )

            if numero >= 4:
                ruoli_al_100 += 1

    percentuale_media = (
        somma_percentuali
        / totale_ruoli
        if totale_ruoli
        else 0
    )

    return (
        ruoli_al_100,
        totale_ruoli,
        percentuale_media
    )


def analizza_modulo(
    df_rosa,
    nome_modulo
):
    """
    Analisi strategica del modulo.

    Nuove definizioni:
    - SLOT SCOPERTO: slot con 2 o meno giocatori compatibili.
    - SLOT DEBOLE: slot che non raggiunge almeno 3 giocatori
      compatibili oppure non raggiunge almeno il 50% di qualità media.
      Gli slot allo 0% sono inclusi automaticamente tra i deboli.

    Il punteggio strategico considera:
    - copertura media;
    - penalità di profondità per gli slot scoperti;
    - penalità qualitativa per gli slot deboli.

    Penalità:
    - 6 punti per ogni slot scoperto;
    - 4 punti per ogni slot debole.
    """

    dati_slot = []

    for _, posizioni in MODULI[
        nome_modulo
    ]:

        for _, ruolo_slot in posizioni:

            numero, percentuale = (
                percentuale_copertura_ruolo(
                    df_rosa,
                    ruolo_slot
                )
            )

            qualita_media = (
                qualita_media_ruolo_slot(
                    df_rosa,
                    ruolo_slot
                )
            )

            dati_slot.append({
                "Ruolo": ruolo_slot,
                "Numero": int(
                    numero
                ),
                "Copertura": float(
                    percentuale
                ),
                "Qualita": float(
                    qualita_media
                )
            })

    if not dati_slot:

        return {
            "Modulo": nome_modulo,
            "Punteggio": 0.0,
            "Copertura media": 0.0,
            "Scoperti": 0,
            "Deboli": 0,
            "Ruoli deboli": "",
            "Al 100%": 0,
            "Totale slot": 0
        }

    copertura_media = (
        sum(
            s["Copertura"]
            for s in dati_slot
        )
        / len(
            dati_slot
        )
    )

    scoperti = sum(
        1
        for s in dati_slot
        if s["Numero"] <= 2
    )

    slot_deboli = [
        s
        for s in dati_slot
        if (
            s["Numero"] < 3
            or s["Qualita"] < 50
        )
    ]

    deboli = len(
        slot_deboli
    )

    ruoli_deboli = ", ".join(
        s["Ruolo"]
        for s in slot_deboli
    )

    al_100 = sum(
        1
        for s in dati_slot
        if s["Numero"] >= 4
    )

    penalita = (
        scoperti * 6
        + deboli * 4
    )

    punteggio = max(
        0.0,
        min(
            100.0,
            copertura_media
            - penalita
        )
    )

    return {
        "Modulo": nome_modulo,
        "Punteggio": round(
            punteggio,
            1
        ),
        "Copertura media": round(
            copertura_media,
            1
        ),
        "Scoperti": scoperti,
        "Deboli": deboli,
        "Ruoli deboli": ruoli_deboli,
        "Al 100%": al_100,
        "Totale slot": len(
            dati_slot
        )
    }

def classifica_moduli(
    df_rosa
):
    """
    Restituisce la classifica dei moduli dal più adatto al meno adatto.
    """

    risultati = [
        analizza_modulo(
            df_rosa,
            nome_modulo
        )
        for nome_modulo in MODULI
    ]

    risultati = sorted(
        risultati,
        key=lambda x: (
            -x["Punteggio"],
            x["Scoperti"],
            x["Deboli"],
            -x["Copertura media"],
            x["Modulo"]
        )
    )

    for posizione, risultato in enumerate(
        risultati,
        start=1
    ):

        risultato["Posizione"] = (
            posizione
        )

    return risultati



# ============================================================
# POPUP PRIORITÀ ACQUISTO
# ============================================================

@st.dialog(
    "Giocatori disponibili per ruolo",
    width="large"
)
def mostra_dettaglio_priorita_acquisto(
    giocatore,
    priorita,
    df_listone
):

    nome_giocatore = html.escape(
        str(
            giocatore.get(
                "Nome",
                ""
            )
        )
    )

    st.markdown(
        f"### {nome_giocatore}"
    )

    ruoli_candidato = sorted(
        ruoli_giocatore(
            giocatore.get(
                "RM",
                ""
            )
        ),
        key=lambda r: ORDINE_RUOLI.get(
            str(r).upper(),
            999
        )
    )

    if not ruoli_candidato:

        ruolo_principale = primo_ruolo(
            giocatore.get(
                "RM",
                ""
            )
        ).upper()

        if ruolo_principale:
            ruoli_candidato = [
                ruolo_principale
            ]

    if not ruoli_candidato:

        st.info(
            "Il giocatore selezionato non ha ruoli Mantra validi."
        )
        return

    st.caption(
        "Giocatori ancora disponibili, separati per ciascun ruolo "
        "Mantra del giocatore selezionato."
    )

    ordine_fasce = {
        "VERDE": 1,
        "BLU": 2,
        "ROSSO": 3,
        "NERO": 4
    }

    # Una colonna per ciascun ruolo: le tabelle vengono affiancate.
    colonne_ruolo = st.columns(
        len(
            ruoli_candidato
        ),
        gap="small"
    )

    for colonna, ruolo_riferimento in zip(
        colonne_ruolo,
        ruoli_candidato
    ):

        ruolo_riferimento = str(
            ruolo_riferimento
        ).strip().upper()

        with colonna:

            st.markdown(
                f"### {ruolo_riferimento}"
            )

            compatibili = giocatori_compatibili(
                df_listone,
                ruolo_riferimento
            )

            if (
                compatibili is None
                or compatibili.empty
            ):

                st.info(
                    "Nessun giocatore disponibile."
                )
                continue

            disponibili = (
                compatibili[
                    compatibili[
                        "Stato"
                    ]
                    .astype(str)
                    .str.upper()
                    == "DISPONIBILE"
                ]
                .copy()
            )

            if disponibili.empty:

                st.warning(
                    "Nessun giocatore disponibile."
                )
                continue

            # Manteniamo il criterio qualitativo per l'ordinamento,
            # ma non mostriamo più FVM e FASCIA nella tabella.
            disponibili[
                "_fascia"
            ] = disponibili.apply(
                lambda r:
                fascia_iqr_giocatore(
                    r.get(
                        "RM",
                        ""
                    ),
                    r.get(
                        "FVM M"
                    )
                ),
                axis=1
            )

            disponibili[
                "_ordine_fascia"
            ] = disponibili[
                "_fascia"
            ].map(
                ordine_fasce
            ).fillna(
                99
            )

            disponibili[
                "_fvm_m_num"
            ] = pd.to_numeric(
                disponibili[
                    "FVM M"
                ],
                errors="coerce"
            )

            disponibili = (
                disponibili
                .sort_values(
                    [
                        "_ordine_fascia",
                        "_fvm_m_num",
                        "Nome"
                    ],
                    ascending=[
                        True,
                        False,
                        True
                    ],
                    na_position="last"
                )
                .reset_index(
                    drop=True
                )
            )

            st.caption(
                f"{len(disponibili)} disponibili"
            )

            righe_html = []

            for _, riga in disponibili.iterrows():

                nome = html.escape(
                    str(
                        riga.get(
                            "Nome",
                            ""
                        )
                    )
                )

                squadra = html.escape(
                    str(
                        riga.get(
                            "Squadra",
                            ""
                        )
                    )
                )

                ruolo = html.escape(
                    str(
                        riga.get(
                            "RM",
                            ""
                        )
                    )
                )

                colore_nome = colore_fvm_mantra(
                    riga.get(
                        "RM",
                        ""
                    ),
                    riga.get(
                        "FVM M"
                    )
                )

                righe_html.append(
                    "<tr>"
                    f"<td style='padding:5px 6px;"
                    f"border:1px solid #e5e7eb;"
                    f"font-weight:800;"
                    f"font-size:0.78rem;"
                    f"color:{colore_nome};'>"
                    f"{nome}</td>"
                    f"<td style='padding:5px 6px;"
                    f"border:1px solid #e5e7eb;"
                    f"font-size:0.74rem;'>"
                    f"{squadra}</td>"
                    f"<td style='padding:5px 6px;"
                    f"border:1px solid #e5e7eb;"
                    f"font-size:0.74rem;"
                    f"text-align:center;'>"
                    f"{ruolo}</td>"
                    "</tr>"
                )

            tabella_html = (
                "<div style='overflow-x:auto;'>"
                "<table style='width:100%;"
                "border-collapse:collapse;"
                "table-layout:fixed;"
                "background:#ffffff;'>"
                "<colgroup>"
                "<col style='width:48%;'>"
                "<col style='width:32%;'>"
                "<col style='width:20%;'>"
                "</colgroup>"
                "<thead>"
                "<tr style='background:#071a2f;"
                "color:#ffffff;'>"
                "<th style='padding:6px;"
                "border:1px solid #d1d5db;"
                "font-size:0.72rem;"
                "text-align:left;'>"
                "GIOCATORE</th>"
                "<th style='padding:6px;"
                "border:1px solid #d1d5db;"
                "font-size:0.72rem;"
                "text-align:left;'>"
                "SQUADRA</th>"
                "<th style='padding:6px;"
                "border:1px solid #d1d5db;"
                "font-size:0.72rem;"
                "text-align:center;'>"
                "RUOLO</th>"
                "</tr>"
                "</thead>"
                "<tbody>"
                + "".join(
                    righe_html
                )
                + "</tbody>"
                "</table>"
                "</div>"
            )

            st.markdown(
                tabella_html,
                unsafe_allow_html=True
            )


# ============================================================
# POPUP IQR - INDICE QUALITÀ ROSA
# ============================================================

@st.dialog(
    "IQR - Indice Qualità Rosa",
    width="medium"
)
def mostra_dettaglio_iqr(
    valore_iqr,
    df_rosa
):

    try:
        valore_popup = float(
            valore_iqr
        )
    except Exception:
        valore_popup = 0.0

    valore_popup = max(
        0.0,
        min(
            100.0,
            valore_popup
        )
    )

    descrizione_popup = html.escape(
        descrizione_iqr(
            valore_popup
        )
    )

    colore_popup = colore_iqr(
        valore_popup
    )

    # Posizione reale del triangolo sulla scala 0-100.
    posizione_popup = max(
        1.5,
        min(
            98.5,
            valore_popup
        )
    )

    # ========================================================
    # CARD IQR POPUP
    # Tutta la grafica è INLINE per evitare interferenze CSS
    # di Streamlit e ottenere lo stesso risultato del mockup.
    # ========================================================

    popup_html = (
        '<div style="'
        'width:100%;'
        'max-width:560px;'
        'margin:0 auto 22px auto;'
        'padding:14px 18px 16px 18px;'
        'box-sizing:border-box;'
        'background:#0b3158;'
        'border-radius:12px;'
        'text-align:center;'
        '">'

        # ----- Titolo -----
        '<div style="'
        'display:flex;'
        'align-items:center;'
        'justify-content:center;'
        'gap:8px;'
        'margin:0 0 18px 0;'
        'white-space:nowrap;'
        '">'

        '<span style="'
        'color:#ffc21c;'
        'font-size:25px;'
        'line-height:1;'
        'font-weight:950;'
        '">★</span>'

        '<span style="'
        'color:#ffffff;'
        'font-size:22px;'
        'line-height:1;'
        'font-weight:950;'
        '">IQR</span>'

        f'<span style="'
        f'color:#ffc21c;'
        f'font-size:22px;'
        f'line-height:1;'
        f'font-weight:950;'
        f'">{valore_popup:.1f}%</span>'

        '</div>'

        # ----- Barra + triangolo -----
        '<div style="'
        'position:relative;'
        'width:82%;'
        'height:48px;'
        'margin:0 auto 10px auto;'
        'padding-top:14px;'
        'box-sizing:border-box;'
        '">'

        '<div style="'
        'width:100%;'
        'height:31px;'
        'display:flex;'
        'overflow:hidden;'
        'box-sizing:border-box;'
        '">'

        '<div style="'
        'width:40%;'
        'height:31px;'
        'background:#050505;'
        '"></div>'

        '<div style="'
        'width:25%;'
        'height:31px;'
        'background:#ff1616;'
        '"></div>'

        '<div style="'
        'width:20%;'
        'height:31px;'
        'background:#0b6df5;'
        '"></div>'

        '<div style="'
        'width:15%;'
        'height:31px;'
        'background:#16a34a;'
        '"></div>'

        '</div>'

        f'<div style="'
        f'position:absolute;'
        f'top:0;'
        f'left:{posizione_popup:.1f}%;'
        f'width:0;'
        f'height:0;'
        f'transform:translateX(-50%);'
        f'border-left:10px solid transparent;'
        f'border-right:10px solid transparent;'
        f'border-top:14px solid #ffffff;'
        f'"></div>'

        '</div>'

        # ----- Stato qualitativo -----
        f'<div style="'
        f'display:inline-block;'
        f'min-width:148px;'
        f'margin:0 auto;'
        f'padding:8px 18px;'
        f'box-sizing:border-box;'
        f'background:{colore_popup};'
        f'color:#ffffff;'
        f'font-size:22px;'
        f'line-height:1.05;'
        f'font-weight:950;'
        f'border-radius:7px;'
        f'">{descrizione_popup}</div>'

        '</div>'
    )

    st.markdown(
        popup_html,
        unsafe_allow_html=True
    )

    st.markdown(
        "### Come viene calcolato l'IQR"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            "**1. Qualità della rosa**"
        )

        st.caption(
            "Ogni giocatore vale in base alla fascia FVM M "
            "del primo ruolo Mantra: Verde 100, Blu 70, "
            "Rosso 40, Nero 0–20. Gli slot vuoti valgono 0."
        )

    with c2:

        st.markdown(
            "**2. Densità fasce alte**"
        )

        st.caption(
            "Premia il numero di giocatori Verdi e Blu. "
            "Riferimenti calibrati per una lega a 12: "
            "8 Verdi e 12 Verdi+Blu."
        )

    with c3:

        st.markdown(
            "**3. Bonus ruoli offensivi**"
        )

        st.caption(
            "Premia la presenza di Verdi/Blu nei ruoli "
            "Pc, A, W, T e C. Riferimenti: "
            "5 Verdi offensivi e 8 Verdi+Blu offensivi."
        )

    st.markdown(
        "### Dettaglio qualità per ruolo"
    )

    dettaglio = (
        dettaglio_iqr_per_ruolo(
            df_rosa
        )
    )

    if dettaglio.empty:

        st.info(
            "La rosa è ancora vuota."
        )

    else:

        # Colora esclusivamente la cella "Qualità media"
        # secondo la scala qualitativa IQR.
        def stile_cella_qualita_media(
            valore
        ):

            try:
                numero = float(
                    str(
                        valore
                    )
                    .replace(
                        "%",
                        ""
                    )
                    .replace(
                        ",",
                        "."
                    )
                    .strip()
                )
            except Exception:
                numero = 0.0

            if numero > 85.0:
                sfondo = "#16a34a"

            elif numero > 65.0:
                sfondo = "#0b6df5"

            elif numero > 40.0:
                sfondo = "#ff1616"

            else:
                sfondo = "#050505"

            return (
                f"background-color:{sfondo};"
                "color:#ffffff;"
                "font-weight:900;"
                "text-align:center;"
            )

        dettaglio_stilizzato = (
            dettaglio.style
            .map(
                stile_cella_qualita_media,
                subset=[
                    "Qualità media"
                ]
            )
        )

        st.dataframe(
            dettaglio_stilizzato,
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        "### Scala qualitativa"
    )

    st.markdown(
        """
- **0–40%** — Rosa debole
- **40,1–65%** — Rosa buona
- **65,1–85%** — Rosa forte
- **>85%** — Rosa eccellente
        """
    )

    st.info(
        "L'IQR è un indicatore sintetico pensato per una lega a 12: "
        "combina qualità complessiva, densità di fasce alte e "
        "forza dei ruoli offensivi. "
        "30 giocatori Verdi = 100%; "
        "30 giocatori con FVM M = 1 = 0%."
    )


# ============================================================
# POPUP REGOLE
# ============================================================

@st.dialog(
    "Regole FANTAELEGANZA"
)
def mostra_regole():

    st.markdown(
        """
**Regole attualmente gestite dall'app**

- Soglia economica: **500,00 €**
- Parte eccedente 500 €: **moltiplicatore ×3**
- Massimo rosa: **30 giocatori**
- Minimo portieri: **2**
- Lo svincolo non recupera il costo sostenuto
- Sono annullabili le ultime **10 operazioni**
        """
    )


# ============================================================
# POPUP ANNULLA ACQUISTO
# ============================================================

@st.dialog(
    "Conferma annullamento"
)
def conferma_annullamento(
    giocatore_id,
    nome_giocatore
):

    st.write(
        f'Annullare l\'acquisto di '
        f'**"{nome_giocatore}"**?'
    )

    st.caption(
        "Il prezzo verrà eliminato "
        "dalla spesa."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key=f"ok_annulla_{giocatore_id}"
        ):

            esegui_operazione(
                giocatore_id,
                "ANNULLA ACQUISTO",
                "DISPONIBILE",
                None,
                0
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_annulla_{giocatore_id}"
        ):

            st.rerun()


# ============================================================
# POPUP MODIFICA PREZZO ACQUISTO
# ============================================================

@st.dialog(
    "Conferma modifica prezzo"
)
def conferma_modifica_prezzo(
    giocatore_id,
    nome_giocatore,
    prezzo_vecchio,
    prezzo_nuovo
):

    prezzo_vecchio = float(
        prezzo_vecchio
        or 0
    )

    prezzo_nuovo = float(
        prezzo_nuovo
        or 0
    )

    st.write(
        f'Modificare il prezzo di acquisto di '
        f'**"{nome_giocatore}"**?'
    )

    st.info(
        f"Prezzo attuale: **{formatta_crediti(prezzo_vecchio)} €**  \n"
        f"Nuovo prezzo: **{formatta_crediti(prezzo_nuovo)} €**"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "CONFERMA",
            type="primary",
            use_container_width=True,
            key=f"ok_modifica_prezzo_{giocatore_id}"
        ):

            esegui_operazione(
                int(
                    giocatore_id
                ),
                "MODIFICA PREZZO",
                "MIO",
                float(
                    prezzo_nuovo
                ),
                0
            )

            st.session_state.pop(
                f"prezzo_rosa_mobile_{giocatore_id}",
                None
            )

            st.session_state.pop(
                f"prezzo_rosa_desktop_{giocatore_id}",
                None
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_modifica_prezzo_{giocatore_id}"
        ):

            st.session_state[
                f"prezzo_rosa_mobile_{giocatore_id}"
            ] = float(
                prezzo_vecchio
            )

            st.session_state[
                f"prezzo_rosa_desktop_{giocatore_id}"
            ] = float(
                prezzo_vecchio
            )

            st.rerun()


# ============================================================
# POPUP SVINCOLO
# ============================================================

@st.dialog(
    "Conferma svincolo"
)
def conferma_svincolo(
    giocatore_id,
    nome_giocatore,
    prezzo_giocatore
):

    prezzo = float(
        prezzo_giocatore
        or 0
    )

    st.write(
        f'Svincolare '
        f'**"{nome_giocatore}"**?'
    )

    st.warning(
        "Il giocatore tornerà disponibile, "
        "ma i "
        f"**{formatta_crediti(prezzo)} €** "
        "spesi resteranno conteggiati."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key=f"ok_svincolo_{giocatore_id}"
        ):

            esegui_operazione(
                giocatore_id,
                "SVINCOLO",
                "DISPONIBILE",
                None,
                prezzo
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_svincolo_{giocatore_id}"
        ):

            st.rerun()


# ============================================================
# POPUP RIPRISTINO AVVERSARIO
# ============================================================

@st.dialog(
    "Ripristina giocatore"
)
def conferma_ripristino_avversario(
    giocatore_id,
    nome_giocatore
):

    st.write(
        f'Rendere nuovamente disponibile '
        f'**"{nome_giocatore}"**?'
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key=f"ok_ripristina_{giocatore_id}"
        ):

            esegui_operazione(
                giocatore_id,
                "RIPRISTINO AVVERSARIO",
                "DISPONIBILE",
                None,
                0
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_ripristina_{giocatore_id}"
        ):

            st.rerun()


# ============================================================
# POPUP UNDO
# ============================================================

@st.dialog(
    "Annulla ultima operazione"
)
def conferma_undo():

    operazioni = (
        carica_ultime_operazioni()
    )

    if operazioni.empty:

        st.info(
            "Non ci sono operazioni "
            "da annullare."
        )

        return

    ultima = (
        operazioni.iloc[0]
    )

    st.write(
        "Vuoi annullare "
        "l'ultima operazione?"
    )

    st.warning(
        f"**{ultima['Operazione']}** — "
        f"{ultima['Giocatore']}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key="ok_undo"
        ):

            annulla_ultima_operazione()

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key="no_undo"
        ):

            st.rerun()


# ============================================================
# POPUP SNAPSHOT
# ============================================================

@st.dialog(
    "Snapshot e ripristino"
)
def gestisci_snapshot():

    st.caption(
        "FANTAELEGANZA usa la cronologia UNDO per le normali "
        "operazioni di asta e conserva gli snapshot completi "
        "per i passaggi più delicati, come import listone e ripristino. "
        f"Puoi inoltre crearli manualmente. "
        f"Vengono conservati gli ultimi {MAX_SNAPSHOT} snapshot."
    )

    c1, c2 = st.columns(
        2
    )

    with c1:

        if st.button(
            "📸 CREA SNAPSHOT ORA",
            use_container_width=True,
            key="snapshot_manual"
        ):

            creato = (
                crea_snapshot_database(
                    "MANUALE"
                )
            )

            if creato is not None:

                st.success(
                    "Snapshot creato correttamente."
                )

                st.rerun()

    with c2:

        if st.button(
            "🔄 AGGIORNA ELENCO",
            use_container_width=True,
            key="snapshot_refresh"
        ):

            st.rerun()

    snapshots = (
        elenco_snapshot(PROFILO_ATTIVO)
    )

    if not snapshots:

        st.info(
            "Non ci sono ancora snapshot."
        )

        return

    opzioni = []
    mappa = {}

    for elemento in snapshots:

        etichetta = (
            f"{elemento['data']} — "
            f"{elemento['motivo']}"
        )

        opzioni.append(
            etichetta
        )

        mappa[
            etichetta
        ] = (
            elemento[
                "path"
            ]
        )

    scelta = st.selectbox(
        "Snapshot da ripristinare",
        opzioni,
        key="snapshot_select"
    )

    st.warning(
        "Il ripristino sostituirà lo stato attuale "
        "dell'asta. Prima del ripristino verrà "
        "salvato automaticamente anche lo stato corrente."
    )

    conferma = st.checkbox(
        "Confermo il ripristino dello snapshot selezionato",
        key="snapshot_confirm"
    )

    if st.button(
        "⏪ RIPRISTINA SNAPSHOT",
        type="primary",
        use_container_width=True,
        disabled=not conferma,
        key="snapshot_restore"
    ):

        try:

            ripristina_snapshot_database(
                mappa[
                    scelta
                ]
            )

            st.success(
                "Snapshot ripristinato correttamente."
            )

            st.rerun()

        except Exception as errore:

            st.error(
                f"Errore durante il ripristino: {errore}"
            )


# ============================================================
# POPUP BACKUP CLOUD
# ============================================================

@st.dialog(
    "Backup database"
)
def gestisci_backup_cloud():

    st.caption(
        "Il backup viene generato solo quando lo richiedi, "
        "così la normale navigazione dell'app non interroga "
        "inutilmente il database Cloud."
    )

    if "backup_cloud_bytes" not in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if st.session_state.backup_cloud_bytes is None:

        if st.button(
            "☁ PREPARA BACKUP",
            use_container_width=True,
            type="primary",
            key="prepara_backup_cloud"
        ):

            with st.spinner(
                "Preparazione backup..."
            ):

                st.session_state.backup_cloud_bytes = (
                    crea_backup_logico_bytes()
                )

            st.rerun()

    else:

        st.success(
            "Backup pronto."
        )

        st.download_button(
            "⬇ SCARICA BACKUP",
            data=(
                st.session_state.backup_cloud_bytes
            ),
            file_name=(
                "fantaeleganza_backup_cloud.json"
            ),
            mime=(
                "application/json"
            ),
            use_container_width=True,
            key="scarica_backup_cloud"
        )

        if st.button(
            "🔄 GENERA NUOVO BACKUP",
            use_container_width=True,
            key="rigenera_backup_cloud"
        ):

            st.session_state.backup_cloud_bytes = None
            st.rerun()


# ============================================================
# INIZIALIZZAZIONE
# ============================================================

if PROFILO_LEGACY_SUPPORTATO:

    inizializza_database(
        PROFILO_ATTIVO
    )

# ------------------------------------------------------------
# MULTILEGA 0.3 - FAST BOOT
# ------------------------------------------------------------
# V84 eseguiva CREATE TABLE + sincronizzazione legacy ad ogni rerun.
# Con DB cloud questo significava molti round-trip ad ogni click
# e poteva facilmente portare i cambi pagina a 15-20 secondi.
#
# Da V85 la foundation viene inizializzata UNA SOLA VOLTA
# per sessione/profilo. I normali cambi sezione non rifanno
# migrazione e DDL.

_ml_boot_key = (
    "ml03_boot_"
    + PROFILO_ATTIVO
)

if not st.session_state.get(
    _ml_boot_key,
    False
):

    try:

        inizializza_database_multilega()

        if PROFILO_LEGACY_SUPPORTATO:

            sincronizza_legacy_in_multilega()

        st.session_state[
            _ml_boot_key
        ] = True

        st.session_state.pop(
            "ml_foundation_error",
            None
        )

    except Exception as errore_multilega:

        st.session_state[
            "ml_foundation_error"
        ] = str(
            errore_multilega
        )


# Gli accessi vengono letti dal DB solo quando servono.
# Una volta selezionata la lega, la membership validata è mantenuta
# nel session_state server-side e non viene ri-queryata a ogni click.
ACCESSO_MULTILEGA_ATTIVO = (
    st.session_state.get(
        "ml_accesso_validato"
    )
)

if ACCESSO_MULTILEGA_ATTIVO is None:

    try:

        ACCESSI_MULTILEGA = (
            elenca_accessi_multilega(
                PROFILO_ATTIVO
            )
        )

    except Exception as errore_accessi:

        st.error(
            "Impossibile leggere le associazioni dell'utente alle leghe."
        )

        st.exception(
            errore_accessi
        )

        st.stop()

    accesso_sessione = (
        accesso_multilega_corrente()
    )

    if accesso_sessione is None:

        azzera_contesto_multilega()

        schermata_le_mie_leghe(
            ACCESSI_MULTILEGA
        )

    ACCESSO_MULTILEGA_ATTIVO = (
        accesso_sessione
    )

    st.session_state[
        "ml_accesso_validato"
    ] = dict(
        ACCESSO_MULTILEGA_ATTIVO
    )


applica_accesso_multilega(
    ACCESSO_MULTILEGA_ATTIVO
)

# ============================================================
# MULTILEGA 1.4 - ISOLAMENTO TEAM / LEGA
# ============================================================
# Da questo punto in poi tutte le query legacy-compatibili dei nuovi
# utenti vengono instradate esclusivamente nel workspace della coppia
# league_id/team_id validata dal database.

if not PROFILO_LEGACY_SUPPORTATO:

    imposta_workspace_team_multilega()

    verifica_isolamento_workspace()

    inizializza_workspace_team_multilega()

LEGA_ATTIVA_NOME = (
    st.session_state.get(
        "ml_league_nome",
        ""
    )
)

TEAM_ATTIVO_NOME = (
    st.session_state.get(
        "ml_team_nome",
        ""
    )
)

RUOLI_ATTIVI = (
    st.session_state.get(
        "ml_ruoli",
        []
    )
)

_workspace_runtime_key = (
    str(
        st.session_state.get(
            "ml_league_id",
            ""
        )
    )
    + ":"
    + str(
        st.session_state.get(
            "ml_team_id",
            ""
        )
    )
)

if (
    st.session_state.get(
        "ml_runtime_workspace_key"
    )
    != _workspace_runtime_key
):

    st.session_state[
        "ml_runtime_workspace_key"
    ] = _workspace_runtime_key

    for _chiave_workspace in [
        "budget_asta_corrente",
        "budget_asta_input",
        "_titolarita_cache",
        "_formazioni_tipo_fast_cache",
        "_ml16_sidebar_metrics"
    ]:

        st.session_state.pop(
            _chiave_workspace,
            None
        )

SEZIONE_PRE_NAV = st.session_state.get("pagina", "DASHBOARD")
SEZIONE_OPERATIVA = SEZIONE_PRE_NAV not in ("GESTIONE LEGA", "PROFILO", "BANDITORE")

if SEZIONE_OPERATIVA:
    if "budget_asta_corrente" not in st.session_state:

        st.session_state[
            "budget_asta_corrente"
        ] = (
            leggi_budget_asta()
        )

    if "budget_asta_input" not in st.session_state:

        st.session_state[
            "budget_asta_input"
        ] = (
            st.session_state[
                "budget_asta_corrente"
            ]
        )

    df_completo = carica_tutti_giocatori()

    df_rosa_globale = (
        df_completo[df_completo["Stato"] == "MIO"].copy()
    )

    _prezzi_rosa = pd.to_numeric(
        df_rosa_globale.get("Prezzo", pd.Series(dtype=float)),
        errors="coerce"
    ).fillna(0)

    _runtime_signature = (
        _workspace_runtime_key,
        int(len(df_rosa_globale)),
        round(float(_prezzi_rosa.sum()), 2),
        tuple(sorted(int(x) for x in df_rosa_globale.get("Id", pd.Series(dtype=int)).tolist()))
    )

    _runtime_cached = st.session_state.get("_ml16_sidebar_metrics")

    if isinstance(_runtime_cached, dict) and _runtime_cached.get("signature") == _runtime_signature:
        valore_attivi = _runtime_cached["valore_attivi"]
        costi_svincoli = _runtime_cached["costi_svincoli"]
        valore_acquisti = _runtime_cached["valore_acquisti"]
        spesa_effettiva = _runtime_cached["spesa_effettiva"]
        oltre_soglia = _runtime_cached["oltre_soglia"]
        numero_rosa = _runtime_cached["numero_rosa"]
        numero_portieri = _runtime_cached["numero_portieri"]
        slot_liberi = _runtime_cached["slot_liberi"]
        iqr = _runtime_cached["iqr"]
    else:
        valore_attivi = round(float(_prezzi_rosa.sum()), 2)
        costi_svincoli = calcola_costi_svincoli()
        valore_acquisti = round(valore_attivi + costi_svincoli, 2)
        spesa_effettiva = calcola_spesa_effettiva(valore_acquisti)
        oltre_soglia = round(max(0, valore_acquisti - SOGLIA_BASE), 2)
        numero_rosa = len(df_rosa_globale)
        numero_portieri = conta_portieri(df_rosa_globale)
        slot_liberi = max(0, MAX_GIOCATORI - numero_rosa)
        iqr = calcola_iqr(df_rosa_globale, df_completo, MAX_GIOCATORI)

        st.session_state["_ml16_sidebar_metrics"] = {
            "signature": _runtime_signature,
            "valore_attivi": valore_attivi,
            "costi_svincoli": costi_svincoli,
            "valore_acquisti": valore_acquisti,
            "spesa_effettiva": spesa_effettiva,
            "oltre_soglia": oltre_soglia,
            "numero_rosa": numero_rosa,
            "numero_portieri": numero_portieri,
            "slot_liberi": slot_liberi,
            "iqr": iqr,
        }

    budget_asta = float(
        st.session_state.get("budget_asta_corrente", SOGLIA_BASE)
    )

    budget_rimanente = round(budget_asta - spesa_effettiva, 2)
else:
    # Le sezioni Profilo/Gestione Lega non richiedono listone, rosa,
    # cronologia economica o calcolo IQR.
    df_completo = pd.DataFrame()
    df_rosa_globale = pd.DataFrame()
    valore_attivi = 0.0
    costi_svincoli = 0.0
    valore_acquisti = 0.0
    spesa_effettiva = 0.0
    oltre_soglia = 0.0
    numero_rosa = 0
    numero_portieri = 0
    slot_liberi = MAX_GIOCATORI
    iqr = 0.0
    budget_asta = float(st.session_state.get("budget_asta_corrente", SOGLIA_BASE))
    budget_rimanente = budget_asta


# ============================================================
# SIDEBAR PRINCIPALE
# ============================================================

st.markdown(
    """
    <style>
    /* ======================================================
       SIDEBAR FISSA: NON COLLASSABILE
       ====================================================== */

    /* Nasconde il pulsante di chiusura/collasso dentro la sidebar */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Alcune versioni Streamlit usano un button header senza testid specifico */
    section[data-testid="stSidebar"]
    button[kind="header"],
    section[data-testid="stSidebar"]
    button[kind="headerNoPadding"],
    section[data-testid="stSidebar"]
    button[data-testid="stBaseButton-header"],
    section[data-testid="stSidebar"]
    button[data-testid="stBaseButton-headerNoPadding"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Forza la sidebar a rimanere visibile e nella sua posizione */
    section[data-testid="stSidebar"] {
        transform: none !important;
        margin-left: 0 !important;
        visibility: visible !important;
        display: block !important;
        left: 0 !important;
    }

    /* Evita che compaia il controllo flottante per riaprirla */
    div[data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Sidebar principale */
    section[data-testid="stSidebar"] {
        width: 320px !important;
        min-width: 320px !important;
        background: #f4f7fb !important;
        border-right: 1px solid #dbe3ec !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 12px !important;
    }

    section[data-testid="stSidebar"] .fanta-header {
        margin: 0 0 12px 0 !important;
        width: 100% !important;
        min-height: 92px !important;
        border-radius: 14px !important;
        box-sizing: border-box !important;
    }

    /* Profilo */
    .sidebar-profile {
        text-align:center;
        font-size:.82rem;
        font-weight:900;
        color:#475569;
        padding:2px 0 4px 0;
    }

    /* Metriche sidebar uniformi */
    section[data-testid="stSidebar"] div[data-testid="stMetric"] {
        background:#ffffff !important;
        border:1px solid #dbe3ec !important;
        border-radius:12px !important;
        padding:10px 12px !important;
        min-height:82px !important;
        box-shadow:0 1px 3px rgba(15,23,42,.04) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetric"] label {
        font-size:.78rem !important;
        font-weight:800 !important;
        color:#475569 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size:1.35rem !important;
        font-weight:850 !important;
        color:#0f172a !important;
    }

    /* Budget: stessa presenza grafica delle metriche */
    div[class*="st-key-sidebar_budget_card"] {
        background:#ffffff !important;
        border:1px solid #dbe3ec !important;
        border-radius:12px !important;
        padding:7px 10px 8px 10px !important;
        min-height:82px !important;
        box-sizing:border-box !important;
        box-shadow:0 1px 3px rgba(15,23,42,.04) !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] {
        margin:0 !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] label {
        font-size:.78rem !important;
        font-weight:800 !important;
        color:#475569 !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] input {
        font-size:1.25rem !important;
        font-weight:850 !important;
        min-height:38px !important;
        border:0 !important;
        background:#f8fafc !important;
        box-shadow:none !important;
    }

    /* Menu strumenti: visibile solo il bottone di apertura */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button {
        width:100% !important;
        min-height:38px !important;
        font-weight:850 !important;
        border-radius:9px !important;
    }

    /* IQR uniformato alla sidebar */
    section[data-testid="stSidebar"] div[class*="st-key-iqr_card_clickable"] {
        min-height:132px !important;
        background:#ffffff !important;
        border:1px solid #dbe3ec !important;
        border-radius:12px !important;
        margin-top:0 !important;
    }

    @media (max-width: 850px) {
        section[data-testid="stSidebar"] {
            width: 290px !important;
            min-width: 290px !important;
        }
    }

    /* ======================================================
       V39 - SIDEBAR BLU / BIANCO / GIALLO
       ====================================================== */

    :root {
        --fe-navy: #061f3a;
        --fe-navy-2: #082b50;
        --fe-card: #0b3158;
        --fe-card-2: #0a2b4d;
        --fe-border: #165387;
        --fe-gold: #ffc21c;
        --fe-white: #ffffff;
        --fe-soft: #c9d9ea;
    }

    section[data-testid="stSidebar"] {
        width: 390px !important;
        min-width: 390px !important;
        background:
            linear-gradient(
                180deg,
                #061f3a 0%,
                #062744 50%,
                #041b32 100%
            ) !important;
        border-right: 1px solid #0f426f !important;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
        padding:
            14px 16px 18px 16px !important;
    }

    /* Nasconde eventuali superfici bianche residue della sidebar */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: transparent;
    }

    /* ------------------------------------------------------
       TESTATA
       ------------------------------------------------------ */

    section[data-testid="stSidebar"] .fanta-header {
        width: 100% !important;
        min-height: 126px !important;
        margin: 0 0 12px 0 !important;
        padding: 15px 17px !important;

        background:
            linear-gradient(
                105deg,
                #06213d 0%,
                #082b4f 100%
            ) !important;

        border:
            2px solid var(--fe-gold) !important;

        border-radius: 18px !important;

        box-shadow:
            0 8px 22px rgba(0,0,0,.16) !important;

        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] .fanta-brand {
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        width: 100% !important;
        min-width: 0 !important;
    }

    section[data-testid="stSidebar"] .fanta-logo {
        width: 76px !important;
        height: 76px !important;
        min-width: 76px !important;

        border:
            3px solid var(--fe-gold) !important;

        border-radius: 17px !important;

        background:
            #ffffff !important;
    }

    section[data-testid="stSidebar"] .fanta-brand > div:last-child {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-title {
        color: var(--fe-white) !important;
        font-size: 27px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        letter-spacing: .1px !important;

        white-space: normal !important;
        overflow: visible !important;
        word-break: normal !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-title span {
        color: var(--fe-gold) !important;
        display: inline !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-subtitle {
        color: var(--fe-white) !important;
        font-size: 14px !important;
        margin-top: 7px !important;
        font-weight: 500 !important;
    }

    /* ------------------------------------------------------
       PROFILO
       ------------------------------------------------------ */

    .sidebar-profile {
        width: 100% !important;
        min-height: 60px !important;
        box-sizing: border-box !important;

        display: flex !important;
        align-items: center !important;

        padding: 0 16px !important;
        margin: 0 0 12px 0 !important;

        border-radius: 14px !important;

        background:
            linear-gradient(
                90deg,
                #0a345f 0%,
                #0b3a69 100%
            ) !important;

        border:
            1px solid rgba(62,132,190,.30) !important;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.03) !important;
    }

    .sidebar-profile-icon {
        color: var(--fe-gold) !important;
        font-size: 21px !important;
        margin-right: 11px !important;
    }

    .sidebar-profile-name {
        flex: 1 !important;
        text-align: left !important;

        color: var(--fe-white) !important;

        font-size: 16px !important;
        font-weight: 900 !important;

        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    .sidebar-profile-arrow {
        color: var(--fe-white) !important;
        font-size: 25px !important;
        line-height: 1 !important;
        margin-left: 8px !important;
    }

    /* ------------------------------------------------------
       CARD METRICHE
       ------------------------------------------------------ */

    section[data-testid="stSidebar"] div[data-testid="stMetric"] {
        min-height: 102px !important;

        margin-bottom: 8px !important;

        padding:
            14px 17px !important;

        background:
            linear-gradient(
                100deg,
                var(--fe-card) 0%,
                var(--fe-card-2) 100%
            ) !important;

        border:
            1px solid var(--fe-border) !important;

        border-radius:
            15px !important;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.025) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetricLabel"],
    section[data-testid="stSidebar"] div[data-testid="stMetric"] label {
        color: var(--fe-white) !important;

        font-size: 15px !important;
        line-height: 1.15 !important;

        font-weight: 850 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetricLabel"] *,
    section[data-testid="stSidebar"] div[data-testid="stMetric"] label * {
        color: inherit !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stMetricValue"] {
        color: var(--fe-gold) !important;

        font-size: 29px !important;
        line-height: 1.05 !important;

        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stMetricDelta"] {
        color: var(--fe-soft) !important;
        font-size: 11px !important;
    }

    /* ------------------------------------------------------
       BUDGET
       ------------------------------------------------------ */

    div[class*="st-key-sidebar_budget_card"] {
        min-height: 102px !important;

        margin-bottom: 8px !important;

        padding:
            10px 14px 12px 14px !important;

        background:
            linear-gradient(
                100deg,
                var(--fe-card) 0%,
                var(--fe-card-2) 100%
            ) !important;

        border:
            1px solid var(--fe-border) !important;

        border-radius:
            15px !important;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.025) !important;
    }

    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] label {
        color: var(--fe-white) !important;

        font-size: 15px !important;
        font-weight: 850 !important;
    }

    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] label * {
        color: inherit !important;
    }

    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] > div {
        background: transparent !important;
    }

    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] input {
        height: 48px !important;

        background:
            #0a2a4b !important;

        color:
            var(--fe-gold) !important;

        border:
            1px solid #174f7e !important;

        border-radius:
            10px !important;

        font-size:
            24px !important;

        font-weight:
            950 !important;

        box-shadow:
            none !important;
    }

    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button {
        width:
            46px !important;

        height:
            46px !important;

        min-height:
            46px !important;

        padding:
            0 !important;

        background:
            #124776 !important;

        color:
            var(--fe-white) !important;

        border:
            0 !important;

        border-radius:
            50% !important;

        box-shadow:
            none !important;
    }

    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button * {
        color:
            var(--fe-white) !important;
    }

    /* ------------------------------------------------------
       IQR
       ------------------------------------------------------ */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"] {
        min-height: 148px !important;

        margin:
            0 0 9px 0 !important;

        padding:
            12px 14px !important;

        background:
            linear-gradient(
                100deg,
                var(--fe-card) 0%,
                var(--fe-card-2) 100%
            ) !important;

        border:
            1px solid var(--fe-border) !important;

        border-radius:
            15px !important;
    }

    section[data-testid="stSidebar"]
    .iqr-gauge-title {
        color:
            var(--fe-white) !important;

        font-size:
            15px !important;

        font-weight:
            900 !important;
    }

    section[data-testid="stSidebar"]
    .iqr-gauge-value {
        color:
            var(--fe-gold) !important;

        font-size:
            27px !important;

        font-weight:
            950 !important;
    }

    section[data-testid="stSidebar"]
    .iqr-gauge-hint {
        color:
            #8fb1cf !important;
    }

    /* ------------------------------------------------------
       MENU COLLASSABILE
       ------------------------------------------------------ */

    section[data-testid="stSidebar"]
    details {
        background:
            transparent !important;

        border:
            0 !important;

        margin-top:
            5px !important;
    }

    section[data-testid="stSidebar"]
    details > summary {
        min-height:
            52px !important;

        box-sizing:
            border-box !important;

        display:
            flex !important;

        align-items:
            center !important;

        padding:
            0 16px !important;

        background:
            #082744 !important;

        color:
            var(--fe-gold) !important;

        border:
            2px solid var(--fe-gold) !important;

        border-radius:
            14px !important;

        font-size:
            17px !important;

        font-weight:
            950 !important;
    }

    section[data-testid="stSidebar"]
    details > summary * {
        color:
            var(--fe-gold) !important;
    }

    section[data-testid="stSidebar"]
    details[open] {
        padding-bottom:
            10px !important;

        background:
            rgba(8,43,80,.72) !important;

        border:
            1px solid #164b78 !important;

        border-radius:
            14px !important;
    }

    section[data-testid="stSidebar"]
    details[open] > summary {
        margin-bottom:
            10px !important;

        border-radius:
            13px !important;
    }

    /* Pulsanti presenti SOLO nel menu laterale */
    section[data-testid="stSidebar"]
    details .stButton > button,
    section[data-testid="stSidebar"]
    details .stDownloadButton > button {
        min-height:
            42px !important;

        height:
            auto !important;

        background:
            transparent !important;

        color:
            var(--fe-white) !important;

        border:
            1px solid transparent !important;

        border-radius:
            8px !important;

        font-size:
            14px !important;

        font-weight:
            650 !important;

        text-align:
            left !important;

        justify-content:
            flex-start !important;

        padding:
            7px 10px !important;

        box-shadow:
            none !important;
    }

    section[data-testid="stSidebar"]
    details .stButton > button:hover,
    section[data-testid="stSidebar"]
    details .stDownloadButton > button:hover {
        background:
            #10446f !important;

        border-color:
            #1d5b91 !important;
    }

    section[data-testid="stSidebar"]
    details .stButton > button *,
    section[data-testid="stSidebar"]
    details .stDownloadButton > button * {
        color:
            inherit !important;
    }

    section[data-testid="stSidebar"]
    details [data-testid="stToggle"] label,
    section[data-testid="stSidebar"]
    details [data-testid="stToggle"] span,
    section[data-testid="stSidebar"]
    details p {
        color:
            var(--fe-white) !important;
    }

    /* ------------------------------------------------------
       GENERALE TESTI SIDEBAR
       ------------------------------------------------------ */

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color:
            var(--fe-white);
    }

    @media (max-width: 950px) {
        section[data-testid="stSidebar"] {
            width: 345px !important;
            min-width: 345px !important;
        }

        section[data-testid="stSidebar"] .fanta-brand-title {
            font-size:
                23px !important;
        }

        section[data-testid="stSidebar"] .fanta-logo {
            width:
                68px !important;

            height:
                68px !important;

            min-width:
                68px !important;
        }
    }

    /* ======================================================
       V42 — LAYOUT SIDEBAR IDENTICO AL MOCKUP
       tutto visibile senza scroll
       ====================================================== */

    section[data-testid="stSidebar"] {
        width: 365px !important;
        min-width: 365px !important;
        height: 100vh !important;
        overflow: hidden !important;
        background:
            linear-gradient(
                180deg,
                #051d36 0%,
                #062846 54%,
                #041b31 100%
            ) !important;
    }

    section[data-testid="stSidebar"] > div {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        padding: 10px 13px 8px 13px !important;
        box-sizing: border-box !important;
    }

    /* HEADER */
    section[data-testid="stSidebar"] .fanta-header {
        min-height: 100px !important;
        height: 100px !important;
        margin: 0 0 8px 0 !important;
        padding: 10px 13px !important;
        border: 2px solid var(--fe-gold) !important;
        border-radius: 16px !important;
    }

    section[data-testid="stSidebar"] .fanta-brand {
        gap: 12px !important;
    }

    section[data-testid="stSidebar"] .fanta-logo {
        width: 62px !important;
        height: 62px !important;
        min-width: 62px !important;
        border-width: 2px !important;
        border-radius: 14px !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-title {
        font-size: 22px !important;
        line-height: .98 !important;
        white-space: normal !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-subtitle {
        font-size: 11px !important;
        margin-top: 4px !important;
    }

    /* PROFILO */
    .sidebar-profile {
        min-height: 43px !important;
        height: 43px !important;
        margin-bottom: 7px !important;
        padding: 0 12px !important;
        border-radius: 12px !important;
    }

    .sidebar-profile-icon {
        font-size: 16px !important;
        margin-right: 8px !important;
    }

    .sidebar-profile-name {
        font-size: 13px !important;
    }

    .sidebar-profile-arrow {
        font-size: 21px !important;
    }

    /* CARD METRICHE: ridotte ma leggibili */
    section[data-testid="stSidebar"] div[data-testid="stMetric"] {
        min-height: 63px !important;
        height: 63px !important;
        margin-bottom: 5px !important;
        padding: 7px 12px !important;
        border-radius: 12px !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetricLabel"],
    section[data-testid="stSidebar"] div[data-testid="stMetric"] label {
        font-size: 11.5px !important;
        line-height: 1.05 !important;
        font-weight: 850 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        line-height: 1 !important;
        margin-top: 2px !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetricDelta"] {
        font-size: 8px !important;
        line-height: 1 !important;
    }

    /* BUDGET */
    div[class*="st-key-sidebar_budget_card"] {
        min-height: 69px !important;
        height: 69px !important;
        margin-bottom: 5px !important;
        padding: 5px 9px 6px 9px !important;
        border-radius: 12px !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] {
        margin: 0 !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] label {
        font-size: 11.5px !important;
        line-height: 1 !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] input {
        height: 35px !important;
        min-height: 35px !important;
        font-size: 18px !important;
        border-radius: 8px !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] button {
        width: 32px !important;
        height: 32px !important;
        min-height: 32px !important;
        border-radius: 50% !important;
        padding: 0 !important;
    }

    /* IQR RIDOTTO */
    section[data-testid="stSidebar"] div[class*="st-key-iqr_card_clickable"] {
        min-height: 90px !important;
        height: 90px !important;
        margin-bottom: 6px !important;
        padding: 5px 10px !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] .iqr-gauge-card {
        transform: scale(.74) !important;
        transform-origin: center top !important;
        margin-top: -5px !important;
        margin-bottom: -24px !important;
    }

    section[data-testid="stSidebar"] .iqr-gauge-title {
        font-size: 12px !important;
    }

    section[data-testid="stSidebar"] .iqr-gauge-value {
        font-size: 19px !important;
    }

    section[data-testid="stSidebar"] .iqr-gauge-description {
        font-size: 8px !important;
        padding: 2px 5px !important;
        margin-top: 2px !important;
    }

    section[data-testid="stSidebar"] .iqr-gauge-hint {
        display: none !important;
    }

    section[data-testid="stSidebar"] div[class*="st-key-iqr_card_clickable"] .stButton {
        position: absolute !important;
        inset: 0 !important;
    }

    section[data-testid="stSidebar"] div[class*="st-key-iqr_card_clickable"] .stButton > button {
        min-height: 100% !important;
        height: 100% !important;
    }


    /* IQR V45 - proporzioni card sidebar */
    div[class*="st-key-iqr_card_clickable"] {
        min-height: 150px !important;
        height: auto !important;
        padding: 10px 14px 12px 14px !important;
        overflow: visible !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-card {
        transform: none !important;
        width:100% !important;
        margin:0 !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-title {
        color:#ffffff !important;
        font-size:15px !important;
        margin-bottom:8px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-scale-wrap {
        width:76% !important;
        padding-bottom:18px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-scale {
        height:20px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-pointer {
        border-left-width:9px !important;
        border-right-width:9px !important;
        border-bottom-width:12px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-value {
        font-size:18px !important;
        margin-top:-1px !important;
        margin-bottom:6px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-description {
        min-width:66% !important;
        color:#ffffff !important;
        font-size:15px !important;
        padding:7px 12px !important;
        border-radius:7px !important;
        margin:0 auto !important;
    }


    /* ======================================================
       V46 - IQR SIDEBAR PROPORZIONATO COME MOCKUP
       ====================================================== */

    div[class*="st-key-iqr_card_clickable"] {
        min-height: 190px !important;
        height: 190px !important;
        padding: 12px 16px 14px 16px !important;
        overflow: hidden !important;
        display: block !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-card {
        transform: none !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        box-sizing: border-box !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-title {
        color: #ffffff !important;
        font-size: 30px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
        margin: 0 0 13px 0 !important;
        padding: 0 !important;
        text-align: center !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-scale-wrap {
        width: 82% !important;
        margin: 0 auto !important;
        padding: 0 0 25px 0 !important;
        position: relative !important;
        box-sizing: border-box !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-scale {
        width: 100% !important;
        height: 34px !important;
        border-radius: 0 !important;
        overflow: hidden !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-pointer {
        bottom: 2px !important;
        border-left: 15px solid transparent !important;
        border-right: 15px solid transparent !important;
        border-bottom: 19px solid #ffc21c !important;
    }

    /* Nella card compatta il valore numerico non serve:
       il mockup richiesto mostra titolo, barra, triangolo e stato. */
    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-value {
        display: none !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-description {
        display: block !important;
        width: 62% !important;
        min-width: 0 !important;
        max-width: none !important;
        color: #ffffff !important;
        font-size: 20px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
        text-align: center !important;
        padding: 12px 10px !important;
        margin: 5px auto 0 auto !important;
        border: 2px solid #050505 !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
        white-space: nowrap !important;
    }


    /* ======================================================
       V47 - IQR: titolo visibile e card più grande
       ====================================================== */

    div[class*="st-key-iqr_card_clickable"] {
        min-height: 225px !important;
        height: 225px !important;
        padding: 16px 16px 16px 16px !important;
        overflow: visible !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-card {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        overflow: visible !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        min-height: 34px !important;
        overflow: visible !important;
        color: #ffffff !important;
        font-size: 18px !important;
        line-height: 1.15 !important;
        font-weight: 900 !important;
        letter-spacing: 0 !important;
        text-align: center !important;
        margin: 0 0 16px 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-scale-wrap {
        width: 84% !important;
        margin: 0 auto !important;
        padding-bottom: 30px !important;
        overflow: visible !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-scale {
        height: 38px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-pointer {
        bottom: 3px !important;
        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-description {
        width: 66% !important;
        min-width: 0 !important;
        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;
        padding: 12px 10px !important;
        margin: 8px auto 0 auto !important;
        white-space: nowrap !important;
    }

    /* MENU IN FONDO */
    section[data-testid="stSidebar"] details {
        margin-top: 3px !important;
        margin-bottom: 0 !important;
        background: transparent !important;
    }

    section[data-testid="stSidebar"] details > summary {
        min-height: 42px !important;
        height: 42px !important;
        padding: 0 13px !important;
        font-size: 15px !important;
        border-radius: 12px !important;
        border-width: 2px !important;
    }

    section[data-testid="stSidebar"] details[open] {
        padding: 0 7px 5px 7px !important;
        border-radius: 12px !important;
        background: rgba(8,43,80,.72) !important;
    }

    section[data-testid="stSidebar"] details[open] > summary {
        margin: 0 -7px 5px -7px !important;
    }

    /* 6 COMANDI = 3 RIGHE x 2 COLONNE */
    section[data-testid="stSidebar"] details div[data-testid="stHorizontalBlock"] {
        gap: 5px !important;
        margin-bottom: 2px !important;
    }

    section[data-testid="stSidebar"] details .stButton > button,
    section[data-testid="stSidebar"] details .stDownloadButton > button {
        min-height: 30px !important;
        height: 30px !important;
        padding: 2px 7px !important;
        font-size: 11px !important;
        line-height: 1 !important;
        justify-content: flex-start !important;
        border-radius: 6px !important;
        background: transparent !important;
        color: #ffffff !important;
        border: 0 !important;
    }

    section[data-testid="stSidebar"] details .stButton > button *,
    section[data-testid="stSidebar"] details .stDownloadButton > button * {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] details [data-testid="stToggle"] {
        min-height: 30px !important;
        height: 30px !important;
        display: flex !important;
        align-items: center !important;
    }

    section[data-testid="stSidebar"] details [data-testid="stToggle"] label,
    section[data-testid="stSidebar"] details [data-testid="stToggle"] span {
        color: #ffffff !important;
        font-size: 11px !important;
    }

    /* Footer compatto */
    section[data-testid="stSidebar"] div[style*="color:#5f8db5"] {
        padding: 4px 2px 0 2px !important;
        font-size: 9px !important;
    }

    /* ulteriore adattamento per notebook bassi */
    @media (max-height: 820px) and (min-width: 851px) {
        section[data-testid="stSidebar"] .fanta-header {
            min-height: 86px !important;
            height: 86px !important;
        }

        section[data-testid="stSidebar"] .fanta-logo {
            width: 52px !important;
            height: 52px !important;
            min-width: 52px !important;
        }

        section[data-testid="stSidebar"] .fanta-brand-title {
            font-size: 19px !important;
        }

        .sidebar-profile {
            min-height: 37px !important;
            height: 37px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stMetric"] {
            min-height: 54px !important;
            height: 54px !important;
            padding: 5px 10px !important;
        }

        div[class*="st-key-sidebar_budget_card"] {
            min-height: 59px !important;
            height: 59px !important;
        }

        section[data-testid="stSidebar"] div[class*="st-key-iqr_card_clickable"] {
            min-height: 76px !important;
            height: 76px !important;
        }
    }

    /* ======================================================
       V43 — SIDEBAR COME MOCKUP ALLEGATO
       ====================================================== */

    section[data-testid="stSidebar"] {
        width: 390px !important;
        min-width: 390px !important;
        background:
            linear-gradient(
                180deg,
                #061f3a 0%,
                #062744 48%,
                #041b31 100%
            ) !important;
        border-right: 1px solid #0d3c67 !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] > div {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding: 14px 16px 18px 16px !important;
        box-sizing: border-box !important;
        scrollbar-width: thin !important;
        scrollbar-color: #2b638e #061f3a !important;
    }

    section[data-testid="stSidebar"] > div::-webkit-scrollbar {
        width: 7px !important;
    }

    section[data-testid="stSidebar"] > div::-webkit-scrollbar-track {
        background: #061f3a !important;
    }

    section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
        background: #2b638e !important;
        border-radius: 8px !important;
    }

    /* HEADER */
    section[data-testid="stSidebar"] .fanta-header {
        width: 100% !important;
        min-height: 126px !important;
        margin: 0 0 12px 0 !important;
        padding: 14px 16px !important;
        background:
            linear-gradient(
                105deg,
                #06213d 0%,
                #082b4f 100%
            ) !important;
        border: 2px solid #ffc21c !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 22px rgba(0,0,0,.16) !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] .fanta-brand {
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] .fanta-logo {
        width: 76px !important;
        height: 76px !important;
        min-width: 76px !important;
        border: 3px solid #ffc21c !important;
        border-radius: 17px !important;
        background: #fff !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-title {
        color: #fff !important;
        font-size: 27px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        white-space: normal !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-title span {
        color: #ffc21c !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-subtitle {
        color: #fff !important;
        font-size: 14px !important;
        margin-top: 6px !important;
    }

    /* PROFILO */
    .sidebar-profile {
        width: 100% !important;
        min-height: 58px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 16px !important;
        margin: 0 0 12px 0 !important;
        border-radius: 14px !important;
        background:
            linear-gradient(
                90deg,
                #0a345f 0%,
                #0b3a69 100%
            ) !important;
        border: 1px solid rgba(62,132,190,.30) !important;
        box-sizing: border-box !important;
    }

    .sidebar-profile-icon {
        color: #ffc21c !important;
        font-size: 20px !important;
        margin-right: 11px !important;
    }

    .sidebar-profile-name {
        flex: 1 !important;
        color: #fff !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        text-align: left !important;
    }

    .sidebar-profile-arrow {
        color: #fff !important;
        font-size: 24px !important;
    }

    /* CARD CUSTOM */
    .fe-side-card {
        display: grid !important;
        grid-template-columns: 58px 1fr auto !important;
        align-items: center !important;
        gap: 12px !important;
        width: 100% !important;
        min-height: 96px !important;
        margin: 0 0 10px 0 !important;
        padding: 13px 16px !important;
        box-sizing: border-box !important;
        background:
            linear-gradient(
                100deg,
                #0b3158 0%,
                #0a2b4d 100%
            ) !important;
        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025) !important;
    }

    .fe-card-icon {
        color: #ffc21c !important;
        font-size: 35px !important;
        line-height: 1 !important;
        text-align: center !important;
    }

    .fe-card-label {
        color: #fff !important;
        font-size: 15px !important;
        font-weight: 850 !important;
        line-height: 1.15 !important;
        margin-bottom: 5px !important;
    }

    .fe-card-value {
        color: #ffc21c !important;
        font-size: 28px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
        white-space: nowrap !important;
    }

    .fe-card-help {
        color: #b9d1e8 !important;
        font-size: 18px !important;
        line-height: 1 !important;
        align-self: start !important;
        padding-top: 3px !important;
    }

    /* BUDGET */
    div[class*="st-key-sidebar_budget_card"] {
        min-height: 104px !important;
        margin: 0 0 10px 0 !important;
        padding: 11px 14px 12px 14px !important;
        background:
            linear-gradient(
                100deg,
                #0b3158 0%,
                #0a2b4d 100%
            ) !important;
        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        box-sizing: border-box !important;
    }

    .fe-budget-head {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        margin-bottom: 7px !important;
    }

    .fe-budget-icon {
        color: #ffc21c !important;
        font-size: 33px !important;
        width: 48px !important;
        text-align: center !important;
    }

    .fe-budget-title {
        color: #fff !important;
        font-size: 15px !important;
        font-weight: 850 !important;
        flex: 1 !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] label {
        display: none !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] input {
        height: 44px !important;
        min-height: 44px !important;
        background: #092947 !important;
        color: #ffc21c !important;
        border: 1px solid #1a5a8d !important;
        border-radius: 10px !important;
        font-size: 24px !important;
        font-weight: 950 !important;
        box-shadow: none !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] button {
        width: 40px !important;
        height: 44px !important;
        min-height: 44px !important;
        background: #124776 !important;
        color: #fff !important;
        border: 0 !important;
        border-radius: 6px !important;
        padding: 0 !important;
        margin-left: 2px !important;
        box-shadow: none !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] button:hover {
        background: #185989 !important;
    }

    div[class*="st-key-sidebar_budget_card"] div[data-testid="stNumberInput"] button * {
        color: #fff !important;
    }

    /* IQR */
    div[class*="st-key-iqr_card_clickable"] {
        min-height: 132px !important;
        margin: 0 0 10px 0 !important;
        padding: 9px 14px !important;
        background:
            linear-gradient(
                100deg,
                #0b3158 0%,
                #0a2b4d 100%
            ) !important;
        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-card {
        transform: scale(.68) !important;
        transform-origin: center top !important;
        margin-top: -8px !important;
        margin-bottom: -32px !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-title {
        color: #fff !important;
        font-size: 14px !important;
        font-weight: 900 !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-value {
        color: #ffc21c !important;
        font-size: 23px !important;
        font-weight: 950 !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-description {
        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 900 !important;
        padding: 5px 10px !important;
        border-radius: 7px !important;
        min-width: 120px !important;
        text-align: center !important;
        margin: 4px auto 0 auto !important;
        display: table !important;
    }

    div[class*="st-key-iqr_card_clickable"] .iqr-gauge-hint {
        display: none !important;
    }

    /* MENU IN FONDO */
    section[data-testid="stSidebar"] details {
        width: 100% !important;
        margin: 2px 0 0 0 !important;
        background: transparent !important;
        border: 0 !important;
    }

    section[data-testid="stSidebar"] details > summary {
        min-height: 52px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 16px !important;
        background: #082744 !important;
        color: #ffc21c !important;
        border: 2px solid #ffc21c !important;
        border-radius: 14px !important;
        font-size: 17px !important;
        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"] details > summary * {
        color: #ffc21c !important;
    }

    section[data-testid="stSidebar"] details[open] {
        background: rgba(8,43,80,.72) !important;
        border: 1px solid #164b78 !important;
        border-radius: 14px !important;
        padding: 0 8px 9px 8px !important;
    }

    section[data-testid="stSidebar"] details[open] > summary {
        margin: 0 -8px 8px -8px !important;
    }

    section[data-testid="stSidebar"] details div[data-testid="stHorizontalBlock"] {
        gap: 8px !important;
        margin-bottom: 4px !important;
    }

    section[data-testid="stSidebar"] details .stButton > button,
    section[data-testid="stSidebar"] details .stDownloadButton > button {
        min-height: 36px !important;
        height: 36px !important;
        padding: 4px 9px !important;
        background: transparent !important;
        color: #fff !important;
        border: 0 !important;
        border-radius: 7px !important;
        font-size: 13px !important;
        font-weight: 650 !important;
        justify-content: flex-start !important;
    }

    section[data-testid="stSidebar"] details .stButton > button *,
    section[data-testid="stSidebar"] details .stDownloadButton > button * {
        color: #fff !important;
    }

    section[data-testid="stSidebar"] details [data-testid="stToggle"] label,
    section[data-testid="stSidebar"] details [data-testid="stToggle"] span {
        color: #fff !important;
        font-size: 13px !important;
    }

    @media (max-width: 950px) {
        section[data-testid="stSidebar"] {
            width: 345px !important;
            min-width: 345px !important;
        }

        .fe-side-card {
            grid-template-columns: 48px 1fr auto !important;
            min-height: 88px !important;
        }

        .fe-card-icon {
            font-size: 30px !important;
        }

        .fe-card-value {
            font-size: 24px !important;
        }
    }
    
    /* ======================================================
       V48 - OVERRIDE FINALE IQR
       Deve restare DOPO tutti gli stili precedenti.
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"] {
        min-height: 225px !important;
        height: 225px !important;
        max-height: none !important;
        margin: 0 0 10px 0 !important;
        padding: 15px 16px 16px 16px !important;
        overflow: visible !important;

        background:
            linear-gradient(
                100deg,
                #0b3158 0%,
                #0a2b4d 100%
            ) !important;

        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-gauge-card {
        transform: none !important;
        transform-origin: initial !important;

        width: 100% !important;
        height: auto !important;

        margin: 0 !important;
        padding: 0 !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;

        overflow: visible !important;
    }

    /* Titolo: stessa dimensione delle etichette delle altre card */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;

        width: 100% !important;
        height: auto !important;
        min-height: 24px !important;

        margin: 0 0 15px 0 !important;
        padding: 0 !important;

        color: #ffffff !important;

        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;

        text-align: center !important;
        white-space: nowrap !important;

        overflow: visible !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-scale-wrap {
        position: relative !important;

        width: 84% !important;

        margin: 0 auto !important;
        padding: 0 0 30px 0 !important;

        overflow: visible !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-scale {
        width: 100% !important;
        height: 38px !important;

        display: grid !important;
        grid-template-columns: 40fr 25fr 15fr 20fr !important;

        overflow: hidden !important;
        border-radius: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-pointer {
        position: absolute !important;

        bottom: 3px !important;

        width: 0 !important;
        height: 0 !important;

        transform: translateX(-50%) !important;

        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    /* Percentuale nascosta solo nella card laterale */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-gauge-value {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-gauge-description {
        display: block !important;

        width: 66% !important;
        min-width: 0 !important;
        max-width: none !important;

        margin: 8px auto 0 auto !important;
        padding: 12px 10px !important;

        color: #ffffff !important;

        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;

        text-align: center !important;
        white-space: nowrap !important;

        border: 2px solid #050505 !important;
        border-radius: 8px !important;

        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    .iqr-gauge-hint {
        display: none !important;
    }


    /* ======================================================
       V49 - IQR CLICK AREA INVISIBILE + TOOLTIP
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"] {
        position: relative !important;
        cursor: pointer !important;
    }

    /* Il contenitore del bottone non deve occupare spazio nel layout */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] {
        position: absolute !important;
        inset: 0 !important;
        z-index: 20 !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: auto !important;
    }

    /* Bottone completamente invisibile ma cliccabile */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] > button {
        position: absolute !important;
        inset: 0 !important;
        z-index: 20 !important;

        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;

        height: 100% !important;
        min-height: 100% !important;
        max-height: 100% !important;

        margin: 0 !important;
        padding: 0 !important;

        background: transparent !important;
        background-color: transparent !important;

        border: 0 !important;
        border-radius: 15px !important;

        box-shadow: none !important;
        outline: none !important;

        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;

        opacity: 0 !important;
        overflow: hidden !important;

        cursor: pointer !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] > button * {
        display: none !important;
        visibility: hidden !important;
    }

    /* Nessun effetto grafico bianco in hover/focus/active */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] > button:hover,
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] > button:focus,
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] > button:focus-visible,
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]
    div[data-testid="stButton"] > button:active {
        background: transparent !important;
        background-color: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        opacity: 0 !important;
    }

    /* Tooltip custom: compare SOLO passando sopra la card */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]::after {
        content: "Clicca per aprire dettaglio IQR";

        position: absolute !important;
        left: 50% !important;
        bottom: 9px !important;
        transform: translate(-50%, 5px) !important;

        z-index: 30 !important;

        padding: 6px 10px !important;

        background: rgba(5, 18, 34, .94) !important;
        color: #ffffff !important;

        border: 1px solid rgba(255, 194, 28, .55) !important;
        border-radius: 7px !important;

        font-size: 12px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;

        white-space: nowrap !important;

        opacity: 0 !important;
        visibility: hidden !important;

        pointer-events: none !important;

        transition:
            opacity .14s ease,
            transform .14s ease,
            visibility .14s ease !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_card_clickable"]:hover::after {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translate(-50%, 0) !important;
    }


    /* ======================================================
       V50 - IQR CARD SENZA ST.BUTTON
       Il click è un link HTML sull'intera card.
       ====================================================== */

    section[data-testid="stSidebar"] .iqr-card-link {
        display: block !important;
        width: 100% !important;
        margin: 0 0 10px 0 !important;

        text-decoration: none !important;
        color: inherit !important;

        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link:visited,
    section[data-testid="stSidebar"] .iqr-card-link:hover,
    section[data-testid="stSidebar"] .iqr-card-link:active,
    section[data-testid="stSidebar"] .iqr-card-link:focus {
        text-decoration: none !important;
        color: inherit !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner {
        min-height: 225px !important;
        height: 225px !important;

        padding: 15px 16px 16px 16px !important;

        background:
            linear-gradient(
                100deg,
                #0b3158 0%,
                #0a2b4d 100%
            ) !important;

        border: 1px solid #165387 !important;
        border-radius: 15px !important;

        box-sizing: border-box !important;
        overflow: visible !important;

        transition:
            border-color .14s ease,
            box-shadow .14s ease !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link:hover
    .iqr-card-link-inner {
        border-color: rgba(255,194,28,.72) !important;
        box-shadow:
            0 0 0 1px rgba(255,194,28,.13),
            inset 0 1px 0 rgba(255,255,255,.03) !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-gauge-card {
        transform: none !important;
        width: 100% !important;
        height: 100% !important;

        margin: 0 !important;
        padding: 0 !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;

        overflow: visible !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;

        width: 100% !important;
        min-height: 24px !important;

        margin: 0 0 15px 0 !important;
        padding: 0 !important;

        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;

        text-align: center !important;
        white-space: nowrap !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-scale-wrap {
        position: relative !important;

        width: 84% !important;

        margin: 0 auto !important;
        padding: 0 0 30px 0 !important;

        overflow: visible !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-scale {
        width: 100% !important;
        height: 38px !important;

        display: grid !important;
        grid-template-columns: 40fr 25fr 15fr 20fr !important;

        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-pointer {
        bottom: 3px !important;

        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-gauge-value {
        display: none !important;
    }

    section[data-testid="stSidebar"] .iqr-card-link-inner
    .iqr-gauge-description {
        display: block !important;

        width: 66% !important;
        min-width: 0 !important;
        max-width: none !important;

        margin: 8px auto 0 auto !important;
        padding: 12px 10px !important;

        color: #ffffff !important;

        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;

        text-align: center !important;
        white-space: nowrap !important;

        border: 2px solid #050505 !important;
        border-radius: 8px !important;

        box-sizing: border-box !important;
    }

    /* Tooltip nativo del browser via title.
       Nessun widget bianco/verticale dentro la card. */


    /* ======================================================
       V51 - CARD IQR PULITA, SENZA WIDGET STREAMLIT
       ====================================================== */

    section[data-testid="stSidebar"] .iqr-v51-link {
        display:block !important;
        width:100% !important;
        margin:0 0 10px 0 !important;
        padding:0 !important;
        text-decoration:none !important;
        color:inherit !important;
        cursor:pointer !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card {
        width:100% !important;
        min-height:225px !important;
        height:225px !important;
        box-sizing:border-box !important;
        padding:15px 16px 16px 16px !important;
        margin:0 !important;

        background:linear-gradient(
            100deg,
            #0b3158 0%,
            #0a2b4d 100%
        ) !important;

        border:1px solid #165387 !important;
        border-radius:15px !important;
        overflow:hidden !important;

        position:relative !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-gauge-card {
        width:100% !important;
        height:100% !important;
        margin:0 !important;
        padding:0 !important;
        transform:none !important;

        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:flex-start !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-gauge-title {
        display:block !important;
        visibility:visible !important;
        opacity:1 !important;

        margin:0 0 15px 0 !important;
        padding:0 !important;

        color:#ffffff !important;
        font-size:15px !important;
        line-height:1.15 !important;
        font-weight:850 !important;
        text-align:center !important;
        white-space:nowrap !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-scale-wrap {
        position:relative !important;
        width:84% !important;
        margin:0 auto !important;
        padding:0 0 30px 0 !important;
        box-sizing:border-box !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-scale {
        display:grid !important;
        grid-template-columns:40fr 25fr 15fr 20fr !important;
        width:100% !important;
        height:38px !important;
        overflow:hidden !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-pointer {
        position:absolute !important;
        bottom:3px !important;
        width:0 !important;
        height:0 !important;
        transform:translateX(-50%) !important;

        border-left:16px solid transparent !important;
        border-right:16px solid transparent !important;
        border-bottom:21px solid #ffc21c !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-gauge-value {
        display:none !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card .iqr-gauge-description {
        display:block !important;
        width:66% !important;
        min-width:0 !important;
        margin:8px auto 0 auto !important;
        padding:12px 10px !important;

        color:#ffffff !important;
        font-size:18px !important;
        line-height:1.05 !important;
        font-weight:950 !important;
        text-align:center !important;
        white-space:nowrap !important;

        border:2px solid #050505 !important;
        border-radius:8px !important;
        box-sizing:border-box !important;
    }

    /* Tooltip custom: non usa title/bottone Streamlit */
    section[data-testid="stSidebar"] .iqr-v51-card::after {
        content:"Clicca per aprire dettaglio IQR";
        position:absolute !important;
        left:50% !important;
        bottom:8px !important;
        transform:translate(-50%,4px) !important;
        z-index:10 !important;

        padding:6px 10px !important;
        background:rgba(5,18,34,.94) !important;
        color:#ffffff !important;
        border:1px solid rgba(255,194,28,.55) !important;
        border-radius:7px !important;

        font-size:12px !important;
        font-weight:700 !important;
        line-height:1.15 !important;
        white-space:nowrap !important;

        opacity:0 !important;
        visibility:hidden !important;
        pointer-events:none !important;
        transition:opacity .14s ease, transform .14s ease !important;
    }

    section[data-testid="stSidebar"] .iqr-v51-card:hover::after {
        opacity:1 !important;
        visibility:visible !important;
        transform:translate(-50%,0) !important;
    }


    /* ======================================================
       V53 - IQR: CLICK NELLA STESSA PAGINA
       Nessun link, nessun query param, nessuna nuova scheda.
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"] {
        position: relative !important;
        width: 100% !important;
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card {
        width: 100% !important;
        min-height: 225px !important;
        height: 225px !important;
        box-sizing: border-box !important;
        padding: 15px 16px 16px 16px !important;

        background: linear-gradient(
            100deg,
            #0b3158 0%,
            #0a2b4d 100%
        ) !important;

        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-gauge-card {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;

        margin: 0 0 15px 0 !important;
        padding: 0 !important;

        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;
        text-align: center !important;
        white-space: nowrap !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-scale-wrap {
        position: relative !important;
        width: 84% !important;
        margin: 0 auto !important;
        padding: 0 0 30px 0 !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-scale {
        display: grid !important;
        grid-template-columns: 40fr 25fr 15fr 20fr !important;
        width: 100% !important;
        height: 38px !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-pointer {
        bottom: 3px !important;
        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-gauge-value {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    .iqr-v53-card .iqr-gauge-description {
        display: block !important;
        width: 66% !important;
        min-width: 0 !important;
        margin: 8px auto 0 auto !important;
        padding: 12px 10px !important;

        color: #ffffff !important;
        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;
        text-align: center !important;
        white-space: nowrap !important;

        border: 2px solid #050505 !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
    }

    /* Il vero bottone Streamlit è un overlay trasparente.
       Non occupa spazio e non può apparire come cartellino bianco. */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    div[data-testid="stButton"] {
        position: absolute !important;
        inset: 0 !important;
        z-index: 30 !important;
        width: 100% !important;
        height: 225px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    div[data-testid="stButton"] > button {
        position: absolute !important;
        inset: 0 !important;

        width: 100% !important;
        height: 225px !important;
        min-height: 225px !important;

        margin: 0 !important;
        padding: 0 !important;

        border: 0 !important;
        border-radius: 15px !important;

        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;

        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;

        opacity: 0.001 !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]
    div[data-testid="stButton"] > button * {
        visibility: hidden !important;
        display: none !important;
    }

    /* Tooltip custom in hover */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]::after {
        content: "Clicca per aprire dettaglio IQR";

        position: absolute !important;
        left: 50% !important;
        bottom: 9px !important;
        transform: translate(-50%, 4px) !important;

        z-index: 40 !important;

        padding: 6px 10px !important;

        background: rgba(5,18,34,.94) !important;
        color: #ffffff !important;

        border: 1px solid rgba(255,194,28,.55) !important;
        border-radius: 7px !important;

        font-size: 12px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;

        white-space: nowrap !important;

        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;

        transition: opacity .14s ease, transform .14s ease !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v53_clickable"]:hover::after {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translate(-50%, 0) !important;
    }


    /* ======================================================
       V54 - FIX CLICK IQR
       Il bottone invisibile è sopra la card e riceve il click.
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"] {
        position: relative !important;
        width: 100% !important;
        height: 225px !important;
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    /* CARD GRAFICA: non intercetta mai il mouse */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card {
        position: absolute !important;
        inset: 0 !important;
        z-index: 1 !important;

        width: 100% !important;
        height: 225px !important;
        box-sizing: border-box !important;
        padding: 15px 16px 16px 16px !important;

        background: linear-gradient(
            100deg,
            #0b3158 0%,
            #0a2b4d 100%
        ) !important;

        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        overflow: hidden !important;

        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card * {
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-gauge-card {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin: 0 0 15px 0 !important;
        padding: 0 !important;
        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;
        text-align: center !important;
        white-space: nowrap !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-scale-wrap {
        position: relative !important;
        width: 84% !important;
        margin: 0 auto !important;
        padding: 0 0 30px 0 !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-scale {
        display: grid !important;
        grid-template-columns: 40fr 25fr 15fr 20fr !important;
        width: 100% !important;
        height: 38px !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-pointer {
        bottom: 3px !important;
        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-gauge-value {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    .iqr-v54-card .iqr-gauge-description {
        display: block !important;
        width: 66% !important;
        min-width: 0 !important;
        margin: 8px auto 0 auto !important;
        padding: 12px 10px !important;
        color: #ffffff !important;
        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;
        text-align: center !important;
        white-space: nowrap !important;
        border: 2px solid #050505 !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
    }

    /* OVERLAY CLICCABILE REALE */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    div[data-testid="stButton"] {
        position: absolute !important;
        inset: 0 !important;
        z-index: 50 !important;

        width: 100% !important;
        height: 225px !important;

        margin: 0 !important;
        padding: 0 !important;

        pointer-events: auto !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    div[data-testid="stButton"] > button {
        position: absolute !important;
        inset: 0 !important;

        width: 100% !important;
        height: 225px !important;
        min-height: 225px !important;

        margin: 0 !important;
        padding: 0 !important;

        background: transparent !important;
        border: 0 !important;
        border-radius: 15px !important;
        box-shadow: none !important;
        outline: none !important;

        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;

        opacity: 0.01 !important;
        cursor: pointer !important;
        pointer-events: auto !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]
    div[data-testid="stButton"] > button * {
        opacity: 0 !important;
        color: transparent !important;
        font-size: 0 !important;
    }

    /* Tooltip custom */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]::after {
        content: "Clicca per aprire dettaglio IQR";

        position: absolute !important;
        left: 50% !important;
        bottom: 9px !important;
        transform: translate(-50%, 4px) !important;

        z-index: 60 !important;
        padding: 6px 10px !important;

        background: rgba(5,18,34,.94) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,194,28,.55) !important;
        border-radius: 7px !important;

        font-size: 12px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
        white-space: nowrap !important;

        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;

        transition: opacity .14s ease, transform .14s ease !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v54_clickable"]:hover::after {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translate(-50%, 0) !important;
    }


    /* ======================================================
       V55 - FIX MENU SOTTO IQR
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"] {
        position: relative !important;
        width: 100% !important;

        /* niente height fissa qui */
        height: auto !important;
        min-height: 0 !important;

        margin: 0 0 10px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-spacer {
        display: block !important;
        width: 100% !important;
        height: 225px !important;
        min-height: 225px !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card {
        position: absolute !important;
        inset: 0 auto auto 0 !important;
        z-index: 1 !important;

        width: 100% !important;
        height: 225px !important;

        box-sizing: border-box !important;
        padding: 15px 16px 16px 16px !important;

        background: linear-gradient(
            100deg,
            #0b3158 0%,
            #0a2b4d 100%
        ) !important;

        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        overflow: hidden !important;

        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card * {
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-card {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;

        margin: 0 0 15px 0 !important;
        padding: 0 !important;

        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;
        text-align: center !important;
        white-space: nowrap !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-scale-wrap {
        position: relative !important;
        width: 84% !important;
        margin: 0 auto !important;
        padding: 0 0 30px 0 !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-scale {
        display: grid !important;
        grid-template-columns: 40fr 25fr 15fr 20fr !important;
        width: 100% !important;
        height: 38px !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-pointer {
        bottom: 3px !important;
        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-value {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-description {
        display: block !important;
        width: 66% !important;
        min-width: 0 !important;
        margin: 8px auto 0 auto !important;
        padding: 12px 10px !important;

        color: #ffffff !important;
        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;
        text-align: center !important;
        white-space: nowrap !important;

        border: 2px solid #050505 !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
    }

    /* overlay cliccabile, limitato ESATTAMENTE alla card */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    div[data-testid="stButton"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;

        width: 100% !important;
        height: 225px !important;

        z-index: 50 !important;
        margin: 0 !important;
        padding: 0 !important;

        pointer-events: auto !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 225px !important;
        min-height: 225px !important;

        margin: 0 !important;
        padding: 0 !important;

        background: transparent !important;
        border: 0 !important;
        border-radius: 15px !important;
        box-shadow: none !important;
        outline: none !important;

        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;

        opacity: .01 !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    div[data-testid="stButton"] > button * {
        display: none !important;
        visibility: hidden !important;
    }

    /* tooltip */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]::after {
        content: "Clicca per aprire dettaglio IQR";

        position: absolute !important;
        left: 50% !important;
        top: 186px !important;
        transform: translate(-50%, 4px) !important;

        z-index: 60 !important;

        padding: 6px 10px !important;

        background: rgba(5,18,34,.94) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,194,28,.55) !important;
        border-radius: 7px !important;

        font-size: 12px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
        white-space: nowrap !important;

        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]:hover::after {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translate(-50%, 0) !important;
    }


    /* ======================================================
       V56 - SIDEBAR UNIFORME COME MOCKUP
       ====================================================== */

    :root {
        --fe-side-bg: #071f38;
        --fe-side-card: #0b3158;
        --fe-side-card-2: #0a2b4d;
        --fe-side-border: #155486;
        --fe-side-gold: #ffc21c;
        --fe-side-white: #ffffff;
        --fe-side-soft: #bfd2e5;
        --fe-side-blue-btn: #124776;
    }

    /* ------------------------------------------------------
       PROFILO
       ------------------------------------------------------ */
    section[data-testid="stSidebar"] .sidebar-profile {
        min-height: 48px !important;
        height: 48px !important;
        margin: 0 0 9px 0 !important;
        padding: 0 14px !important;
        border-radius: 12px !important;
        background: linear-gradient(
            90deg,
            #0a345f 0%,
            #0b3a69 100%
        ) !important;
        border: 1px solid rgba(62,132,190,.32) !important;
    }

    section[data-testid="stSidebar"] .sidebar-profile-icon {
        color: var(--fe-side-gold) !important;
        font-size: 18px !important;
        margin-right: 9px !important;
    }

    section[data-testid="stSidebar"] .sidebar-profile-name {
        color: var(--fe-side-white) !important;
        font-size: 14px !important;
        font-weight: 900 !important;
    }

    /* ------------------------------------------------------
       CARD STANDARD
       ------------------------------------------------------ */
    section[data-testid="stSidebar"] .fe-side-card {
        width: 100% !important;
        min-height: 82px !important;
        height: 82px !important;
        margin: 0 0 8px 0 !important;
        padding: 11px 14px !important;

        display: grid !important;
        grid-template-columns: 46px 1fr 20px !important;
        align-items: center !important;
        column-gap: 10px !important;

        background: linear-gradient(
            100deg,
            var(--fe-side-card) 0%,
            var(--fe-side-card-2) 100%
        ) !important;

        border: 1px solid var(--fe-side-border) !important;
        border-radius: 12px !important;
        box-sizing: border-box !important;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.025) !important;
    }

    section[data-testid="stSidebar"] .fe-card-icon {
        width: 46px !important;
        min-width: 46px !important;
        color: var(--fe-side-gold) !important;
        font-size: 29px !important;
        line-height: 1 !important;
        text-align: center !important;
    }

    section[data-testid="stSidebar"] .fe-card-label {
        margin: 0 0 5px 0 !important;
        color: var(--fe-side-white) !important;
        font-size: 13px !important;
        line-height: 1.05 !important;
        font-weight: 850 !important;
    }

    section[data-testid="stSidebar"] .fe-card-value {
        color: var(--fe-side-gold) !important;
        font-size: 22px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
        white-space: nowrap !important;
    }

    section[data-testid="stSidebar"] .fe-card-help {
        width: 20px !important;
        height: 20px !important;
        color: var(--fe-side-soft) !important;
        font-size: 13px !important;
        font-weight: 900 !important;
        line-height: 18px !important;
        text-align: center !important;
        border: 1px solid var(--fe-side-soft) !important;
        border-radius: 50% !important;
        box-sizing: border-box !important;
    }

    /* ------------------------------------------------------
       BUDGET - stessa card delle altre
       ------------------------------------------------------ */
    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"] {
        position: relative !important;

        width: 100% !important;
        min-height: 94px !important;
        height: 94px !important;

        margin: 0 0 8px 0 !important;
        padding: 10px 12px 10px 12px !important;

        background: linear-gradient(
            100deg,
            var(--fe-side-card) 0%,
            var(--fe-side-card-2) 100%
        ) !important;

        border: 1px solid var(--fe-side-border) !important;
        border-radius: 12px !important;
        box-sizing: border-box !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025) !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-head {
        display: grid !important;
        grid-template-columns: 38px 1fr 18px !important;
        align-items: center !important;
        gap: 8px !important;
        margin: 0 0 5px 0 !important;
        min-height: 27px !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-icon {
        width: 38px !important;
        color: var(--fe-side-gold) !important;
        font-size: 26px !important;
        line-height: 1 !important;
        text-align: center !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-title {
        color: var(--fe-side-white) !important;
        font-size: 13px !important;
        line-height: 1 !important;
        font-weight: 850 !important;
    }

    /* piccolo simbolo modifica, coerente col mockup */
    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-head::after {
        content: "✎";
        color: var(--fe-side-soft) !important;
        font-size: 18px !important;
        line-height: 1 !important;
        text-align: right !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] {
        margin: 0 0 0 46px !important;
        width: calc(100% - 46px) !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] label {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] > div {
        gap: 3px !important;
        background: transparent !important;
        border: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] input {
        height: 38px !important;
        min-height: 38px !important;

        padding: 0 10px !important;

        color: var(--fe-side-gold) !important;
        background: #092947 !important;

        border: 1px solid #1a5a8d !important;
        border-radius: 7px !important;

        font-size: 20px !important;
        line-height: 1 !important;
        font-weight: 950 !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button {
        width: 34px !important;
        min-width: 34px !important;
        height: 38px !important;
        min-height: 38px !important;

        margin: 0 !important;
        padding: 0 !important;

        color: #ffffff !important;
        background: var(--fe-side-blue-btn) !important;

        border: 0 !important;
        border-radius: 6px !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button:hover {
        background: #185989 !important;
    }

    /* ------------------------------------------------------
       IQR
       Mantiene le ultime modifiche V55.
       Cambiamo solo bordo/background per uniformarlo alle card.
       ------------------------------------------------------ */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card {
        background: linear-gradient(
            100deg,
            var(--fe-side-card) 0%,
            var(--fe-side-card-2) 100%
        ) !important;

        border: 1px solid var(--fe-side-border) !important;
        border-radius: 12px !important;
    }

    /* ------------------------------------------------------
       MENU
       ------------------------------------------------------ */
    section[data-testid="stSidebar"] details > summary {
        background: #082744 !important;
        color: var(--fe-side-gold) !important;
        border: 2px solid var(--fe-side-gold) !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"] details > summary * {
        color: var(--fe-side-gold) !important;
    }


    /* V57: riduzione spazio superiore + icone oro */
    section[data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2px !important;
        margin-top: 0 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        height: 2px !important;
        min-height: 2px !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] > * {
        display: none !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-card,
    section[data-testid="stSidebar"] .fanta-brand-wrap {
        margin-top: 0 !important;
    }

    section[data-testid="stSidebar"] .fe-card-icon,
    section[data-testid="stSidebar"] .fe-budget-icon,
    section[data-testid="stSidebar"] .sidebar-profile-icon {
        color: #ffc21c !important;
        filter: grayscale(1) sepia(1) saturate(8)
                hue-rotate(355deg) brightness(1.18) contrast(1.05) !important;
    }

    section[data-testid="stSidebar"] .fe-card-icon svg,
    section[data-testid="stSidebar"] .fe-budget-icon svg,
    section[data-testid="stSidebar"] .sidebar-profile-icon svg {
        fill: #ffc21c !important;
        stroke: #ffc21c !important;
        color: #ffc21c !important;
        filter: none !important;
    }

    /* ======================================================
       V58 - ICONE REALMENTE MONOCROMATICHE ORO
       ====================================================== */
    section[data-testid="stSidebar"] .fe-card-icon,
    section[data-testid="stSidebar"] .fe-budget-icon,
    section[data-testid="stSidebar"] .sidebar-profile-icon {
        color: #ffc21c !important;
        -webkit-text-fill-color: #ffc21c !important;
        filter: none !important;
        text-shadow: none !important;
        font-family: Arial, "Noto Sans Symbols 2", sans-serif !important;
        font-weight: 900 !important;
    }

    section[data-testid="stSidebar"] .fe-card-icon *,
    section[data-testid="stSidebar"] .fe-budget-icon *,
    section[data-testid="stSidebar"] .sidebar-profile-icon * {
        color: #ffc21c !important;
        fill: #ffc21c !important;
        stroke: #ffc21c !important;
        filter: none !important;
    }

    /* V59 - icona Portieri: guanto allegato dall'utente */
    section[data-testid="stSidebar"] .fe-portieri-icon {
        display:flex !important;
        align-items:center !important;
        justify-content:center !important;
        filter:none !important;
    }

    section[data-testid="stSidebar"] .fe-portieri-icon img {
        display:block !important;
        width:34px !important;
        height:34px !important;
        object-fit:contain !important;
        filter:none !important;
    }

    /* V60 - icona Giocatori: scarpa + pallone allegata dall'utente */
    section[data-testid="stSidebar"] .fe-giocatori-icon {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .fe-giocatori-icon img {
        display: block !important;
        width: 39px !important;
        height: 39px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    /* V61 - icona Budget: monete allegata dall'utente */
    section[data-testid="stSidebar"] .fe-budget-coins-icon {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .fe-budget-coins-icon img {
        display: block !important;
        width: 36px !important;
        height: 36px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    /* V62 - icona Budget rimanente: portafoglio allegato dall'utente */
    section[data-testid="stSidebar"] .fe-budget-rimanente-icon {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .fe-budget-rimanente-icon img {
        display: block !important;
        width: 37px !important;
        height: 37px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    /* V63 - icona Oltre soglia: triangolo di attenzione */
    section[data-testid="stSidebar"] .fe-oltre-soglia-icon {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .fe-oltre-soglia-icon img {
        display: block !important;
        width: 36px !important;
        height: 36px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    /* V64 - Oltre soglia: nuova icona grafico a barre */
    section[data-testid="stSidebar"] .fe-oltre-soglia-icon img {
        width: 37px !important;
        height: 37px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    /* ======================================================
       V65 - SIDEBAR FEDELE AL MOCKUP APPROVATO
       ====================================================== */

    :root {
        --fe-navy: #061f3a;
        --fe-card: #0b3158;
        --fe-card2: #0a2b4d;
        --fe-border: #155486;
        --fe-gold: #ffc21c;
        --fe-white: #ffffff;
        --fe-help: #c7d7e8;
        --fe-btn: #124776;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        width: 390px !important;
        min-width: 390px !important;
        background:
            linear-gradient(
                180deg,
                #061f3a 0%,
                #062744 50%,
                #041b31 100%
            ) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding: 10px 15px 16px 15px !important;
    }

    /* Header/logo */
    section[data-testid="stSidebar"] .fanta-header {
        margin: 0 0 10px 0 !important;
        min-height: 118px !important;
        padding: 13px 15px !important;
        border: 2px solid var(--fe-gold) !important;
        border-radius: 18px !important;
        background: linear-gradient(
            105deg,
            #06213d 0%,
            #082b4f 100%
        ) !important;
        box-shadow: 0 7px 20px rgba(0,0,0,.14) !important;
    }

    section[data-testid="stSidebar"] .fanta-logo {
        width: 72px !important;
        height: 72px !important;
        min-width: 72px !important;
        border: 2px solid var(--fe-gold) !important;
        border-radius: 16px !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-title {
        font-size: 25px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"] .fanta-brand-subtitle {
        font-size: 13px !important;
        margin-top: 5px !important;
    }

    /* Profilo */
    section[data-testid="stSidebar"] .sidebar-profile {
        min-height: 50px !important;
        height: 50px !important;
        margin: 0 0 10px 0 !important;
        border-radius: 12px !important;
        padding: 0 14px !important;
        background: linear-gradient(
            90deg,
            #0a345f 0%,
            #0b3a69 100%
        ) !important;
    }

    section[data-testid="stSidebar"] .sidebar-profile-icon {
        color: var(--fe-gold) !important;
        font-size: 18px !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .sidebar-profile-name {
        color: var(--fe-white) !important;
        font-size: 14px !important;
        font-weight: 900 !important;
    }

    /* Tutte le card standard */
    section[data-testid="stSidebar"] .fe-side-card {
        min-height: 90px !important;
        height: 90px !important;
        margin: 0 0 9px 0 !important;
        padding: 12px 15px !important;

        display: grid !important;
        grid-template-columns: 54px 1fr 24px !important;
        align-items: center !important;
        column-gap: 12px !important;

        background: linear-gradient(
            100deg,
            var(--fe-card) 0%,
            var(--fe-card2) 100%
        ) !important;

        border: 1px solid var(--fe-border) !important;
        border-radius: 13px !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] .fe-card-icon {
        width: 54px !important;
        min-width: 54px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: var(--fe-gold) !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .fe-card-icon img {
        width: 42px !important;
        height: 42px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"] .fe-card-label {
        color: var(--fe-white) !important;
        font-size: 15px !important;
        line-height: 1.05 !important;
        font-weight: 850 !important;
        margin: 0 0 6px 0 !important;
    }

    section[data-testid="stSidebar"] .fe-card-value {
        color: var(--fe-gold) !important;
        font-size: 24px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"] .fe-card-help {
        width: 22px !important;
        height: 22px !important;
        line-height: 20px !important;
        font-size: 13px !important;
        color: var(--fe-help) !important;
        border: 1px solid var(--fe-help) !important;
        border-radius: 50% !important;
        text-align: center !important;
    }

    /* Budget */
    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"] {
        min-height: 106px !important;
        height: 106px !important;
        margin: 0 0 9px 0 !important;
        padding: 11px 14px !important;

        background: linear-gradient(
            100deg,
            var(--fe-card) 0%,
            var(--fe-card2) 100%
        ) !important;

        border: 1px solid var(--fe-border) !important;
        border-radius: 13px !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-head {
        display: grid !important;
        grid-template-columns: 46px 1fr 24px !important;
        align-items: center !important;
        gap: 10px !important;
        margin: 0 0 7px 0 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-icon {
        width: 46px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-icon img {
        width: 40px !important;
        height: 40px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-title {
        color: var(--fe-white) !important;
        font-size: 15px !important;
        font-weight: 850 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-head::after {
        content: "✎";
        color: var(--fe-help) !important;
        font-size: 21px !important;
        text-align: right !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] {
        margin-left: 55px !important;
        width: calc(100% - 55px) !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] input {
        height: 43px !important;
        min-height: 43px !important;
        padding: 0 12px !important;

        color: var(--fe-gold) !important;
        background: #092947 !important;

        border: 1px solid #1a5a8d !important;
        border-radius: 7px !important;

        font-size: 22px !important;
        font-weight: 950 !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button {
        width: 39px !important;
        min-width: 39px !important;
        height: 43px !important;
        min-height: 43px !important;

        color: #ffffff !important;
        background: var(--fe-btn) !important;

        border: 0 !important;
        border-radius: 7px !important;
        box-shadow: none !important;
    }

    /* IQR Sidebar */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v65_clickable"] {
        position: relative !important;
        width: 100% !important;
        height: auto !important;
        margin: 0 0 9px 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-card {
        position: absolute !important;
        inset: 0 auto auto 0 !important;

        width: 100% !important;
        height: 150px !important;

        display: grid !important;
        grid-template-columns: 104px 1fr !important;
        align-items: center !important;

        padding: 13px 16px !important;
        box-sizing: border-box !important;

        background: linear-gradient(
            100deg,
            var(--fe-card) 0%,
            var(--fe-card2) 100%
        ) !important;

        border: 1px solid var(--fe-border) !important;
        border-radius: 13px !important;
        overflow: hidden !important;

        pointer-events: none !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-left {
        display: grid !important;
        grid-template-columns: 40px auto 22px !important;
        align-items: start !important;
        gap: 6px !important;
        align-self: start !important;
        padding-top: 5px !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-star {
        color: var(--fe-gold) !important;
        font-size: 34px !important;
        line-height: 1 !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-title {
        color: var(--fe-white) !important;
        font-size: 15px !important;
        font-weight: 850 !important;
        line-height: 1.1 !important;
        padding-top: 5px !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-help {
        width: 22px !important;
        height: 22px !important;
        line-height: 20px !important;
        text-align: center !important;
        color: var(--fe-help) !important;
        border: 1px solid var(--fe-help) !important;
        border-radius: 50% !important;
        font-size: 13px !important;
        margin-top: 1px !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-gauge-wrap {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        padding-top: 1px !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-gauge {
        width: 160px !important;
        height: 86px !important;
        display: block !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-value {
        color: var(--fe-gold) !important;
        font-size: 22px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
        margin-top: -2px !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-desc {
        color: var(--fe-white) !important;
        font-size: 14px !important;
        line-height: 1 !important;
        font-weight: 600 !important;
        margin-top: 5px !important;
    }

    section[data-testid="stSidebar"] .iqr-v65-spacer {
        height: 150px !important;
        min-height: 150px !important;
        width: 100% !important;
    }

    /* overlay cliccabile IQR */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v65_clickable"]
    div[data-testid="stButton"] {
        position: absolute !important;
        inset: 0 !important;
        z-index: 50 !important;
        width: 100% !important;
        height: 150px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v65_clickable"]
    div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 150px !important;
        min-height: 150px !important;
        opacity: .01 !important;
        background: transparent !important;
        border: 0 !important;
        color: transparent !important;
        font-size: 0 !important;
        cursor: pointer !important;
        box-shadow: none !important;
    }


    /* V78 - Budget: pulsanti +/- puliti e simmetrici */
    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] {
        overflow: visible !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] > div {
        gap: 5px !important;
        overflow: visible !important;
        background: transparent !important;
        border: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button {
        width: 38px !important;
        min-width: 38px !important;
        height: 38px !important;
        min-height: 38px !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 1px solid #8fc7f5 !important;
        border-radius: 9px !important;
        background: #164f82 !important;
        color: #ffffff !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button:hover {
        background: #1d609b !important;
        border-color: #ffffff !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button:focus {
        box-shadow: 0 0 0 1px rgba(255,255,255,.30) !important;
        outline: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button svg {
        width: 15px !important;
        height: 15px !important;
        color: #ffffff !important;
        fill: currentColor !important;
    }

    /* Menu */
    section[data-testid="stSidebar"] details > summary {
        min-height: 48px !important;
        background: #082744 !important;
        color: var(--fe-gold) !important;
        border: 2px solid var(--fe-gold) !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 950 !important;
    }


    /* V66 - IQR ESATTAMENTE COME V64 */
    /* ======================================================
       V55 - FIX MENU SOTTO IQR
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"] {
        position: relative !important;
        width: 100% !important;

        /* niente height fissa qui */
        height: auto !important;
        min-height: 0 !important;

        margin: 0 0 10px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-spacer {
        display: block !important;
        width: 100% !important;
        height: 225px !important;
        min-height: 225px !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card {
        position: absolute !important;
        inset: 0 auto auto 0 !important;
        z-index: 1 !important;

        width: 100% !important;
        height: 225px !important;

        box-sizing: border-box !important;
        padding: 15px 16px 16px 16px !important;

        background: linear-gradient(
            100deg,
            #0b3158 0%,
            #0a2b4d 100%
        ) !important;

        border: 1px solid #165387 !important;
        border-radius: 15px !important;
        overflow: hidden !important;

        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card * {
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-card {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-title {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;

        margin: 0 0 15px 0 !important;
        padding: 0 !important;

        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;
        text-align: center !important;
        white-space: nowrap !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-scale-wrap {
        position: relative !important;
        width: 84% !important;
        margin: 0 auto !important;
        padding: 0 0 30px 0 !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-scale {
        display: grid !important;
        grid-template-columns: 40fr 25fr 15fr 20fr !important;
        width: 100% !important;
        height: 38px !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-pointer {
        bottom: 3px !important;
        border-left: 16px solid transparent !important;
        border-right: 16px solid transparent !important;
        border-bottom: 21px solid #ffc21c !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-value {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card .iqr-gauge-description {
        display: block !important;
        width: 66% !important;
        min-width: 0 !important;
        margin: 8px auto 0 auto !important;
        padding: 12px 10px !important;

        color: #ffffff !important;
        font-size: 18px !important;
        line-height: 1.05 !important;
        font-weight: 950 !important;
        text-align: center !important;
        white-space: nowrap !important;

        border: 2px solid #050505 !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
    }

    /* overlay cliccabile, limitato ESATTAMENTE alla card */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    div[data-testid="stButton"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;

        width: 100% !important;
        height: 225px !important;

        z-index: 50 !important;
        margin: 0 !important;
        padding: 0 !important;

        pointer-events: auto !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 225px !important;
        min-height: 225px !important;

        margin: 0 !important;
        padding: 0 !important;

        background: transparent !important;
        border: 0 !important;
        border-radius: 15px !important;
        box-shadow: none !important;
        outline: none !important;

        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;

        opacity: .01 !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    div[data-testid="stButton"] > button * {
        display: none !important;
        visibility: hidden !important;
    }

    /* tooltip */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]::after {
        content: "Clicca per aprire dettaglio IQR";

        position: absolute !important;
        left: 50% !important;
        top: 186px !important;
        transform: translate(-50%, 4px) !important;

        z-index: 60 !important;

        padding: 6px 10px !important;

        background: rgba(5,18,34,.94) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,194,28,.55) !important;
        border-radius: 7px !important;

        font-size: 12px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
        white-space: nowrap !important;

        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]:hover::after {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translate(-50%, 0) !important;
    }



    /* ------------------------------------------------------
       IQR
       Mantiene le ultime modifiche V55.
       Cambiamo solo bordo/background per uniformarlo alle card.
       ------------------------------------------------------ */
    section[data-testid="stSidebar"]
    div[class*="st-key-iqr_v55_clickable"]
    .iqr-v55-card {
        background: linear-gradient(
            100deg,
            var(--fe-side-card) 0%,
            var(--fe-side-card-2) 100%
        ) !important;

        border: 1px solid var(--fe-side-border) !important;
        border-radius: 12px !important;
    }



    /* ======================================================
       V73 - IQR PULITA + HELP RIMOSSI
       ====================================================== */

    section[data-testid="stSidebar"] .iqr-card-v73 {
        width: 100% !important;
        height: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        margin: 0 !important;
        padding: 0 !important;
        color: #ffffff !important;
        text-align: center !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-top {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        width: 100% !important;
        margin: 0 0 16px 0 !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-star {
        color: #ffc21c !important;
        font-size: 24px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-title {
        color: #ffffff !important;
        font-size: 16px !important;
        line-height: 1 !important;
        font-weight: 900 !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-percent {
        color: #ffc21c !important;
        font-size: 16px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-bar-wrap {
        position: relative !important;
        width: 88% !important;
        height: 48px !important;
        margin: 0 auto 12px auto !important;
        padding-top: 14px !important;
        box-sizing: border-box !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-bar {
        width: 100% !important;
        height: 30px !important;
        background: linear-gradient(
            to right,
            #050505 0%,
            #050505 40%,
            #ff1616 40%,
            #ff1616 65%,
            #0b6df5 65%,
            #0b6df5 85%,
            #16a34a 85%,
            #16a34a 100%
        ) !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        border-radius: 0 !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-pointer {
        position: absolute !important;
        top: 0 !important;
        width: 0 !important;
        height: 0 !important;
        transform: translateX(-50%) !important;
        border-left: 10px solid transparent !important;
        border-right: 10px solid transparent !important;
        border-top: 14px solid #ffffff !important;
    }

    section[data-testid="stSidebar"] .iqr-card-v73 .iqr-v73-status {
        display: inline-block !important;
        min-width: 48% !important;
        margin: 2px auto 0 auto !important;
        padding: 8px 13px !important;
        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1 !important;
        font-weight: 900 !important;
        border: 1px solid rgba(255,255,255,.15) !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] .iqr-v71-legend,
    section[data-testid="stSidebar"] .iqr-v71-legend-item,
    section[data-testid="stSidebar"] .iqr-v71-swatch {
        display: none !important;
    }

    section[data-testid="stSidebar"] .fe-card-help,
    section[data-testid="stSidebar"] .iqr-v65-help,
    section[data-testid="stSidebar"] .iqr-v71-help,
    section[data-testid="stSidebar"] .iqr-v73-help {
        display: none !important;
    }

    section[data-testid="stSidebar"] .fe-side-card {
        grid-template-columns: 54px 1fr !important;
    }

    /* ======================================================
       V79 - CARD BUDGET IDENTICA IN TUTTE LE SEZIONI
       ====================================================== */

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"] {
        min-height: 106px !important;
        height: 106px !important;
        margin: 0 0 9px 0 !important;
        padding: 11px 14px !important;

        background: linear-gradient(
            100deg,
            #0b3158 0%,
            #0a2b4d 100%
        ) !important;

        border: 1px solid #155486 !important;
        border-radius: 13px !important;
        box-sizing: border-box !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-head {
        display: grid !important;
        grid-template-columns: 46px 1fr 24px !important;
        align-items: center !important;
        gap: 10px !important;
        margin: 0 0 7px 0 !important;
        min-height: 40px !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-icon {
        width: 46px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-icon img {
        width: 40px !important;
        height: 40px !important;
        object-fit: contain !important;
        filter: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-title {
        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1 !important;
        font-weight: 850 !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    .fe-budget-head::after {
        content: "✎";
        color: #c7d7e8 !important;
        font-size: 21px !important;
        line-height: 1 !important;
        text-align: right !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] {
        margin-left: 55px !important;
        width: calc(100% - 55px) !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] label {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] > div {
        display: flex !important;
        align-items: center !important;
        gap: 5px !important;
        overflow: visible !important;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] input {
        height: 43px !important;
        min-height: 43px !important;
        padding: 0 12px !important;

        color: #ffc21c !important;
        -webkit-text-fill-color: #ffc21c !important;
        background: #092947 !important;

        border: 1px solid #8fc7f5 !important;
        border-radius: 8px !important;

        font-size: 22px !important;
        line-height: 1 !important;
        font-weight: 950 !important;

        box-shadow: none !important;
        outline: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button {
        width: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;

        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;

        margin: 0 !important;
        padding: 0 !important;

        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;

        color: #ffffff !important;
        background: #164f82 !important;

        border: 1px solid #8fc7f5 !important;
        border-radius: 9px !important;

        box-shadow: none !important;
        outline: none !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button:hover {
        color: #ffffff !important;
        background: #1d609b !important;
        border-color: #ffffff !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button:focus,
    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button:active {
        color: #ffffff !important;
        background: #164f82 !important;
        border-color: #8fc7f5 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    section[data-testid="stSidebar"]
    div[class*="st-key-sidebar_budget_card"]
    div[data-testid="stNumberInput"] button svg {
        width: 15px !important;
        height: 15px !important;
        color: #ffffff !important;
        fill: currentColor !important;
        stroke: currentColor !important;
    }

</style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:


    if not PROFILO_LEGACY_SUPPORTATO:
        st.caption(
            "🔒 Dati isolati per lega e squadra"
        )

    header_html = (
        '<div class="fanta-header">'
        '<div class="fanta-brand">'
        '<div class="fanta-logo">''<img src="data:image/jpeg;base64,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" alt="FantaEleganza">''</div>'
        '<div>'
        '<div class="fanta-brand-title">'
        'FANTAELEGANZA <span>26/27</span>'
        '</div>'
        '<div class="fanta-brand-subtitle">'
        'Gestione asta e rosa'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )

    st.markdown(
        (
            '<div class="sidebar-profile">'
            '<span class="sidebar-profile-icon">●</span>'
            '<span class="sidebar-profile-name">'
            + html.escape(PROFILO_ATTIVO)
            + '</span>'
            '<span class="sidebar-profile-arrow">⌄</span>'
            '</div>'

            '<div style="'
            'margin:-3px 2px 8px 2px;'
            'padding:6px 9px;'
            'border-radius:8px;'
            'background:rgba(255,255,255,.045);'
            'border:1px solid rgba(255,255,255,.07);'
            '">'
            '<div style="'
            'color:#ffc21c;'
            'font-size:10px;'
            'font-weight:900;'
            'white-space:nowrap;'
            'overflow:hidden;'
            'text-overflow:ellipsis;'
            '">'
            + html.escape(
                LEGA_ATTIVA_NOME
            )
            + '</div>'
            '<div style="'
            'color:#ffffff;'
            'font-size:10px;'
            'margin-top:2px;'
            'white-space:nowrap;'
            'overflow:hidden;'
            'text-overflow:ellipsis;'
            '">'
            + html.escape(
                TEAM_ATTIVO_NOME
                or "Nessuna squadra"
            )
            + (
                " · "
                + html.escape(
                    " / ".join(
                        RUOLI_ATTIVI
                    )
                )
                if RUOLI_ATTIVI
                else ""
            )
            + '</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # MENU STRUMENTI: chiuso per default
    # --------------------------------------------------------


    # --------------------------------------------------------
    # INDICATORI PRINCIPALI
    # Soglia base eliminata
    # --------------------------------------------------------
    with st.container(
        key="sidebar_budget_card"
    ):

        st.markdown(
            """
            <div class="fe-budget-head">
                <div class="fe-budget-icon fe-budget-coins-icon"><img src="data:image/png;base64,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" alt="Budget"></div>
                <div class="fe-budget-title">Budget</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.number_input(
            "Budget",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            key="budget_asta_input",
            on_change=aggiorna_budget_da_widget,
            help=(
                "Budget totale che hai deciso di destinare all'asta."
            )
        )

    st.markdown(
        f"""
        <div class="fe-side-card">
            <div class="fe-card-icon fe-budget-rimanente-icon"><img src="data:image/png;base64,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" alt="Budget rimanente"></div>
            <div>
                <div class="fe-card-label">Budget rimanente</div>
                <div class="fe-card-value">{formatta_crediti(budget_rimanente)} €</div>
            </div>
        </div>

        <div class="fe-side-card">
            <div class="fe-card-icon fe-spesa-icon"><img src="data:image/png;base64,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" alt="Spesa effettiva"></div>
            <div>
                <div class="fe-card-label">Spesa effettiva</div>
                <div class="fe-card-value">{formatta_crediti(spesa_effettiva)} €</div>
            </div>
        </div>

        <div class="fe-side-card">
            <div class="fe-card-icon fe-oltre-soglia-icon"><img src="data:image/png;base64,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" alt="Oltre soglia"></div>
            <div>
                <div class="fe-card-label">Oltre soglia</div>
                <div class="fe-card-value">{formatta_crediti(oltre_soglia)} €</div>
            </div>
        </div>

        <div class="fe-side-card">
            <div class="fe-card-icon fe-giocatori-icon"><img src="data:image/png;base64,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" alt="Giocatori"></div>
            <div>
                <div class="fe-card-label">Giocatori</div>
                <div class="fe-card-value">{numero_rosa}/{MAX_GIOCATORI}</div>
            </div>
        </div>

        <div class="fe-side-card">
            <div class="fe-card-icon fe-portieri-icon"><img src="data:image/png;base64,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" alt="Portieri"></div>
            <div>
                <div class="fe-card-label">Portieri</div>
                <div class="fe-card-value">{numero_portieri}/{MIN_PORTIERI}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container(
        key="iqr_v55_clickable"
    ):

        # Bottone Streamlit reale, reso invisibile via CSS.
        if st.button(
            "Apri dettaglio IQR",
            key="btn_iqr_v55_overlay",
            use_container_width=True
        ):

            mostra_dettaglio_iqr(
                iqr,
                df_rosa_globale
            )

        st.markdown(
            (
                '<div class="iqr-v55-card">'
                + genera_html_gauge_iqr(
                    iqr
                )
                + '</div>'
            ),
            unsafe_allow_html=True
        )

        # Spacer reale: serve a far terminare correttamente il container
        # e impedisce che il menu successivo finisca sotto l'overlay.
        st.markdown(
            '<div class="iqr-v55-spacer"></div>',
            unsafe_allow_html=True
        )

    with st.expander(
        "☰  MENU",
        expanded=False
    ):

        menu_r1c1, menu_r1c2 = st.columns(2)

        with menu_r1c1:

            if st.button(
                "↪  Esci",
                use_container_width=True,
                key="btn_logout_profilo"
            ):

                for chiave_sessione in list(
                    st.session_state.keys()
                ):

                    if chiave_sessione in {
                        "profilo_attivo",
                        "profilo_login_select"
                    }:
                        continue

                    if (
                        chiave_sessione.startswith("_df_")
                        or chiave_sessione.startswith("_ultime_")
                        or chiave_sessione.startswith("_costi_")
                        or chiave_sessione.startswith("budget_")
                        or chiave_sessione.startswith("backup_")
                        or chiave_sessione.startswith("pdf_")
                    ):

                        st.session_state.pop(
                            chiave_sessione,
                            None
                        )

                azzera_contesto_multilega()

                st.session_state.pop(
                    "profilo_attivo",
                    None
                )

                st.session_state.pop(
                    "auth_user_id",
                    None
                )

                st.session_state.pop(
                    "auth_ok",
                    None
                )

                st.session_state.pop(
                    "profilo_login_select",
                    None
                )

                st.rerun()

        with menu_r1c2:

            if USA_DATABASE_CLOUD:

                if st.button(
                    "☁  Backup",
                    use_container_width=True,
                    key="btn_backup_cloud"
                ):

                    gestisci_backup_cloud()

            elif DB_PATH.exists():

                backup_profilo = (
                    crea_backup_logico_bytes()
                )

                st.download_button(
                    "☁  Backup",
                    data=backup_profilo,
                    file_name=(
                        "fantaeleganza_backup_"
                        + PROFILO_ATTIVO
                        .lower()
                        .replace(
                            " ",
                            "_"
                        )
                        + ".json"
                    ),
                    mime="application/json",
                    use_container_width=True
                )

        menu_r2c1, menu_r2c2 = st.columns(2)

        with menu_r2c1:

            if st.button(
                "⟳  Aggiorna",
                use_container_width=True,
                key="btn_aggiorna_app"
            ):

                invalida_cache_dati()
                st.rerun()

        with menu_r2c2:

            if st.button(
                "▤  Regole",
                use_container_width=True,
                key="btn_regole"
            ):

                mostra_regole()

        menu_r3c1, menu_r3c2 = st.columns(2)

        with menu_r3c1:

            if st.button(
                "📷  Snapshot",
                use_container_width=True,
                key="btn_snapshot"
            ):

                gestisci_snapshot()

        with menu_r3c2:

            nuovo_dark = st.toggle(
                "☾  Modalità scura",
                value=(
                    st.session_state.dark_mode
                ),
                key="toggle_dark"
            )

            if (
                nuovo_dark
                != st.session_state.dark_mode
            ):

                st.session_state.dark_mode = (
                    nuovo_dark
                )

                st.rerun()


    st.markdown(
        '<div style="'
        'color:#5f8db5;'
        'font-size:11px;'
        'padding:8px 3px 0 3px;'
        'letter-spacing:.2px;'
        '">'
        'MULTILEGA 2.0 &nbsp;|&nbsp; V101 Auctioneer 1.0'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# RIEPILOGO PRINCIPALE ORA NELLA SIDEBAR
# ============================================================

st.markdown('''<style>
.pf-team{background:#071a2f;color:white;padding:10px 14px;border-radius:10px 10px 0 0;font-weight:900;display:flex;justify-content:space-between}.pf-team span{color:#f5b51b}
.pf-pitch{min-height:420px;padding:16px 7px;border:3px solid white;border-radius:0 0 11px 11px;background:repeating-linear-gradient(90deg,#16863b 0,#16863b 46px,#118039 46px,#118039 92px);display:flex;flex-direction:column;justify-content:space-around;box-shadow:0 3px 12px #0002}
.pf-line{display:flex;justify-content:space-around;gap:4px}.pf-player{width:112px;min-height:58px;background:#fffffff2;border-radius:8px;padding:7px 5px;text-align:center;box-shadow:0 2px 6px #0003}.pf-name{font-size:.82rem;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pf-alt{font-size:.82rem;margin-top:6px;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pf-alt span{font-size:.82rem;font-weight:900}
@media(max-width:768px){.pf-pitch{min-height:410px}.pf-player{width:82px;min-height:58px}.pf-name,.pf-alt,.pf-alt span{font-size:.66rem}}
</style>''',unsafe_allow_html=True)


st.markdown("""
<style>
.pf-player-goal{
    min-height:38px !important;
    display:flex;
    align-items:center;
    justify-content:center;
}
.pf-player-goal .pf-name{
    font-size:.86rem !important;
    line-height:1.08;
}
.pf-alt-box{
    background:#eff6ff;
    border:1px solid #bfdbfe;
    border-radius:0 0 10px 10px;
    padding:8px 10px;
    margin-top:-1px;
}
.pf-alt-title{
    display:block;
    color:#64748b;
    font-size:.62rem;
    font-weight:800;
    margin-bottom:5px;
}
.pf-alt-chip{
    display:inline-block;
    color:#2563eb;
    font-size:.78rem;
    font-weight:900;
    margin:2px 10px 2px 0;
}

.pf-line{
    width:100% !important;
    max-width:100% !important;
    box-sizing:border-box !important;
    gap:10px !important;
    padding:7px 8px !important;
    align-items:stretch !important;
    justify-content:center !important;
    overflow:hidden !important;
}

.pf-player-goal{
    /* La larghezza reale viene determinata dalla linea.
       Mai più una min-width fissa che possa far uscire la card. */
    width:auto !important;
    min-width:0 !important;
    max-width:230px !important;
    flex:1 1 0 !important;

    min-height:92px !important;
    padding:9px 8px !important;
    box-sizing:border-box !important;

    border:1px solid rgba(15,23,42,.10) !important;
    border-radius:14px !important;
    background:rgba(255,255,255,.97) !important;

    display:flex !important;
    flex-direction:column !important;
    align-items:stretch !important;
    justify-content:center !important;

    overflow:hidden !important;
}

.pf-main-player,
.pf-sub-player{
    display:flex !important;
    flex:0 0 auto !important;
    align-items:baseline !important;
    justify-content:center !important;
    gap:5px !important;
    width:100% !important;

    white-space:nowrap !important;
    overflow:hidden !important;
}

.pf-main-player .pf-name,
.pf-sub-name{
    display:inline-block !important;
    min-width:0 !important;
    max-width:100% !important;

    font-size:.96rem !important;
    line-height:1.10 !important;
    font-weight:900 !important;

    white-space:nowrap !important;
    overflow:visible !important;
    text-overflow:clip !important;
}

.pf-main-player .pf-name{
    color:#16a34a !important;
}

.pf-sub-name{
    color:#2563eb !important;
}

.pf-mantra-role,
.pf-sub-role{
    display:inline-block !important;
    flex:0 0 auto !important;

    margin:0 !important;
    color:#111827 !important;

    font-size:.75rem !important;
    line-height:1 !important;
    font-weight:900 !important;

    white-space:nowrap !important;
}

.pf-sub-player{
    margin-top:10px !important;
    padding-top:0 !important;
    border-top:0 !important;
}

/* ==========================================================
   RIDUZIONE PROGRESSIVA DEI CARATTERI
   Più giocatori ci sono nella linea, più la card si restringe.
   ========================================================== */

.pf-line-count-1 .pf-player-goal{
    max-width:260px !important;
}

.pf-line-count-2 .pf-player-goal{
    max-width:245px !important;
}

.pf-line-count-3 .pf-player-goal{
    max-width:220px !important;
}

.pf-line-count-4 .pf-main-player .pf-name,
.pf-line-count-4 .pf-sub-name{
    font-size:.83rem !important;
}

.pf-line-count-4 .pf-mantra-role,
.pf-line-count-4 .pf-sub-role{
    font-size:.65rem !important;
}

.pf-line-count-5 .pf-main-player .pf-name,
.pf-line-count-5 .pf-sub-name{
    font-size:.73rem !important;
}

.pf-line-count-5 .pf-mantra-role,
.pf-line-count-5 .pf-sub-role{
    font-size:.57rem !important;
}

.pf-line-count-5{
    gap:6px !important;
    padding-left:5px !important;
    padding-right:5px !important;
}

@media(max-width:768px){
    .pf-pitch{
        min-height:470px !important;
        padding-left:1px !important;
        padding-right:1px !important;
    }

    .pf-line{
        gap:3px !important;
        padding-left:2px !important;
        padding-right:2px !important;
    }

    .pf-player-goal{
        min-height:78px !important;
        padding:6px 3px !important;
        border-radius:9px !important;
    }

    .pf-main-player .pf-name,
    .pf-sub-name{
        font-size:.68rem !important;
    }

    .pf-mantra-role,
    .pf-sub-role{
        font-size:.52rem !important;
    }

    .pf-line-count-4 .pf-main-player .pf-name,
    .pf-line-count-4 .pf-sub-name{
        font-size:.58rem !important;
    }

    .pf-line-count-4 .pf-mantra-role,
    .pf-line-count-4 .pf-sub-role{
        font-size:.46rem !important;
    }

    .pf-line-count-5 .pf-main-player .pf-name,
    .pf-line-count-5 .pf-sub-name{
        font-size:.51rem !important;
    }

    .pf-line-count-5 .pf-mantra-role,
    .pf-line-count-5 .pf-sub-role{
        font-size:.41rem !important;
    }

    .pf-sub-player{
        margin-top:7px !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# MULTILEGA 2.0 - AUCTIONEER 1.0
# ============================================================

def inizializza_listone_lega_asta(league_id):
    """
    Inizializza league_players usando il listone globale come catalogo.
    Non tocca le tabelle operative delle singole squadre.
    """
    league_id=int(league_id)
    conn=_portal_raw_connection()
    cur=conn.cursor()
    try:
        cur.execute("""
            INSERT INTO league_players (
                league_id, player_id, stato,
                assigned_team_id, prezzo_assegnazione, updated_at
            )
            SELECT ?, g.id, 'DISPONIBILE', NULL, NULL, CURRENT_TIMESTAMP
            FROM giocatori g
            WHERE NOT EXISTS (
                SELECT 1
                FROM league_players lp
                WHERE lp.league_id=?
                  AND lp.player_id=g.id
            )
        """,(league_id,league_id))

        cur.execute("""
            INSERT INTO team_budgets (
                league_id, team_id, budget_impostato,
                valore_acquisti, spesa_effettiva, updated_at
            )
            SELECT
                ?, t.id,
                COALESCE(r.budget_iniziale,500),
                0,0,CURRENT_TIMESTAMP
            FROM teams t
            LEFT JOIN league_rules r ON r.league_id=t.league_id
            WHERE t.league_id=? AND t.is_active=1
              AND NOT EXISTS (
                SELECT 1 FROM team_budgets b
                WHERE b.league_id=? AND b.team_id=t.id
              )
        """,(league_id,league_id,league_id))
        conn.commit()
    finally:
        _portal_close(conn)


def elenco_giocatori_asta_multilega(league_id):
    league_id=int(league_id)
    inizializza_listone_lega_asta(league_id)
    conn=_portal_raw_connection()
    cur=conn.cursor()
    try:
        cur.execute("""
            SELECT
                g.id,
                COALESCE(g.nome,''),
                COALESCE(g.squadra,''),
                COALESCE(g.ruolo_mantra,''),
                COALESCE(g.fvm_mantra,g.fvm,0),
                COALESCE(lp.stato,'DISPONIBILE'),
                lp.assigned_team_id,
                lp.prezzo_assegnazione
            FROM giocatori g
            JOIN league_players lp
              ON lp.player_id=g.id
             AND lp.league_id=?
            ORDER BY g.nome COLLATE NOCASE
        """,(league_id,))
        return [
            {
                "player_id":int(r[0]),
                "nome":str(r[1]),
                "squadra":str(r[2]),
                "ruolo_mantra":str(r[3]),
                "fvm":float(r[4] or 0),
                "stato":str(r[5] or "DISPONIBILE"),
                "assigned_team_id":int(r[6]) if r[6] is not None else None,
                "prezzo":float(r[7]) if r[7] is not None else None,
            }
            for r in (cur.fetchall() or [])
        ]
    finally:
        _portal_close(conn)


def riepilogo_team_asta_multilega(league_id):
    league_id=int(league_id)
    inizializza_listone_lega_asta(league_id)
    conn=_portal_raw_connection()
    cur=conn.cursor()
    try:
        cur.execute("""
            SELECT
                t.id,
                t.nome,
                COALESCE(b.budget_impostato,r.budget_iniziale,500),
                COALESCE(b.valore_acquisti,0),
                COALESCE(b.spesa_effettiva,0),
                COUNT(ro.id)
            FROM teams t
            LEFT JOIN league_rules r ON r.league_id=t.league_id
            LEFT JOIN team_budgets b
              ON b.league_id=t.league_id AND b.team_id=t.id
            LEFT JOIN rosters ro
              ON ro.league_id=t.league_id AND ro.team_id=t.id
            WHERE t.league_id=? AND t.is_active=1
            GROUP BY
                t.id,t.nome,b.budget_impostato,r.budget_iniziale,
                b.valore_acquisti,b.spesa_effettiva
            ORDER BY t.posizione,t.id
        """,(league_id,))
        return [
            {
                "team_id":int(r[0]),
                "nome":str(r[1]),
                "budget":float(r[2] or 0),
                "valore_acquisti":float(r[3] or 0),
                "spesa_effettiva":float(r[4] or 0),
                "giocatori":int(r[5] or 0)
            }
            for r in (cur.fetchall() or [])
        ]
    finally:
        _portal_close(conn)


def assegna_giocatore_banditore(league_id, player_id, team_id, prezzo):
    """
    Assegnazione server-side autorevole:
    - verifica ruolo Banditore/Admin
    - verifica giocatore disponibile
    - verifica squadra attiva e capienza rosa
    - verifica budget effettivo
    - aggiorna league_players, rosters, team_budgets e audit
    - sincronizza anche il workspace operativo della squadra target
    """
    league_id=int(league_id)
    player_id=int(player_id)
    team_id=int(team_id)
    prezzo=float(prezzo)

    if prezzo < 0:
        raise ValueError("Il prezzo non può essere negativo.")

    user_id=int(st.session_state.get("auth_user_id") or 0)
    conn=_portal_raw_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM league_members
            WHERE league_id=? AND user_id=? AND is_active=1
              AND (is_auctioneer=1 OR is_admin=1)
        """,(league_id,user_id))
        if int(cur.fetchone()[0] or 0)==0:
            raise PermissionError("Operazione riservata a Banditore o Admin.")

        cur.execute("""
            SELECT stato,assigned_team_id
            FROM league_players
            WHERE league_id=? AND player_id=?
            LIMIT 1
        """,(league_id,player_id))
        rp=cur.fetchone()
        if not rp:
            raise ValueError("Giocatore non presente nel listone della lega.")
        if str(rp[0] or "").upper()!="DISPONIBILE":
            raise ValueError("Il giocatore non è più disponibile.")

        cur.execute("""
            SELECT nome FROM teams
            WHERE league_id=? AND id=? AND is_active=1
            LIMIT 1
        """,(league_id,team_id))
        rt=cur.fetchone()
        if not rt:
            raise ValueError("Squadra non valida.")
        nome_team=str(rt[0])

        cur.execute("""
            SELECT
                COALESCE(max_giocatori,30),
                COALESCE(budget_iniziale,500),
                COALESCE(soglia_budget,500),
                COALESCE(moltiplicatore_oltre_soglia,1)
            FROM league_rules
            WHERE league_id=?
            LIMIT 1
        """,(league_id,))
        rr=cur.fetchone()
        if not rr:
            raise ValueError("Regolamento della lega non trovato.")

        max_giocatori=int(rr[0] or 30)
        budget_default=float(rr[1] or 500)
        soglia=float(rr[2] or budget_default)
        moltiplicatore=max(1,float(rr[3] or 1))

        cur.execute("""
            SELECT COUNT(*),COALESCE(SUM(prezzo_acquisto),0)
            FROM rosters
            WHERE league_id=? AND team_id=?
        """,(league_id,team_id))
        roster_count,valore_attuale=cur.fetchone()
        roster_count=int(roster_count or 0)
        valore_attuale=float(valore_attuale or 0)

        if roster_count >= max_giocatori:
            raise ValueError("La rosa della squadra è già completa.")

        cur.execute("""
            SELECT COALESCE(budget_impostato,?)
            FROM team_budgets
            WHERE league_id=? AND team_id=?
            LIMIT 1
        """,(budget_default,league_id,team_id))
        rb=cur.fetchone()
        budget=float(rb[0] if rb else budget_default)

        nuovo_valore=round(valore_attuale+prezzo,2)
        if nuovo_valore <= soglia:
            nuova_spesa=nuovo_valore
        else:
            nuova_spesa=round(soglia+(nuovo_valore-soglia)*moltiplicatore,2)

        if nuova_spesa > budget + 1e-9:
            raise ValueError(
                "Budget insufficiente: la spesa effettiva diventerebbe "
                + f"{nuova_spesa:.2f} su {budget:.2f} crediti."
            )

        cur.execute("""
            UPDATE league_players
            SET stato='ASSEGNATO',
                assigned_team_id=?,
                prezzo_assegnazione=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE league_id=? AND player_id=? AND stato='DISPONIBILE'
        """,(team_id,prezzo,league_id,player_id))

        if cur.rowcount==0:
            raise ValueError("Il giocatore è stato appena assegnato da un'altra operazione.")

        cur.execute("""
            INSERT INTO rosters (
                league_id,team_id,player_id,prezzo_acquisto,fonte,assigned_at,updated_at
            )
            VALUES (?,?,?,?,'AUCTIONEER',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
            ON CONFLICT(league_id,team_id,player_id)
            DO UPDATE SET
                prezzo_acquisto=excluded.prezzo_acquisto,
                fonte='AUCTIONEER',
                updated_at=CURRENT_TIMESTAMP
        """,(league_id,team_id,player_id,prezzo))

        cur.execute("""
            INSERT INTO team_budgets (
                league_id,team_id,budget_impostato,valore_acquisti,spesa_effettiva,updated_at
            )
            VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)
            ON CONFLICT(league_id,team_id)
            DO UPDATE SET
                valore_acquisti=excluded.valore_acquisti,
                spesa_effettiva=excluded.spesa_effettiva,
                updated_at=CURRENT_TIMESTAMP
        """,(league_id,team_id,budget,nuovo_valore,nuova_spesa))

        # Sincronizza il workspace fisico della squadra target.
        tab_team="giocatori_ml_l"+str(league_id)+"_t"+str(team_id)
        try:
            cur.execute(
                f"""UPDATE {tab_team}
                    SET stato='MIO',
                        prezzo_acquisto=?,
                        ultimo_aggiornamento=CURRENT_TIMESTAMP
                    WHERE id=?""",
                (prezzo,player_id)
            )
        except Exception:
            # Se il team non ha mai aperto l'app, il suo workspace può
            # non esistere ancora: rosters resta comunque autorevole.
            pass

        cur.execute("""
            INSERT INTO audit_log (
                league_id,user_id,team_id,azione,entita,entita_id,dettagli_json,created_at
            )
            VALUES (?,?,?,'PLAYER_ASSIGNED','PLAYER',?,?,CURRENT_TIMESTAMP)
        """,(
            league_id,user_id,team_id,str(player_id),
            json.dumps({
                "prezzo":prezzo,
                "team":nome_team,
                "valore_acquisti":nuovo_valore,
                "spesa_effettiva":nuova_spesa
            },ensure_ascii=False)
        ))

        conn.commit()
        return {
            "team":nome_team,
            "valore_acquisti":nuovo_valore,
            "spesa_effettiva":nuova_spesa,
            "budget":budget
        }

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        _portal_close(conn)


def render_banditore_asta():
    if not any(r in RUOLI_ATTIVI for r in ("AUCTIONEER","ADMIN")):
        st.error("Questa sezione è riservata a Banditore o Admin.")
        return

    league_id=int(st.session_state.get("ml_league_id"))
    st.subheader("🔨 Banditore · Auctioneer 1.0")
    st.caption(
        "Assegna manualmente il giocatore vincente a una squadra. "
        "L'operazione aggiorna listone di lega, rosa, budget e audit."
    )

    try:
        giocatori=elenco_giocatori_asta_multilega(league_id)
        teams=riepilogo_team_asta_multilega(league_id)
    except Exception as errore:
        st.error("Impossibile caricare la console Banditore: "+str(errore))
        return

    disponibili=[g for g in giocatori if g["stato"].upper()=="DISPONIBILE"]

    m1,m2,m3=st.columns(3)
    m1.metric("Disponibili",len(disponibili))
    m2.metric("Assegnati",len(giocatori)-len(disponibili))
    m3.metric("Squadre",len(teams))

    if not disponibili:
        st.success("Non ci sono più giocatori disponibili.")
        return
    if not teams:
        st.warning("La lega non contiene squadre attive.")
        return

    ricerca=st.text_input(
        "Cerca giocatore",
        placeholder="Nome, squadra o ruolo...",
        key="auctioneer_search"
    ).strip().lower()

    filtrati=disponibili
    if ricerca:
        filtrati=[
            g for g in disponibili
            if ricerca in g["nome"].lower()
            or ricerca in g["squadra"].lower()
            or ricerca in g["ruolo_mantra"].lower()
        ]

    if not filtrati:
        st.info("Nessun giocatore disponibile corrisponde alla ricerca.")
        return

    etichette_giocatori={
        f'{g["nome"]} · {g["squadra"]} · {g["ruolo_mantra"]} · FVM {g["fvm"]:g}':g
        for g in filtrati
    }
    scelta_g=st.selectbox(
        "Giocatore",
        list(etichette_giocatori.keys()),
        key="auctioneer_player"
    )
    g=etichette_giocatori[scelta_g]

    etichette_team={
        f'{t["nome"]} · {t["giocatori"]} gioc. · {t["spesa_effettiva"]:g}/{t["budget"]:g} cr.':t
        for t in teams
    }
    c1,c2=st.columns([2,1])
    with c1:
        scelta_t=st.selectbox(
            "Squadra vincitrice",
            list(etichette_team.keys()),
            key="auctioneer_team"
        )
    with c2:
        prezzo=st.number_input(
            "Prezzo finale",
            min_value=0.0,
            value=1.0,
            step=1.0,
            key="auctioneer_price"
        )

    t=etichette_team[scelta_t]

    st.info(
        f'**{g["nome"]}** ({g["ruolo_mantra"]}, {g["squadra"]}) → '
        f'**{t["nome"]}** a **{prezzo:g} crediti**'
    )

    if st.button(
        "✅ ASSEGNA GIOCATORE",
        type="primary",
        use_container_width=True,
        key="auctioneer_assign"
    ):
        try:
            risultato=assegna_giocatore_banditore(
                league_id,g["player_id"],t["team_id"],prezzo
            )
            # Rimuove le cache locali se il Banditore sta anche gestendo
            # la propria squadra.
            invalida_cache_dati()
            st.session_state["auctioneer_msg"]=(
                f'{g["nome"]} assegnato a {risultato["team"]} '
                f'a {prezzo:g} crediti.'
            )
            st.rerun(scope="fragment")
        except Exception as errore:
            st.error(str(errore))

    if st.session_state.get("auctioneer_msg"):
        st.success(st.session_state.pop("auctioneer_msg"))

    st.markdown("#### Situazione squadre")
    df_team=pd.DataFrame([
        {
            "Squadra":t["nome"],
            "Giocatori":t["giocatori"],
            "Valore acquisti":t["valore_acquisti"],
            "Spesa effettiva":t["spesa_effettiva"],
            "Budget":t["budget"],
            "Residuo":round(t["budget"]-t["spesa_effettiva"],2)
        }
        for t in teams
    ])
    st.dataframe(df_team,use_container_width=True,hide_index=True)


# ============================================================
# MULTILEGA 1.8 - NAVIGAZIONE A FRAGMENT
# ============================================================

@st.fragment
def render_navigazione_e_pagina():
    # ============================================================
    # NAVBAR
    # ============================================================

    PAGINE = [
        ("🏠", "DASHBOARD"),
        ("☷", "LISTONE"),
        ("🔨", "ASTA"),
        ("👕", "ROSA"),
        ("▣", "MODULI"),
        ("⚽", "FORMAZIONI TIPO"),
        ("🔴", "VENDUTI AD AVVERSARI")
    ]

    PAGINE.append(("👤", "PROFILO"))

    if any(r in RUOLI_ATTIVI for r in ("AUCTIONEER", "ADMIN")):
        PAGINE.append(("🔨", "BANDITORE"))

    if "ADMIN" in RUOLI_ATTIVI:
        PAGINE.append(
            (
                "⚙️",
                "GESTIONE LEGA"
            )
        )

    def _naviga_a(pagina_destinazione):
        """
        V100: essendo la navbar dentro st.fragment, il click aggiorna
        soltanto il fragment di navigazione/pagina. Il boot globale,
        l'autenticazione, la sidebar e le verifiche DB non vengono
        rieseguite durante un semplice cambio sezione.
        """
        st.session_state.pagina = pagina_destinazione


    st.markdown(
        '<div class="nav-title">Navigazione</div>',
        unsafe_allow_html=True
    )

    nav_cols = st.columns(len(PAGINE))

    for col, (icona, pagina_nav) in zip(nav_cols, PAGINE):
        with col:
            st.button(
                f"{icona}  {pagina_nav}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.pagina == pagina_nav
                    else "secondary"
                ),
                key=f"nav_{pagina_nav}",
                on_click=_naviga_a,
                args=(pagina_nav,)
            )

    sezione = st.session_state.pagina


    # ============================================================
    # TOOLBAR UNDO COMPATTA
    # ============================================================

    if sezione not in ("GESTIONE LEGA", "PROFILO", "BANDITORE"):

        operazioni_undo = carica_ultime_operazioni()

        undo1, undo2 = st.columns([1.7, 7])

        with undo1:
            if st.button(
                "↶ ANNULLA ULTIMA OPERAZIONE",
                use_container_width=True,
                disabled=operazioni_undo.empty,
                key="btn_undo_generale"
            ):
                conferma_undo()

        with undo2:
            if not operazioni_undo.empty:
                ultima = operazioni_undo.iloc[0]
                testo_ultima = (
                    f'<div class="operation-info">'
                    f'Ultima operazione annullabile:&nbsp;'
                    f'<b>{html.escape(str(ultima["Operazione"]))}'
                    f' — {html.escape(str(ultima["Giocatore"]))}</b>'
                    f'&nbsp;({len(operazioni_undo)}/10)'
                    f'</div>'
                )
                st.markdown(testo_ultima, unsafe_allow_html=True)

        with st.expander("📜 Ultime operazioni", expanded=False):
            if operazioni_undo.empty:
                st.caption("Nessuna operazione registrata.")
            else:
                st.dataframe(
                    operazioni_undo[["Operazione", "Giocatore", "Data"]],
                    use_container_width=True,
                    hide_index=True
                )
    else:
        operazioni_undo = pd.DataFrame()



    @st.dialog("Ripristina tutti i venduti agli avversari")
    def conferma_ripristina_tutti_avversari():

        df_corrente = carica_tutti_giocatori()

        numero = int(
            (
                df_corrente["Stato"]
                == "AVVERSARIO"
            ).sum()
        )

        st.warning(
            f"Stai per rendere nuovamente DISPONIBILI "
            f"tutti i {numero} giocatori assegnati agli avversari."
        )

        st.caption(
            "La tua rosa, i prezzi dei tuoi acquisti e i costi di svincolo "
            "non verranno modificati."
        )

        conferma = st.checkbox(
            "Confermo di voler ripristinare tutti i giocatori degli avversari",
            key="conferma_reset_totale_avversari"
        )

        if st.button(
            "↩️ RIPRISTINA TUTTI",
            type="primary",
            use_container_width=True,
            disabled=not conferma,
            key="esegui_reset_totale_avversari"
        ):

            ripristinati = (
                ripristina_tutti_giocatori_avversari()
            )

            st.session_state[
                "messaggio_reset_avversari"
            ] = (
                f"Ripristino completato: {ripristinati} giocatori "
                f"sono tornati disponibili."
            )

            st.rerun()


    @st.dialog("Elimina tutta la rosa")
    def conferma_elimina_tutta_rosa():
        df_corrente = carica_tutti_giocatori()
        numero = int((df_corrente["Stato"] == "MIO").sum())

        st.warning(
            f"Stai per eliminare tutti i {numero} giocatori presenti nella rosa. "
            "Torneranno DISPONIBILI e i prezzi di acquisto verranno azzerati."
        )
        st.caption(
            "Verranno azzerati anche i costi di svincolo e la cronologia UNDO."
        )

        conferma = st.checkbox(
            "Confermo di voler eliminare tutta la rosa",
            key="conferma_reset_totale_rosa"
        )

        if st.button(
            "🗑️ ELIMINA TUTTA LA ROSA",
            type="primary",
            use_container_width=True,
            disabled=not conferma,
            key="esegui_reset_totale_rosa"
        ):
            eliminati = elimina_tutta_la_rosa()
            st.session_state["messaggio_reset_rosa"] = (
                f"Rosa eliminata: {eliminati} giocatori sono tornati disponibili."
            )
            st.rerun()


    # ============================================================
    # ADMIN LEGA
    # ============================================================

    if sezione == "PROFILO":

        render_profilo_utente()

    elif sezione == "GESTIONE LEGA":

        render_admin_multilega()

    elif sezione == "BANDITORE":

        render_banditore_asta()


    # ============================================================
    # DASHBOARD
    # ============================================================

    elif sezione == "DASHBOARD":

        st.subheader(
            "📊 Dashboard"
        )

        snapshot_disponibili = (
            elenco_snapshot(PROFILO_ATTIVO)
        )

        st.caption(
            f"💾 Protezione attiva — "
            f"{len(snapshot_disponibili)} snapshot disponibili "
            f"(massimo {MAX_SNAPSHOT}) · "
            f"UNDO fino a {MAX_UNDO} operazioni. "
            + (
                "🌐 Database Cloud persistente attivo."
                if USA_DATABASE_CLOUD
                else "💻 Database locale attivo."
            )
        )


        # --------------------------------------------------------
        # STAMPA ROSA E MODULI
        # --------------------------------------------------------

        stampa_col1, stampa_col2 = st.columns(
            [
                1.6,
                4.4
            ]
        )

        with stampa_col1:

            if st.button(
                "🖨️ STAMPA ROSA E MODULI",
                use_container_width=True,
                disabled=(
                    numero_rosa == 0
                ),
                key="btn_genera_pdf_rosa_moduli"
            ):

                with st.spinner(
                    "Creazione PDF..."
                ):

                    try:

                        st.session_state[
                            "pdf_rosa_moduli"
                        ] = (
                            genera_pdf_rosa_e_moduli(
                                df_rosa_globale,
                                valore_attivi,
                                costi_svincoli,
                                valore_acquisti,
                                spesa_effettiva
                            )
                        )

                    except Exception as errore:

                        st.session_state[
                            "pdf_rosa_moduli"
                        ] = None

                        st.error(
                            f"Errore durante la creazione del PDF: {errore}"
                        )

        with stampa_col2:

            if st.session_state.get(
                "pdf_rosa_moduli"
            ):

                st.download_button(
                    "⬇️ SCARICA PDF ROSA E MODULI",
                    data=(
                        st.session_state[
                            "pdf_rosa_moduli"
                        ]
                    ),
                    file_name=(
                        "FANTAELEGANZA_26-27_ROSA_E_MODULI.pdf"
                    ),
                    mime=(
                        "application/pdf"
                    ),
                    use_container_width=True,
                    key="download_pdf_rosa_moduli"
                )

            elif numero_rosa > 0:

                st.caption(
                    "Premi STAMPA ROSA E MODULI per preparare il PDF scaricabile."
                )

        if numero_rosa == 0:

            st.info(
                "La rosa è ancora vuota. "
                "Vai nella sezione ASTA "
                "per iniziare ad acquistare."
            )

        else:

            if (
                numero_rosa
                == MAX_GIOCATORI
                and numero_portieri
                >= MIN_PORTIERI
            ):

                st.success(
                    "✅ Rosa completa e conforme."
                )

            elif (
                numero_portieri
                < MIN_PORTIERI
            ):

                mancanti = (
                    MIN_PORTIERI
                    - numero_portieri
                )

                st.warning(
                    f"⚠️ Mancano ancora "
                    f"{mancanti} portieri."
                )

            dleft, dright = st.columns(
                [
                    1,
                    1
                ]
            )

            with dleft:

                st.markdown(
                    "#### Distribuzione rosa"
                )

                distribuzione = (
                    df_rosa_globale.copy()
                )

                distribuzione[
                    "Primo ruolo"
                ] = (
                    distribuzione["RM"]
                    .apply(
                        primo_ruolo
                    )
                )

                righe = []

                for ruolo in ELENCO_RUOLI:

                    gruppo = (
                        distribuzione[
                            distribuzione[
                                "Primo ruolo"
                            ]
                            .str.upper()
                            == ruolo.upper()
                        ]
                    )

                    numero_giocatori = len(
                        gruppo
                    )

                    righe.append({
                        "Ruolo":
                            ruolo,

                        "Giocatori":
                            numero_giocatori,

                        "Valore":
                            formatta_crediti(
                                gruppo[
                                    "Prezzo"
                                ]
                                .fillna(0)
                                .sum()
                            )
                            if not gruppo.empty
                            else "0,00"
                    })

                df_distribuzione = (
                    pd.DataFrame(
                        righe
                    )
                )

                def colora_riga_ruolo(
                    riga
                ):

                    numero = int(
                        riga[
                            "Giocatori"
                        ]
                    )

                    # 0-1: rosso
                    if numero < 2:

                        colore = (
                            "background-color: #fee2e2; "
                            "color: #991b1b; "
                            "font-weight: 700;"
                        )

                    # 3: giallo
                    elif numero == 3:

                        colore = (
                            "background-color: #fef3c7; "
                            "color: #92400e; "
                            "font-weight: 700;"
                        )

                    # 4 o più: verde
                    elif numero >= 4:

                        colore = (
                            "background-color: #dcfce7; "
                            "color: #166534; "
                            "font-weight: 700;"
                        )

                    # Esattamente 2: neutro
                    else:

                        colore = ""

                    return [
                        colore
                        for _ in riga.index
                    ]

                st.dataframe(
                    df_distribuzione.style.apply(
                        colora_riga_ruolo,
                        axis=1
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            with dright:

                st.markdown(
                    "#### ⭐ Modulo consigliato"
                )

                classifica = (
                    classifica_moduli(
                        df_rosa_globale
                    )
                )

                if classifica:

                    migliore = (
                        classifica[0]
                    )

                    st.success(
                        f"**{migliore['Modulo']}** "
                        f"— punteggio strategico "
                        f"**{migliore['Punteggio']}/100** "
                        f"— copertura media "
                        f"**{migliore['Copertura media']}%** "
                        f"— slot scoperti "
                        f"**{migliore['Scoperti']}** "
                        f"— slot deboli "
                        f"**{migliore['Deboli']}**"
                        + (
                            f" ({migliore['Ruoli deboli']})"
                            if migliore[
                                "Ruoli deboli"
                            ]
                            else ""
                        )
                    )

                    tabella_classifica = (
                        pd.DataFrame(
                            classifica
                        )[
                            [
                                "Posizione",
                                "Modulo",
                                "Punteggio",
                                "Copertura media",
                                "Scoperti",
                                "Deboli",
                                "Al 100%"
                            ]
                        ]
                    )

                    st.dataframe(
                        tabella_classifica,
                        use_container_width=True,
                        hide_index=True
                    )


    # ============================================================
    # LISTONE
    # ============================================================

    elif sezione == "LISTONE":

        st.subheader(
            "☷ Listone giocatori"
        )

        file_caricato = st.file_uploader(
            "Carica il listone Fantacalcio.it",
            type=[
                "xlsx",
                "xlsm"
            ]
        )

        if file_caricato is not None:

            try:

                contenuto = (
                    file_caricato
                    .getvalue()
                )

                excel = pd.ExcelFile(
                    io.BytesIO(
                        contenuto
                    ),
                    engine="openpyxl"
                )

                foglio_tutti = None

                for nome_foglio in (
                    excel.sheet_names
                ):

                    if (
                        nome_foglio
                        .strip()
                        .upper()
                        == "TUTTI"
                    ):

                        foglio_tutti = (
                            nome_foglio
                        )

                        break

                if foglio_tutti is None:

                    st.error(
                        "Non trovo il foglio Tutti."
                    )

                else:

                    df_excel = pd.read_excel(
                        io.BytesIO(
                            contenuto
                        ),
                        sheet_name=(
                            foglio_tutti
                        ),
                        engine="openpyxl",
                        header=1
                    )

                    df_excel = (
                        df_excel
                        .dropna(
                            axis=1,
                            how="all"
                        )
                        .dropna(
                            axis=0,
                            how="all"
                        )
                    )

                    df_excel.columns = [
                        str(c).strip()
                        for c
                        in df_excel.columns
                    ]

                    obbligatorie = {
                        "Id",
                        "R",
                        "RM",
                        "Nome",
                        "Squadra"
                    }

                    mancanti = (
                        obbligatorie
                        - set(
                            df_excel.columns
                        )
                    )

                    if mancanti:

                        st.error(
                            "Formato non valido. "
                            "Colonne mancanti: "
                            + ", ".join(
                                sorted(
                                    mancanti
                                )
                            )
                        )

                    else:

                        nuovi, aggiornati = (
                            importa_listone_nel_database(
                                df_excel
                            )
                        )

                        st.success(
                            "✅ Listone importato con successo — "
                            f"{st.session_state.get('ultimo_upload_listone', '')}. "
                            f"Nuovi: {nuovi} — "
                            f"Aggiornati: {aggiornati}. "
                            "I giocatori invariati non sono stati riscritti."
                        )

            except Exception as errore:

                st.error(
                    f"Errore: {errore}"
                )

        df = (
            df_completo.copy()
        )

        if df.empty:

            st.info(
                "Il database è vuoto."
            )

        else:

            f1, f2, f3 = st.columns(3)

            with f1:

                filtro_stato = (
                    st.selectbox(
                        "Stato",
                        [
                            "TUTTI",
                            "DISPONIBILE",
                            "MIO",
                            "AVVERSARIO"
                        ]
                    )
                )

            with f2:

                filtro_ruolo = (
                    st.selectbox(
                        "Primo ruolo",
                        [
                            "TUTTI"
                        ]
                        + ELENCO_RUOLI
                    )
                )

            squadre = sorted(
                df[
                    "Squadra"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            with f3:

                filtro_squadra = (
                    st.selectbox(
                        "Squadra",
                        [
                            "TUTTE"
                        ]
                        + squadre
                    )
                )

            ricerca = st.text_input(
                "🔎 Cerca giocatore"
            )

            filtrato = (
                df.copy()
            )

            if (
                filtro_stato
                != "TUTTI"
            ):

                filtrato = (
                    filtrato[
                        filtrato[
                            "Stato"
                        ]
                        == filtro_stato
                    ]
                )

            if (
                filtro_ruolo
                != "TUTTI"
            ):

                filtrato = (
                    filtrato[
                        filtrato[
                            "RM"
                        ]
                        .apply(
                            primo_ruolo
                        )
                        .str.upper()
                        == filtro_ruolo.upper()
                    ]
                )

            if (
                filtro_squadra
                != "TUTTE"
            ):

                filtrato = (
                    filtrato[
                        filtrato[
                            "Squadra"
                        ]
                        == filtro_squadra
                    ]
                )

            if ricerca:

                testo = (
                    ricerca
                    .lower()
                    .strip()
                )

                filtrato = (
                    filtrato[
                        filtrato[
                            "Nome"
                        ]
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            testo,
                            na=False
                        )
                    ]
                )

            filtrato[
                "Priorita"
            ] = (
                filtrato[
                    "RM"
                ]
                .apply(
                    priorita_ruolo
                )
            )

            filtrato = (
                filtrato
                .sort_values(
                    by=[
                        "Priorita",
                        "FVM",
                        "Nome"
                    ],
                    ascending=[
                        True,
                        False,
                        True
                    ],
                    na_position="last"
                )
            )

            vista = (
                filtrato[
                    [
                        "Id",
                        "R",
                        "RM",
                        "Nome",
                        "Squadra",
                        "Qt.A",
                        "Qt.I",
                        "Diff.",
                        "FVM",
                        "Stato",
                        "Prezzo"
                    ]
                ]
                .copy()
            )

            vista[
                "Prezzo"
            ] = (
                vista[
                    "Prezzo"
                ]
                .apply(
                    formatta_crediti
                )
            )

            st.dataframe(
                vista,
                use_container_width=True,
                hide_index=True,
                height=620
            )


    # ============================================================
    # ASTA
    # ============================================================

    elif sezione == "ASTA":

        st.markdown(
            """
            <style>
            /* VERSIONE B - CONSOLE ASTA COMPATTA */
            section[data-testid="stMain"] div[data-testid="stNumberInput"] input {
                font-size:1.22rem !important;
                font-weight:800 !important;
                text-align:center !important;
                min-height:58px !important;
                border:2px solid #94a3b8 !important;
                border-radius:10px !important;
                background:#ffffff !important;
            }

            section[data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
                border:2px solid #94a3b8 !important;
                border-radius:10px !important;
                background:#ffffff !important;
                min-height:50px !important;
            }

            section[data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
            section[data-testid="stMain"] div[data-testid="stNumberInput"]:focus-within input {
                border-color:#071a2f !important;
                box-shadow:0 0 0 3px rgba(7,26,47,.10) !important;
            }

            /* DISPONIBILITÀ: croce rossa compatta e ben visibile */
            div[class*="st-key-btn_infortunio_"] .stButton > button {
                border:none !important;
                background:transparent !important;
                box-shadow:none !important;
                padding:0 !important;
                min-height:42px !important;
                height:42px !important;
                font-size:1.55rem !important;
                line-height:1 !important;
            }

            /* STRISCIA OPERATIVA ASTA: stessa altezza reale per tutti i blocchi */
            div[class*="st-key-btn_acquista_"] .stButton,
            div[class*="st-key-btn_avversario_"] .stButton {
                height:76px !important;
            }

            div[class*="st-key-btn_acquista_"] .stButton > button,
            div[class*="st-key-btn_avversario_"] .stButton > button {
                min-height:76px !important;
                height:76px !important;
                width:100% !important;
                font-weight:900 !important;
                font-size:1rem !important;
                border-radius:8px !important;
                padding-top:0 !important;
                padding-bottom:0 !important;
            }

            /* OFFERTA: alza l'intero controllo, compresi +/- */
            section[data-testid="stMain"] div[data-testid="stNumberInput"] > div,
            section[data-testid="stMain"] div[data-testid="stNumberInput"] [data-baseweb="input"],
            section[data-testid="stMain"] div[data-testid="stNumberInput"] [data-baseweb="base-input"] {
                min-height:76px !important;
                height:76px !important;
            }

            section[data-testid="stMain"] div[data-testid="stNumberInput"] input {
                min-height:76px !important;
                height:76px !important;
                font-size:1.22rem !important;
                font-weight:800 !important;
                text-align:center !important;
                border-radius:8px 0 0 8px !important;
                padding-top:0 !important;
                padding-bottom:0 !important;
            }

            section[data-testid="stMain"] div[data-testid="stNumberInput"] button {
                height:38px !important;
                min-height:38px !important;
            }

            /* Metriche: riferimento visivo per l'altezza della riga */
            section[data-testid="stMain"] div[data-testid="stMetric"] {
                min-height:76px !important;
                height:76px !important;
                padding:8px 12px !important;
                display:flex !important;
                flex-direction:column !important;
                justify-content:center !important;
                box-sizing:border-box !important;
            }

            @media (max-width:768px) {
                section[data-testid="stMain"] div[data-testid="stNumberInput"] input {
                    font-size:1.08rem !important;
                    min-height:52px !important;
                }

                section[data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
                    min-height:46px !important;
                }

                div[class*="st-key-btn_acquista_"] .stButton > button,
                div[class*="st-key-btn_avversario_"] .stButton > button {
                    min-height:68px !important;
                    height:68px !important;
                }
            }

    /* ==========================================================
       V74 - POPUP DETTAGLIO IQR
       ========================================================== */

    /* Titolo interno IQR nel popup */
    div[data-testid="stDialog"] .iqr-gauge-card .iqr-v73-star,
    div[role="dialog"] .iqr-gauge-card .iqr-v73-star {
        color: #ffc21c !important;
        font-size: 26px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
    }

    div[data-testid="stDialog"] .iqr-gauge-card .iqr-v73-title,
    div[role="dialog"] .iqr-gauge-card .iqr-v73-title {
        color: #111827 !important;
        font-size: 24px !important;
        line-height: 1 !important;
        font-weight: 900 !important;
    }

    div[data-testid="stDialog"] .iqr-gauge-card .iqr-v73-percent,
    div[role="dialog"] .iqr-gauge-card .iqr-v73-percent {
        color: #ffc21c !important;
        font-size: 24px !important;
        line-height: 1 !important;
        font-weight: 950 !important;
    }

    /* Stato qualitativo nel popup */
    div[data-testid="stDialog"] .iqr-gauge-card .iqr-v73-status,
    div[role="dialog"] .iqr-gauge-card .iqr-v73-status {
        color: #ffffff !important;
        font-size: 22px !important;
        line-height: 1.15 !important;
        font-weight: 900 !important;
        padding: 10px 22px !important;
    }

    /* Mantiene ben leggibile e centrata l'intestazione */
    div[data-testid="stDialog"] .iqr-gauge-card .iqr-v73-top,
    div[role="dialog"] .iqr-gauge-card .iqr-v73-top {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
    }

    /* Compatibilità con eventuale markup IQR precedente usato nel dettaglio */
    div[data-testid="stDialog"] .iqr-v71-star,
    div[role="dialog"] .iqr-v71-star {
        color: #ffc21c !important;
        font-size: 26px !important;
        font-weight: 950 !important;
    }

    div[data-testid="stDialog"] .iqr-v71-title,
    div[role="dialog"] .iqr-v71-title {
        color: #111827 !important;
        font-size: 24px !important;
        font-weight: 900 !important;
    }

    div[data-testid="stDialog"] .iqr-v71-percent,
    div[role="dialog"] .iqr-v71-percent {
        color: #ffc21c !important;
        font-size: 24px !important;
        font-weight: 950 !important;
    }

    div[data-testid="stDialog"] .iqr-v71-status,
    div[role="dialog"] .iqr-v71-status {
        color: #ffffff !important;
        font-size: 22px !important;
        line-height: 1.15 !important;
        font-weight: 900 !important;
    }
    </style>
            """,
            unsafe_allow_html=True
        )

        df = df_completo.copy()

        if df.empty:
            st.info("Prima devi caricare il listone.")

        else:
            disponibili = (
                df[
                    df["Stato"] == "DISPONIBILE"
                ]
                .copy()
                .sort_values("Nome")
                .reset_index(drop=True)
            )

            if disponibili.empty:

                st.info(
                    "Nessun giocatore disponibile."
                )

            else:

                opzioni_asta = (
                    disponibili
                    .apply(
                        lambda r:
                        f"{r['Nome']} — "
                        f"{r['Squadra']} — "
                        f"{r['RM']}",
                        axis=1
                    )
                    .tolist()
                )

                scelta = st.selectbox(
                    "🔎 CERCA GIOCATORE / SQUADRA / RUOLO",
                    options=opzioni_asta,
                    index=None,
                    placeholder=(
                        "Scrivi nome, squadra o ruolo…"
                    ),
                    key="search_select_asta"
                )

                if scelta is None:

                    st.info(
                        "⌨️ Scrivi poche lettere: il giocatore viene proposto "
                        "subito. Puoi cercare anche per squadra o ruolo."
                    )

                else:

                    giocatore = (
                        disponibili.iloc[
                            opzioni_asta.index(
                                scelta
                            )
                        ]
                    )

                    colore_nome_asta = (
                        colore_fvm_mantra(
                            giocatore.get(
                                "RM",
                                ""
                            ),
                            giocatore.get(
                                "FVM M"
                            )
                        )
                    )

                    priorita_acquisto = (
                        valuta_priorita_acquisto(
                            giocatore,
                            df_rosa_globale,
                            df_completo
                        )
                    )

                    (
                        bg_priorita,
                        fg_priorita,
                        bordo_priorita
                    ) = stile_priorita_acquisto(
                        priorita_acquisto[
                            "Etichetta"
                        ]
                    )

                    consiglio_budget = (
                        calcola_budget_massimo_consigliato(
                            giocatore,
                            priorita_acquisto,
                            budget_asta,
                            budget_rimanente,
                            numero_rosa
                        )
                    )

                    g1, g2, g3, g4, g5, g6, g7, g8 = (
                        st.columns(
                            [
                                1.06,
                                0.72,
                                0.68,
                                0.58,
                                0.72,
                                0.52,
                                1.12,
                                0.88
                            ]
                        )
                    )

                    with g1:

                        st.markdown(
                            f"""
                            <div class="asta-player-mobile-fix">
                                <div style="
                                    font-size:0.875rem;
                                    color:rgba(49,51,63,0.65);
                                    margin-bottom:0.15rem;
                                ">
                                    Giocatore
                                </div>
                                <div style="
                                    font-size:1.35rem;
                                    line-height:1.15;
                                    font-weight:700;
                                    color:{colore_nome_asta};
                                    white-space:normal;
                                    overflow-wrap:anywhere;
                                ">
                                    {html.escape(str(giocatore["Nome"]))}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    g2.metric(
                        "Squadra",
                        giocatore["Squadra"]
                    )

                    g3.metric(
                        "Ruolo",
                        giocatore["RM"]
                    )

                    sigle_specialista = (
                        sigle_specialista_giocatore(
                            giocatore["Nome"],
                            giocatore["Squadra"]
                        )
                    )

                    g4.metric(
                        "R / CP",
                        sigle_specialista
                        if sigle_specialista
                        else "—"
                    )

                    info_disp = info_disponibilita_giocatore(
                        giocatore["Nome"],
                        giocatore["Squadra"]
                    )

                    with g5:
                        st.caption("Disponibilità")
                        if info_disp["disponibile"]:
                            st.markdown(
                                '<div style="font-size:1.65rem;line-height:1.55;'
                                'font-weight:900;color:#16a34a;">✓</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            if st.button(
                                "❌",
                                key=f"btn_infortunio_{int(giocatore['Id'])}",
                                help="Clicca per vedere infortunio e tempi di recupero"
                            ):
                                mostra_dettaglio_infortunio(
                                    giocatore["Nome"],
                                    giocatore["Squadra"],
                                    info_disp["dettaglio"]
                                )

                    g6.metric(
                        "FVM",
                        giocatore["FVM"]
                    )

                    with g7:

                        dettaglio_priorita = (
                            f"Ruolo {priorita_acquisto['Ruolo']} · "
                            f"fascia {priorita_acquisto['Fascia candidato'].title()} · "
                            f"in rosa {priorita_acquisto['Copertura']} · "
                            f"rimasti {priorita_acquisto['Disponibili']}"
                        )

                        with st.container(
                            key=(
                                "priorita_click_"
                                f"{int(giocatore['Id'])}"
                            )
                        ):

                            st.markdown(
                                f"""
                                <div style="
                                    min-height:72px;
                                    border:2px solid {bordo_priorita};
                                    border-radius:10px;
                                    background:{bg_priorita};
                                    padding:9px 10px;
                                    display:flex;
                                    flex-direction:column;
                                    justify-content:center;
                                    box-sizing:border-box;
                                    cursor:pointer;
                                ">
                                    <div style="
                                        font-size:0.78rem;
                                        color:#475569;
                                        margin-bottom:4px;
                                        font-weight:600;
                                    ">
                                        Priorità acquisto
                                    </div>
                                    <div style="
                                        font-size:1.00rem;
                                        line-height:1.10;
                                        font-weight:800;
                                        color:{fg_priorita};
                                    ">
                                        {html.escape(
                                            priorita_acquisto[
                                                "Etichetta"
                                            ]
                                        )}
                                    </div>
                                    <div style="
                                        font-size:0.66rem;
                                        line-height:1.15;
                                        color:#64748b;
                                        margin-top:4px;
                                    ">
                                        {html.escape(
                                            dettaglio_priorita
                                        )}
                                    </div>
                                    <div style="
                                        font-size:0.62rem;
                                        line-height:1.1;
                                        color:#64748b;
                                        margin-top:5px;
                                        font-weight:600;
                                    ">
                                        Giocatori disponibili
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            if st.button(
                                "Giocatori disponibili",
                                key=(
                                    "btn_priorita_"
                                    f"{int(giocatore['Id'])}"
                                ),
                            ):

                                mostra_dettaglio_priorita_acquisto(
                                    giocatore,
                                    priorita_acquisto,
                                    df_completo
                                )

                    with g8:

                        st.markdown(
                            f"""
                            <div style="
                                min-height:72px;
                                border:2px solid #f5b51b;
                                border-radius:10px;
                                background:#fff8e6;
                                padding:9px 10px;
                                display:flex;
                                flex-direction:column;
                                justify-content:center;
                                box-sizing:border-box;
                            ">
                                <div style="
                                    font-size:0.76rem;
                                    color:#475569;
                                    margin-bottom:4px;
                                    font-weight:700;
                                ">
                                    Budget max consigliato
                                </div>
                                <div style="
                                    font-size:1.32rem;
                                    line-height:1.05;
                                    font-weight:900;
                                    color:#071a2f;
                                ">
                                    {consiglio_budget["Massimo"]} €
                                </div>
                                <div style="
                                    font-size:0.62rem;
                                    line-height:1.15;
                                    color:#64748b;
                                    margin-top:5px;
                                ">
                                    FVM + priorità + budget residuo
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    chiave_prezzo = (
                        "offerta_asta_"
                        f"{int(giocatore['Id'])}"
                    )

                    if chiave_prezzo not in st.session_state:
                        st.session_state[
                            chiave_prezzo
                        ] = 1.00

                    c1, c2, c3, c4, c5 = (
                        st.columns(
                            [
                                1.15,
                                1.20,
                                1.20,
                                0.85,
                                0.85
                            ],
                            vertical_alignment="bottom"
                        )
                    )

                    with c1:

                        prezzo = st.number_input(
                            "Offerta",
                            min_value=0.10,
                            max_value=5000.00,
                            step=0.10,
                            format="%.2f",
                            key=chiave_prezzo,
                            label_visibility="collapsed"
                        )

                    prezzo = round(
                        float(prezzo),
                        2
                    )

                    nuovo_valore = round(
                        valore_acquisti + prezzo,
                        2
                    )

                    nuova_spesa = (
                        calcola_spesa_effettiva(
                            nuovo_valore
                        )
                    )

                    incremento = round(
                        nuova_spesa
                        - spesa_effettiva,
                        2
                    )

                    valido, motivo = (
                        verifica_acquisto_regole(
                            df_rosa_globale,
                            giocatore["RM"]
                        )
                    )

                    with c2:

                        if st.button(
                            "✅ ACQUISTA",
                            use_container_width=True,
                            type="primary",
                            disabled=(not valido),
                            key=(
                                "btn_acquista_"
                                f"{int(giocatore['Id'])}"
                            )
                        ):

                            esegui_operazione(
                                int(giocatore["Id"]),
                                "ACQUISTO",
                                "MIO",
                                prezzo,
                                0
                            )

                            st.rerun()

                    with c3:

                        if st.button(
                            "🔴 VENDUTO AD AVVERSARIO",
                            use_container_width=True,
                            key=(
                                "btn_avversario_"
                                f"{int(giocatore['Id'])}"
                            )
                        ):

                            esegui_operazione(
                                int(giocatore["Id"]),
                                "VENDUTO AVVERSARIO",
                                "AVVERSARIO",
                                None,
                                0
                            )

                            st.rerun()

                    with c4:

                        st.metric(
                            "Impatto effettivo",
                            f"{formatta_crediti(incremento)} €"
                        )

                    with c5:

                        st.metric(
                            "Nuova spesa",
                            f"{formatta_crediti(nuova_spesa)} €"
                        )

                    if not valido:

                        st.error(
                            "⛔ " + motivo
                        )



    # ============================================================
    # VENDUTI AD AVVERSARI
    # ============================================================

    elif sezione == "VENDUTI AD AVVERSARI":

        st.subheader("🔴 Venduti ad avversari")

        if "messaggio_reset_avversari" in st.session_state:

            st.success(
                st.session_state.pop(
                    "messaggio_reset_avversari"
                )
            )

        avversari = (
            df_completo[
                df_completo["Stato"] == "AVVERSARIO"
            ]
            .copy()
            .sort_values("Nome")
            .reset_index(drop=True)
        )

        if avversari.empty:

            st.info("Nessun giocatore venduto agli avversari.")

        else:

            reset_col1, reset_col2 = st.columns(
                [
                    1.8,
                    4.2
                ]
            )

            with reset_col1:

                if st.button(
                    "↩️ RIPRISTINA TUTTI",
                    use_container_width=True,
                    key="btn_reset_tutti_avversari"
                ):

                    conferma_ripristina_tutti_avversari()

            with reset_col2:

                st.caption(
                    "Rende nuovamente disponibili tutti i giocatori "
                    "assegnati agli avversari."
                )

            st.caption(
                f"Giocatori venduti agli avversari: {len(avversari)}"
            )

            intestazione = st.columns(
                [4, 2, 2, 1, 0.8]
            )

            for col, titolo in zip(
                intestazione,
                ["Giocatore", "Squadra", "Ruolo", "FVM", "Ripristina"]
            ):
                col.markdown(f"**{titolo}**")

            for _, riga in avversari.iterrows():

                cols = st.columns(
                    [4, 2, 2, 1, 0.8],
                    vertical_alignment="center"
                )

                colore_nome = colore_fvm_mantra(
                    riga.get("RM", ""),
                    riga.get("FVM M")
                )

                cols[0].markdown(
                    f"<span style='color:{colore_nome};font-weight:800;'>"
                    f"{html.escape(str(riga['Nome']))}</span>",
                    unsafe_allow_html=True
                )
                cols[1].write(riga["Squadra"])
                cols[2].write(riga["RM"])
                cols[3].write(riga["FVM"])

                with cols[4]:
                    if st.button(
                        "↩️",
                        key=f"ripristina_{int(riga['Id'])}",
                        help="Rendi nuovamente disponibile",
                        use_container_width=True
                    ):
                        conferma_ripristino_avversario(
                            int(riga["Id"]),
                            riga["Nome"]
                        )


    # ============================================================
    # ROSA
    # ============================================================

    elif sezione == "ROSA":

        st.subheader(
            "👕 La mia rosa"
        )

        if "messaggio_reset_rosa" in st.session_state:
            st.success(
                st.session_state.pop(
                    "messaggio_reset_rosa"
                )
            )

        df_rosa = (
            df_rosa_globale.copy()
        )

        # MULTILEGA 0.4:
        # nessun accesso alle Formazioni Tipo se la rosa è vuota.
        # Se la rosa contiene giocatori, la mappa viene recuperata dalla
        # cache RAM e ricostruita solo al primo accesso/aggiornamento.
        mappa_titolarita_rosa = {}

        if not df_rosa.empty:

            mappa_titolarita_rosa = (
                costruisci_mappa_titolarita()
            )
            if st.button(
                "🗑️ ELIMINA TUTTA LA ROSA",
                key="btn_reset_tutta_rosa"
            ):
                conferma_elimina_tutta_rosa()

        if df_rosa.empty:

            empty_html = (
                '<div class="empty-card">'
                '<div class="empty-icon">👕</div>'
                '<div class="empty-title">'
                'La rosa è ancora vuota'
                '</div>'
                '<div class="empty-text">'
                'Vai nella sezione ASTA '
                'per acquistare i primi giocatori.'
                '</div>'
                '</div>'
            )

            st.markdown(
                empty_html,
                unsafe_allow_html=True
            )

        else:

            df_rosa[
                "Priorita"
            ] = (
                df_rosa["RM"]
                .apply(
                    priorita_ruolo
                )
            )

            df_rosa = (
                df_rosa
                .sort_values(
                    [
                        "Priorita",
                        "Nome"
                    ]
                )
                .reset_index(
                    drop=True
                )
            )

            # ----------------------------------------------------
            # VISTA MOBILE - tabella semplice
            # ----------------------------------------------------
            with st.container(
                key="rosa_mobile_view"
            ):

                # Header compatto mobile
                h1, h2, h3, h4, h5, h6 = st.columns(
                    [2.0, 0.8, 1.4, 0.7, 0.9, 0.5]
                )

                h1.markdown("**NOME GIOCATORE**")
                h2.markdown("**RUOLO**")
                h3.markdown("**TITOLARITÀ**")
                h4.markdown("**R/CP**")
                h5.markdown("**PREZZO**")
                h6.markdown("**OK**")

                for _, giocatore in df_rosa.iterrows():

                    giocatore_id = int(
                        giocatore["Id"]
                    )

                    prezzo_attuale = float(
                        giocatore["Prezzo"]
                        or 0
                    )

                    chiave_prezzo = (
                        f"prezzo_rosa_mobile_{giocatore_id}"
                    )

                    if chiave_prezzo not in st.session_state:

                        st.session_state[
                            chiave_prezzo
                        ] = prezzo_attuale

                    r1, r2, r3, r4, r5, r6 = st.columns(
                        [2.0, 0.8, 1.4, 0.7, 0.9, 0.5],
                        vertical_alignment="center"
                    )

                    colore_nome = (
                        colore_fvm_mantra(
                            giocatore.get(
                                "RM",
                                ""
                            ),
                            giocatore.get(
                                "FVM M"
                            )
                        )
                    )

                    r1.markdown(
                        f"<span style='color:{colore_nome};"
                        f"font-weight:800;'>"
                        f"{html.escape(str(giocatore['Nome']))}"
                        f"</span>",
                        unsafe_allow_html=True
                    )

                    r2.write(
                        giocatore["RM"]
                    )

                    r3.markdown(
                        html_titolarita_rosa(
                            giocatore["Nome"],
                            giocatore["Squadra"],
                            mappa_titolarita_rosa
                        ),
                        unsafe_allow_html=True
                    )

                    r4.write(
                        sigle_specialista_giocatore(
                            giocatore["Nome"],
                            giocatore["Squadra"]
                        )
                        or "—"
                    )

                    with r5:

                        nuovo_prezzo = st.number_input(
                            "Prezzo",
                            min_value=0.0,
                            max_value=5000.0,
                            step=0.10,
                            format="%.2f",
                            key=chiave_prezzo,
                            label_visibility="collapsed"
                        )

                    with r6:

                        modificato = (
                            round(
                                float(
                                    nuovo_prezzo
                                ),
                                2
                            )
                            != round(
                                prezzo_attuale,
                                2
                            )
                        )

                        if st.button(
                            "✓",
                            key=f"salva_prezzo_mobile_{giocatore_id}",
                            help="Conferma modifica prezzo",
                            disabled=not modificato,
                            use_container_width=True
                        ):

                            conferma_modifica_prezzo(
                                giocatore_id,
                                giocatore["Nome"],
                                prezzo_attuale,
                                nuovo_prezzo
                            )


            # ----------------------------------------------------
            # VISTA DESKTOP - invariata
            # ----------------------------------------------------
            with st.container(
                key="rosa_desktop_view"
            ):

                intestazione = (
                    st.columns(
                        [
                            4,
                            2,
                            2,
                            1.8,
                            1.2,
                            1.2,
                            1.9,
                            0.7,
                            0.7
                        ]
                    )
                )

                titoli = [
                    "Nome",
                    "Squadra",
                    "Ruolo",
                    "Titolarità",
                    "R / CP",
                    "FVM",
                    "Prezzo acquisto",
                    "🗑️",
                    "🔓"
                ]

                for col, titolo in zip(
                    intestazione,
                    titoli
                ):
                    col.markdown(
                        f"**{titolo}**"
                    )

                for _, giocatore in df_rosa.iterrows():

                    cols = (
                        st.columns(
                            [
                                4,
                                2,
                                2,
                                1.8,
                                1.2,
                                1.2,
                                1.9,
                                0.7,
                                0.7
                            ],
                            vertical_alignment="center"
                        )
                    )

                    cols[0].write(
                        giocatore["Nome"]
                    )
                    cols[1].write(
                        giocatore["Squadra"]
                    )
                    cols[2].write(
                        giocatore["RM"]
                    )

                    cols[3].markdown(
                        html_titolarita_rosa(
                            giocatore["Nome"],
                            giocatore["Squadra"],
                            mappa_titolarita_rosa
                        ),
                        unsafe_allow_html=True
                    )

                    cols[4].write(
                        sigle_specialista_giocatore(
                            giocatore["Nome"],
                            giocatore["Squadra"]
                        )
                        or "—"
                    )

                    cols[5].write(
                        giocatore["FVM"]
                    )
                    giocatore_id = int(
                        giocatore["Id"]
                    )

                    prezzo_attuale = float(
                        giocatore["Prezzo"]
                        or 0
                    )

                    chiave_prezzo = (
                        f"prezzo_rosa_desktop_{giocatore_id}"
                    )

                    if chiave_prezzo not in st.session_state:

                        st.session_state[
                            chiave_prezzo
                        ] = prezzo_attuale

                    with cols[6]:

                        prezzo_col1, prezzo_col2 = st.columns(
                            [3.2, 0.8],
                            vertical_alignment="center"
                        )

                        with prezzo_col1:

                            nuovo_prezzo = st.number_input(
                                "Prezzo acquisto",
                                min_value=0.0,
                                max_value=5000.0,
                                step=0.10,
                                format="%.2f",
                                key=chiave_prezzo,
                                label_visibility="collapsed"
                            )

                        with prezzo_col2:

                            modificato = (
                                round(
                                    float(
                                        nuovo_prezzo
                                    ),
                                    2
                                )
                                != round(
                                    prezzo_attuale,
                                    2
                                )
                            )

                            if st.button(
                                "✓",
                                key=f"salva_prezzo_{giocatore_id}",
                                help="Conferma modifica prezzo",
                                disabled=not modificato,
                                use_container_width=True
                            ):

                                conferma_modifica_prezzo(
                                    giocatore_id,
                                    giocatore["Nome"],
                                    prezzo_attuale,
                                    nuovo_prezzo
                                )

                    with cols[7]:
                        if st.button(
                            "🗑️",
                            key=(
                                "elimina_"
                                f"{int(giocatore['Id'])}"
                            ),
                            help="Annulla acquisto"
                        ):
                            conferma_annullamento(
                                int(
                                    giocatore["Id"]
                                ),
                                giocatore["Nome"]
                            )

                    with cols[8]:
                        if st.button(
                            "🔓",
                            key=(
                                "svincola_"
                                f"{int(giocatore['Id'])}"
                            ),
                            help="Svincola giocatore"
                        ):
                            conferma_svincolo(
                                int(
                                    giocatore["Id"]
                                ),
                                giocatore["Nome"],
                                giocatore["Prezzo"]
                            )


    # ============================================================
    # PROBABILI FORMAZIONI
    # ============================================================

    elif sezione == "FORMAZIONI TIPO":

        st.subheader(
            "⚽ Formazioni tipo Serie A 2026/27"
        )

        dati = (
            carica_probabili_web()
        )

        a, b = st.columns(
            [
                1.35,
                4.65
            ],
            vertical_alignment="center"
        )

        with a:

            if st.button(
                "🌐 AGGIORNA DAL WEB",
                type="primary",
                use_container_width=True,
                key="pf_update"
            ):

                try:

                    with st.spinner(
                        "Aggiornamento formazioni tipo..."
                    ):

                        dati = (
                            aggiorna_probabili_web()
                        )

                        invalida_cache_titolarita()

                        st.session_state[
                            "_formazioni_tipo_fast_cache"
                        ] = dati

                    st.success(
                        f"Aggiornate "
                        f"{len(dati.get('squadre', []))} squadre."
                    )

                    st.rerun()

                except Exception as errore:

                    st.error(
                        "Aggiornamento non riuscito. "
                        "Gli eventuali dati già salvati "
                        "restano disponibili."
                    )

                    st.caption(
                        str(
                            errore
                        )
                    )

        with b:

            if dati:

                testo = (
                    "Ultimo download: "
                    f"**{dati.get('scaricato_il', '—')}**"
                )

                if dati.get(
                    "aggiornamento_fonte"
                ):

                    testo += (
                        " · Fonte: "
                        f"**{dati.get('aggiornamento_fonte')}**"
                    )

                st.markdown(
                    testo
                )

            else:

                st.info(
                    "Nessuna formazione tipo ancora salvata. "
                    "Premi «AGGIORNA DAL WEB» per effettuare "
                    "il primo aggiornamento dalla nuova fonte."
                )

        st.caption(
            "Fonte: Fantacalcio.it — probabili formazioni stagionali per l’asta. "
            "I dati sono stagionali, non riferiti alla singola giornata. "
            "Il consenso delle guide viene trasformato in "
            "TITOLARE / BALLOTTAGGIO / RISERVA."
        )

        legenda = (
            '<div style="display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 12px 0;">'
            '<span style="background:#dcfce7;color:#15803d;border-radius:7px;padding:5px 9px;font-weight:900;">'
            '● TITOLARE CONSOLIDATO</span>'
            '<span style="background:#dbeafe;color:#1d4ed8;border-radius:7px;padding:5px 9px;font-weight:900;">'
            '● BALLOTTAGGIO</span>'
            '</div>'
        )

        st.markdown(
            legenda,
            unsafe_allow_html=True
        )

        if dati:

            squadre = (
                dati.get(
                    "squadre",
                    []
                )
            )

            nomi = [
                squadra.get(
                    "squadra",
                    ""
                )
                for squadra in squadre
            ]

            filtro = st.selectbox(
                "Vai a una squadra",
                [
                    "TUTTE"
                ]
                + nomi,
                key="pf_filter"
            )

            visibili = (
                squadre
                if filtro == "TUTTE"
                else [
                    squadra
                    for squadra in squadre
                    if squadra.get(
                        "squadra"
                    ) == filtro
                ]
            )

            for indice in range(
                0,
                len(
                    visibili
                ),
                2
            ):

                colonne = (
                    st.columns(
                        2
                    )
                )

                for offset in range(
                    2
                ):

                    posizione = (
                        indice
                        + offset
                    )

                    if posizione < len(
                        visibili
                    ):

                        with colonne[
                            offset
                        ]:

                            mostra_probabile(
                                visibili[
                                    posizione
                                ]
                            )


    # ============================================================
    # MODULI
    # ============================================================

    elif sezione == "MODULI":

        df_rosa = (
            df_rosa_globale.copy()
        )

        classifica_moduli_corrente = (
            classifica_moduli(
                df_rosa
            )
        )

        modulo_consigliato = (
            classifica_moduli_corrente[0][
                "Modulo"
            ]
            if classifica_moduli_corrente
            else list(
                MODULI.keys()
            )[0]
        )

        if "modulo_attivo" not in st.session_state:
            st.session_state.modulo_attivo = (
                modulo_consigliato
            )

        if classifica_moduli_corrente:

            migliore = (
                classifica_moduli_corrente[0]
            )

            st.success(
                f"⭐ **Modulo consigliato: "
                f"{migliore['Modulo']}** "
                f"— punteggio strategico "
                f"**{migliore['Punteggio']}/100** "
                f"— copertura media "
                f"**{migliore['Copertura media']}%** "
                f"— slot scoperti "
                f"**{migliore['Scoperti']}** "
                f"— slot deboli "
                f"**{migliore['Deboli']}**"
                + (
                    f" ({migliore['Ruoli deboli']})"
                    if migliore[
                        "Ruoli deboli"
                    ]
                    else ""
                )
            )

        st.markdown(
            '<div class="module-button-note">'
            'Seleziona il modulo da visualizzare'
            '</div>',
            unsafe_allow_html=True
        )

        lista_moduli = list(
            MODULI.keys()
        )

        # --------------------------------------------------------
        # TASTI MODULO
        # --------------------------------------------------------

        for inizio in range(
            0,
            len(lista_moduli),
            5
        ):

            gruppo_moduli = lista_moduli[
                inizio:
                inizio + 5
            ]

            colonne = st.columns(
                len(gruppo_moduli),
                gap="small"
            )

            for colonna, nome_modulo in zip(
                colonne,
                gruppo_moduli
            ):

                with colonna:

                    etichetta_modulo = (
                        f"⭐ {nome_modulo}"
                        if nome_modulo
                        == modulo_consigliato
                        else nome_modulo
                    )

                    if st.button(
                        etichetta_modulo,
                        use_container_width=True,
                        type=(
                            "primary"
                            if st.session_state.modulo_attivo
                            == nome_modulo
                            else "secondary"
                        ),
                        key=(
                            "btn_modulo_"
                            + nome_modulo
                            .replace("-", "_")
                        )
                    ):

                        st.session_state.modulo_attivo = (
                            nome_modulo
                        )

                        st.rerun()

        modulo_scelto = (
            st.session_state.modulo_attivo
        )

        if df_rosa.empty:

            empty_html = (
                '<div class="empty-card">'
                '<div class="empty-icon">⚽</div>'
                '<div class="empty-title">'
                'Nessun giocatore in rosa'
                '</div>'
                '<div class="empty-text">'
                'Acquista almeno un giocatore '
                'dalla sezione ASTA.<br>'
                'Il modulo selezionato verrà compilato '
                'automaticamente.'
                '</div>'
                '</div>'
            )

            st.markdown(
                empty_html,
                unsafe_allow_html=True
            )

        else:

            righe_modulo = (
                MODULI[
                    modulo_scelto
                ]
            )

            ruoli_al_100, totale_posizioni, percentuale_media = (
                calcola_copertura_modulo(
                    df_rosa,
                    modulo_scelto
                )
            )

            percentuale = round(
                percentuale_media
            )

            analisi_corrente = (
                analizza_modulo(
                    df_rosa,
                    modulo_scelto
                )
            )

            html_campo = (
                '<div class="module-card">'
                '<div class="module-card-title">'
                f'{html.escape(modulo_scelto)}'
                '</div>'
                '<div class="module-card-summary">'
                f'Punteggio strategico '
                f'{analisi_corrente["Punteggio"]}/100'
                f' · copertura media {percentuale}%'
                f' · ruoli con almeno 4 giocatori: '
                f'{ruoli_al_100}/{totale_posizioni}'
                f' · slot scoperti: '
                f'{analisi_corrente["Scoperti"]}'
                f' · slot deboli: '
                f'{analisi_corrente["Deboli"]}'
                + (
                    f' ({html.escape(analisi_corrente["Ruoli deboli"])})'
                    if analisi_corrente[
                        "Ruoli deboli"
                    ]
                    else ""
                )
                + '</div>'
                '<div class="pitch">'
                '<div class="pitch-half-line"></div>'
            )

            # Attacco in alto, portiere in basso.
            # Visualizzazione ridotta ai soli ruoli Mantra
            # e ai nomi dei giocatori compatibili.
            for _, posizioni in reversed(
                righe_modulo
            ):

                html_campo += (
                    '<div class="pitch-line">'
                )

                for _, ruolo_slot in (
                    posizioni
                ):

                    possibili = (
                        giocatori_compatibili(
                            df_rosa,
                            ruolo_slot
                        )
                    )

                    numero_ruolo, percentuale_ruolo = (
                        percentuale_copertura_ruolo(
                            df_rosa,
                            ruolo_slot
                        )
                    )

                    percentuale_ruolo_arrotondata = round(
                        percentuale_ruolo
                    )

                    colore_copertura = (
                        colore_percentuale_copertura(
                            percentuale_ruolo
                        )
                    )

                    html_campo += (
                        '<div class="player-slot">'
                        '<div class="slot-code">'
                        f'<span>{html.escape(str(ruolo_slot))}</span>'
                        '<span class="slot-coverage" '
                        f'style="color:{colore_copertura};">'
                        f'{percentuale_ruolo_arrotondata}%'
                        '</span>'
                        '</div>'
                    )

                    if possibili.empty:

                        html_campo += (
                            '<span class="slot-empty">'
                            '—'
                            '</span>'
                        )

                    else:

                        for _, giocatore in (
                            possibili.iterrows()
                        ):

                            nome = html.escape(
                                str(
                                    giocatore[
                                        "Nome"
                                    ]
                                )
                            )

                            ruoli_giocatore_testo = html.escape(
                                str(
                                    giocatore.get(
                                        "RM",
                                        ""
                                    )
                                ).strip()
                            )

                            colore = (
                                colore_fvm_mantra(
                                    giocatore.get(
                                        "RM",
                                        ""
                                    ),
                                    giocatore.get(
                                        "FVM M"
                                    )
                                )
                            )

                            nome_con_ruoli = (
                                f"{nome} "
                                f"({ruoli_giocatore_testo})"
                                if ruoli_giocatore_testo
                                else nome
                            )

                            html_campo += (
                                '<div class="player-name" '
                                f'style="color:{colore};">'
                                f'{nome_con_ruoli}'
                                '</div>'
                            )

                    html_campo += (
                        '</div>'
                    )

                html_campo += (
                    '</div>'
                )

            html_campo += (
                '</div>'
                '</div>'
            )

            st.markdown(
                html_campo,
                unsafe_allow_html=True
            )


    # ============================================================
    # FOOTER
    # ============================================================

    footer_html = (
        '<div class="fanta-footer">'
        'ⓘ &nbsp;'
        '<b>FANTAELEGANZA 26/27</b>'
        ' — Il tuo assistente per un\'asta perfetta.'
        '</div>'
    )

    st.markdown(
        footer_html,
        unsafe_allow_html=True
    )

render_navigazione_e_pagina()
