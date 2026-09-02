# FANTAELEGANZA MULTIMODULO V3 - FILE VERIFICATO
import html
import io
import json
import math
import os
import sqlite3
import re
import urllib.request
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
    initial_sidebar_state="collapsed"
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
</style>
""", unsafe_allow_html=True)

SOGLIA_BASE = 500.00
MAX_GIOCATORI = 30
MIN_PORTIERI = 2
MAX_UNDO = 10

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fantacalcio.db"
URL_PROBABILI_FORMAZIONI = "https://www.goal.com/it/liste/fantacalcio-formazioni-titolari-serie-a-2026-2027-tutte-le-squadre-tipo/blt5527c89487e5b7d3"

MAX_SNAPSHOT = 30


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
    Etichetta qualitativa dell'Indice Qualità Rosa.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        return "Rosa debole"

    if valore >= 95:
        return "Rosa eccezionale"

    if valore >= 85:
        return "Rosa eccellente"

    if valore >= 75:
        return "Rosa molto forte"

    if valore >= 60:
        return "Rosa buona"

    if valore >= 40:
        return "Rosa discreta"

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
    Colore sintetico dell'indicatore IQR.
    Scala richiesta: NERO -> ROSSO -> BLU -> VERDE.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        valore = 0.0

    if valore >= 85:
        return "#16a34a"

    if valore >= 60:
        return "#2563eb"

    if valore >= 40:
        return "#dc2626"

    return "#111827"


def genera_html_gauge_iqr(
    valore
):
    """
    Crea il tachimetro semicircolare IQR in puro SVG/HTML.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        valore = 0.0

    valore = max(
        0.0,
        min(
            100.0,
            valore
        )
    )

    cx = 120.0
    cy = 108.0
    r = 86.0

    segmenti = [
        (0.0, 40.0, "#111827"),
        (40.0, 60.0, "#dc2626"),
        (60.0, 85.0, "#2563eb"),
        (85.0, 100.0, "#16a34a")
    ]

    polilinee = []

    for inizio, fine, colore in segmenti:

        punti = []

        passi = 18

        for indice in range(
            passi + 1
        ):

            quota = (
                inizio
                + (
                    fine
                    - inizio
                )
                * indice
                / passi
            )

            angolo = (
                math.pi
                - quota
                / 100.0
                * math.pi
            )

            x = (
                cx
                + r
                * math.cos(
                    angolo
                )
            )

            y = (
                cy
                - r
                * math.sin(
                    angolo
                )
            )

            punti.append(
                f"{x:.1f},{y:.1f}"
            )

        polilinee.append(
            (
                f'<polyline points="{" ".join(punti)}" '
                f'fill="none" stroke="{colore}" '
                f'stroke-width="18" stroke-linecap="butt"/>'
            )
        )

    angolo_indicatore = (
        math.pi
        - valore
        / 100.0
        * math.pi
    )

    lunghezza = 66.0

    x2 = (
        cx
        + lunghezza
        * math.cos(
            angolo_indicatore
        )
    )

    y2 = (
        cy
        - lunghezza
        * math.sin(
            angolo_indicatore
        )
    )

    descrizione = html.escape(
        descrizione_iqr(
            valore
        )
    )

    colore_descrizione = (
        colore_iqr(
            valore
        )
    )

    return (
        '<div class="iqr-gauge-card">'
        '<div class="iqr-gauge-title">⭐ IQR</div>'
        '<svg viewBox="0 0 240 128" class="iqr-gauge-svg" '
        'role="img" aria-label="Indice Qualità Rosa">'
        + "".join(
            polilinee
        )
        + (
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            'stroke="#0f172a" stroke-width="5" '
            'stroke-linecap="round"/>'
        )
        + (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" '
            'fill="#0f172a"/>'
        )
        + '</svg>'
        + (
            f'<div class="iqr-gauge-value">{valore:.1f}%</div>'
        )
        + (
            f'<div class="iqr-gauge-description" '
            f'style="background:{colore_descrizione};">'
            f'{descrizione}</div>'
        )
        + '<div class="iqr-gauge-hint">Tocca / clicca per i dettagli</div>'
        + '</div>'
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


def leggi_config_generica(chiave, default=""):
    conn=get_connection(); cur=conn.cursor()
    try:
        cur.execute("SELECT valore FROM configurazione_app WHERE chiave = ?",(chiave,))
        r=cur.fetchone()
    finally: chiudi_connessione(conn)
    return r[0] if r else default

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


def _goal_split_names(text):
    return [
        re.sub(r"\s+", " ", x).strip(" .")
        for x in str(text).split(",")
        if re.sub(r"\s+", " ", x).strip(" .")
    ]


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


def aggiorna_probabili_web():
    """
    Source: GOAL Italia, seasonal Serie A formations.

    Reliability rules:
    - reads GOAL's explicit FORMATION TYPE, not inferred percentages;
    - keeps semicolon-separated tactical lines exactly as published;
    - accepts a team only when the source supplies exactly 11 starters;
    - 'Altri possibili titolari' are stored as BALLOTTAGGIO;
    - no player is invented and no reserve is inferred.
    """
    req = urllib.request.Request(
        URL_PROBABILI_FORMAZIONI,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/152 Safari/537.36"
            ),
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.7"
        }
    )

    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read().decode("utf-8", "ignore")

    parser = GoalTextParser()
    parser.feed(raw)

    # Collapse duplicate consecutive fragments.
    items = []
    for x in parser.items:
        if not items or items[-1] != x:
            items.append(x)

    teams = []
    i = 0
    while i < len(items):
        head = re.match(
            r"^PROBABILE FORMAZIONE\s+(.+)$",
            items[i],
            flags=re.IGNORECASE
        )
        if not head:
            i += 1
            continue

        team = head.group(1).strip().title()
        j = i + 1
        formation = None
        alternatives = []
        coach = ""

        while j < len(items):
            if re.match(r"^PROBABILE FORMAZIONE\s+", items[j], re.I):
                break

            if items[j].upper().startswith("FORMAZIONE TIPO"):
                cm = re.search(r"Allenatore\s*:\s*([^)]+)", items[j], re.I)
                if cm:
                    coach = cm.group(1).strip()

            parsed = _goal_parse_formation_line(items[j])
            if parsed and formation is None:
                formation = parsed

            if items[j].lower().startswith("altri possibili titolari"):
                tail = items[j].split(":", 1)[1] if ":" in items[j] else ""
                alternatives = _goal_split_names(tail)

            j += 1

        if formation:
            teams.append({
                "squadra": team,
                "allenatore": coach,
                "modulo": formation["modulo"],
                "linee_fonte": formation["linee_fonte"],
                "formazione": [
                    {"nome": n, "status": "TITOLARE"}
                    for n in formation["titolari"]
                ],
                "alternative": [
                    {"nome": n, "status": "BALLOTTAGGIO"}
                    for n in alternatives
                ]
            })

        i = max(j, i + 1)

    # Deduplicate teams.
    unique = {}
    for s in teams:
        unique[s["squadra"].upper()] = s
    teams = list(unique.values())

    # Strict: all 20 teams and 11 starters each.
    invalid = [
        s["squadra"] for s in teams
        if len(s.get("formazione", [])) != 11
    ]
    if len(teams) != 20 or invalid:
        raise RuntimeError(
            "Aggiornamento annullato: GOAL ha restituito "
            f"{len(teams)} squadre valide su 20"
            + (f"; formazioni non valide: {', '.join(invalid)}" if invalid else "")
            + ". La cache precedente non è stata modificata."
        )

    dati = {
        "versione_dati": 3,
        "fonte": URL_PROBABILI_FORMAZIONI,
        "scaricato_il": datetime.now(
            ZoneInfo("Europe/Rome")
        ).strftime("%d/%m/%Y %H:%M"),
        "squadre": teams
    }

    salva_config_generica(
        "formazioni_tipo_goal_v1",
        json.dumps(dati, ensure_ascii=False)
    )
    return dati


def carica_probabili_web():
    raw = leggi_config_generica("formazioni_tipo_goal_v1", "")
    if not raw:
        return None
    try:
        dati = json.loads(raw)
        if isinstance(dati, dict) and dati.get("versione_dati") == 3:
            # Refuse malformed cache too.
            squadre = dati.get("squadre", [])
            if len(squadre) == 20 and all(
                len(s.get("formazione", [])) == 11 for s in squadre
            ):
                return dati
    except Exception:
        pass
    return None


def _goal_visual_lines(squadra):
    """
    GOAL line order is goalkeeper -> defence -> midfield/... -> attack.
    The pitch is rendered attack -> ... -> goalkeeper.
    """
    linee = squadra.get("linee_fonte", []) or []
    return list(reversed(linee))


def mostra_probabile(squadra):
    linee = _goal_visual_lines(squadra)
    rows = ""

    # Only GOAL's exact starting XI goes on the pitch.
    for linea in linee:
        players = ""
        for nome_raw in linea:
            nome = html.escape(str(nome_raw))
            players += (
                '<div class="pf-player pf-player-goal">'
                '<div class="pf-name" style="color:#16a34a;">'
                + nome +
                '</div>'
                '</div>'
            )
        rows += '<div class="pf-line">' + players + '</div>'

    titolo = html.escape(str(squadra.get("squadra", "")))
    modulo = html.escape(str(squadra.get("modulo", "")))

    st.markdown(
        '<div class="pf-team">'
        + titolo
        + '<span>'
        + modulo
        + '</span></div>'
        + '<div class="pf-pitch">'
        + rows
        + '</div>',
        unsafe_allow_html=True
    )

    # GOAL does not identify which exact starter each "possible starter"
    # challenges. We therefore do not invent pairings or tactical positions.
    alternatives = squadra.get("alternative", []) or []
    if alternatives:
        alt_html = "".join(
            '<span class="pf-alt-chip">'
            + html.escape(str(g.get("nome", "")))
            + '</span>'
            for g in alternatives
        )
        st.markdown(
            '<div class="pf-alt-box">'
            '<span class="pf-alt-title">ALTRI POSSIBILI TITOLARI</span>'
            + alt_html +
            '</div>',
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
def elenco_snapshot():

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

def get_connection():

    if USA_DATABASE_CLOUD:

        try:

            import libsql

        except ImportError as errore:

            raise RuntimeError(
                "La modalità Cloud richiede il pacchetto libsql. "
                "Installa le dipendenze da requirements.txt."
            ) from errore

        # Riutilizza la stessa connessione durante tutta la sessione.
        # Evita handshake/connessioni remote ripetute a ogni operazione.
        chiave = "_turso_connessione"

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
def inizializza_database():

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

        return (
            st.session_state[
                chiave
            ].copy()
        )

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
        "_costi_svincoli_sessione"
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
    width="large"
)
def mostra_dettaglio_iqr(
    valore_iqr,
    df_rosa
):

    st.markdown(
        genera_html_gauge_iqr(
            valore_iqr
        ),
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

        st.dataframe(
            dettaglio,
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        "### Scala qualitativa"
    )

    st.markdown(
        """
- **0–39%** — Rosa debole
- **40–59%** — Rosa discreta
- **60–74%** — Rosa buona
- **75–84%** — Rosa molto forte
- **85–94%** — Rosa eccellente
- **95–100%** — Rosa eccezionale
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
        elenco_snapshot()
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

inizializza_database()

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

df_completo = (
    carica_tutti_giocatori()
)

df_rosa_globale = (
    df_completo[
        df_completo["Stato"]
        == "MIO"
    ]
    .copy()
)

valore_attivi = (
    calcola_valore_acquisti_attivi()
)

costi_svincoli = (
    calcola_costi_svincoli()
)

valore_acquisti = round(
    valore_attivi
    + costi_svincoli,
    2
)

spesa_effettiva = (
    calcola_spesa_effettiva(
        valore_acquisti
    )
)

oltre_soglia = round(
    max(
        0,
        valore_acquisti
        - SOGLIA_BASE
    ),
    2
)

numero_rosa = len(
    df_rosa_globale
)

numero_portieri = (
    conta_portieri(
        df_rosa_globale
    )
)

slot_liberi = max(
    0,
    MAX_GIOCATORI
    - numero_rosa
)

budget_asta = float(
    st.session_state.get(
        "budget_asta_corrente",
        SOGLIA_BASE
    )
)

budget_rimanente = round(
    budget_asta
    - spesa_effettiva,
    2
)


iqr = (
    calcola_iqr(
        df_rosa_globale,
        df_completo,
        MAX_GIOCATORI
    )
)


# ============================================================
# HEADER COMPATTO
# ============================================================

head_left, head_refresh, head_snapshot, head_backup, head_rules, head_theme = (
    st.columns(
        [
            5.0,
            0.9,
            1.0,
            0.9,
            0.8,
            1.0
        ],
        vertical_alignment="center"
    )
)

with head_left:

    # IMPORTANTE:
    # stringa HTML senza indentazione iniziale,
    # così Streamlit non la mostra come codice.

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


with head_refresh:

    if st.button(
        "🔄 Aggiorna",
        use_container_width=True,
        key="btn_aggiorna_app"
    ):

        invalida_cache_dati()
        st.rerun()


with head_snapshot:

    if st.button(
        "📸 Snapshot",
        use_container_width=True,
        key="btn_snapshot"
    ):

        gestisci_snapshot()


with head_backup:

    if USA_DATABASE_CLOUD:

        if st.button(
            "☁ Backup",
            use_container_width=True,
            key="btn_backup_cloud"
        ):

            gestisci_backup_cloud()

    elif DB_PATH.exists():

        with open(
            DB_PATH,
            "rb"
        ) as file_db:

            st.download_button(
                "☁ Backup",
                data=file_db.read(),
                file_name=(
                    "fantaeleganza_backup.db"
                ),
                mime=(
                    "application/octet-stream"
                ),
                use_container_width=True
            )


with head_rules:

    if st.button(
        "❔ Regole",
        use_container_width=True,
        key="btn_regole"
    ):

        mostra_regole()


with head_theme:

    nuovo_dark = st.toggle(
        "🌙 Scuro",
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
    """
    <style>

    div[class*="st-key-iqr_card_clickable"] {
        position: relative !important;
        min-height: 154px !important;
        border: 1px solid #dbe2ea;
        border-radius: 12px;
        background: #ffffff;
        padding: 6px 7px 7px 7px;
        overflow: hidden;
    }

    div[class*="st-key-iqr_card_clickable"]:hover {
        border-color: #2563eb;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.10);
    }

    div[class*="st-key-iqr_card_clickable"] .stButton {
        position: absolute !important;
        inset: 0 !important;
        z-index: 20 !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
    }

    div[class*="st-key-iqr_card_clickable"] .stButton > button {
        width: 100% !important;
        height: 100% !important;
        min-height: 100% !important;
        opacity: 0 !important;
        cursor: pointer !important;
        padding: 0 !important;
        border: none !important;
    }

    .iqr-gauge-card {
        text-align: center;
        width: 100%;
        pointer-events: none;
    }

    .iqr-gauge-title {
        font-size: 12px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: -7px;
    }

    .iqr-gauge-svg {
        width: 100%;
        max-width: 150px;
        height: 76px;
        display: block;
        margin: 0 auto -2px auto;
    }

    .iqr-gauge-value {
        font-size: 20px;
        line-height: 1;
        font-weight: 800;
        color: #0f172a;
        margin-top: -2px;
    }

    .iqr-gauge-description {
        display: inline-block;
        color: #ffffff;
        font-size: 9px;
        font-weight: 800;
        line-height: 1.1;
        padding: 4px 7px;
        border-radius: 6px;
        margin-top: 5px;
    }

    .iqr-gauge-hint {
        font-size: 7px;
        color: #64748b;
        margin-top: 4px;
    }

    @media (max-width: 850px) {

        div[class*="st-key-iqr_card_clickable"] {
            min-height: 142px !important;
            padding: 5px !important;
        }

        .iqr-gauge-svg {
            max-width: 135px;
            height: 68px;
        }

        .iqr-gauge-value {
            font-size: 18px;
        }

        .iqr-gauge-description {
            font-size: 8px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RIEPILOGO COMPATTO
# ============================================================

m1, m2, m3, m4, m5, m6, m7, m8 = (
    st.columns(8)
)

m1.metric(
    "💳 Soglia base",
    f"{formatta_crediti(SOGLIA_BASE)} €"
)

with m2:

    st.number_input(
        "💰 Budget",
        min_value=0.0,
        step=10.0,
        format="%.2f",
        key="budget_asta_input",
        on_change=aggiorna_budget_da_widget,
        help=(
            "Budget totale che hai deciso di destinare all'asta. "
            "Il valore viene salvato nel database Cloud e resta "
            "disponibile anche da altri dispositivi."
        )
    )

m3.metric(
    "💵 Budget rimanente",
    f"{formatta_crediti(budget_rimanente)} €",
    delta=(
        "Disponibile"
        if budget_rimanente >= 0
        else "Budget superato"
    ),
    delta_color=(
        "off"
        if budget_rimanente >= 0
        else "inverse"
    ),
    help=(
        "Budget impostato meno Spesa effettiva. "
        "La Spesa effettiva include la maggiorazione prevista "
        "oltre la soglia base."
    )
)

m4.metric(
    "🪙 Spesa effettiva",
    f"{formatta_crediti(spesa_effettiva)} €"
)

m5.metric(
    "⚡ Oltre soglia",
    f"{formatta_crediti(oltre_soglia)} €"
)

m6.metric(
    "👥 Giocatori",
    f"{numero_rosa}/{MAX_GIOCATORI}"
)

m7.metric(
    "🧤 Portieri",
    f"{numero_portieri}/{MIN_PORTIERI}"
)

with m8:

    with st.container(
        key="iqr_card_clickable"
    ):

        st.markdown(
            genera_html_gauge_iqr(
                iqr
            ),
            unsafe_allow_html=True
        )

        if st.button(
            "Apri dettaglio IQR",
            key="btn_apri_dettaglio_iqr",
            help="Apri il dettaglio dell'Indice Qualità Rosa"
        ):

            mostra_dettaglio_iqr(
                iqr,
                df_rosa_globale
            )


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
</style>
""", unsafe_allow_html=True)

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

st.markdown(
    '<div class="nav-title">Navigazione</div>',
    unsafe_allow_html=True
)

nav_cols = st.columns(7)

for col, (
    icona,
    pagina
) in zip(
    nav_cols,
    PAGINE
):

    with col:

        if st.button(
            f"{icona}  {pagina}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.pagina
                == pagina
                else "secondary"
            ),
            key=f"nav_{pagina}"
        ):

            st.session_state.pagina = (
                pagina
            )

            st.rerun()

sezione = (
    st.session_state.pagina
)


# ============================================================
# TOOLBAR UNDO COMPATTA
# ============================================================

operazioni_undo = (
    carica_ultime_operazioni()
)

undo1, undo2 = st.columns(
    [
        1.7,
        7
    ]
)

with undo1:

    if st.button(
        "↶ ANNULLA ULTIMA OPERAZIONE",
        use_container_width=True,
        disabled=(
            operazioni_undo.empty
        ),
        key="btn_undo_generale"
    ):

        conferma_undo()


with undo2:

    if not operazioni_undo.empty:

        ultima = (
            operazioni_undo.iloc[0]
        )

        testo_ultima = (
            f'<div class="operation-info">'
            f'Ultima operazione annullabile:&nbsp;'
            f'<b>'
            f'{html.escape(str(ultima["Operazione"]))}'
            f' — '
            f'{html.escape(str(ultima["Giocatore"]))}'
            f'</b>'
            f'&nbsp;'
            f'({len(operazioni_undo)}/10)'
            f'</div>'
        )

        st.markdown(
            testo_ultima,
            unsafe_allow_html=True
        )


with st.expander(
    "📜 Ultime operazioni",
    expanded=False
):

    if operazioni_undo.empty:

        st.caption(
            "Nessuna operazione registrata."
        )

    else:

        st.dataframe(
            operazioni_undo[
                [
                    "Operazione",
                    "Giocatore",
                    "Data"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


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
# DASHBOARD
# ============================================================

if sezione == "DASHBOARD":

    st.subheader(
        "📊 Dashboard"
    )

    snapshot_disponibili = (
        elenco_snapshot()
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
        div[data-testid="stNumberInput"] input {
            font-size:1.22rem !important;
            font-weight:800 !important;
            text-align:center !important;
            min-height:58px !important;
            border:2px solid #94a3b8 !important;
            border-radius:10px !important;
            background:#ffffff !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border:2px solid #94a3b8 !important;
            border-radius:10px !important;
            background:#ffffff !important;
            min-height:50px !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
        div[data-testid="stNumberInput"]:focus-within input {
            border-color:#071a2f !important;
            box-shadow:0 0 0 3px rgba(7,26,47,.10) !important;
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
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInput"] [data-baseweb="input"],
        div[data-testid="stNumberInput"] [data-baseweb="base-input"] {
            min-height:76px !important;
            height:76px !important;
        }

        div[data-testid="stNumberInput"] input {
            min-height:76px !important;
            height:76px !important;
            font-size:1.22rem !important;
            font-weight:800 !important;
            text-align:center !important;
            border-radius:8px 0 0 8px !important;
            padding-top:0 !important;
            padding-bottom:0 !important;
        }

        div[data-testid="stNumberInput"] button {
            height:38px !important;
            min-height:38px !important;
        }

        /* Metriche: riferimento visivo per l'altezza della riga */
        div[data-testid="stMetric"] {
            min-height:76px !important;
            height:76px !important;
            padding:8px 12px !important;
            display:flex !important;
            flex-direction:column !important;
            justify-content:center !important;
            box-sizing:border-box !important;
        }

        @media (max-width:768px) {
            div[data-testid="stNumberInput"] input {
                font-size:1.08rem !important;
                min-height:52px !important;
            }

            div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
                min-height:46px !important;
            }

            div[class*="st-key-btn_acquista_"] .stButton > button,
            div[class*="st-key-btn_avversario_"] .stButton > button {
                min-height:68px !important;
                height:68px !important;
            }
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

                g1, g2, g3, g4, g5, g6 = (
                    st.columns(
                        [
                            1.15,
                            0.85,
                            0.80,
                            0.65,
                            1.20,
                            0.95
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

                g4.metric(
                    "FVM",
                    giocatore["FVM"]
                )

                with g5:

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

                with g6:

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

    if not df_rosa.empty:
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
            h1, h2, h3, h4 = st.columns(
                [2.4, 1.0, 1.1, 0.7]
            )

            h1.markdown("**NOME GIOCATORE**")
            h2.markdown("**RUOLO**")
            h3.markdown("**PREZZO**")
            h4.markdown("**OK**")

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

                r1, r2, r3, r4 = st.columns(
                    [2.4, 1.0, 1.1, 0.7],
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

                with r3:

                    nuovo_prezzo = st.number_input(
                        "Prezzo",
                        min_value=0.0,
                        max_value=5000.0,
                        step=0.10,
                        format="%.2f",
                        key=chiave_prezzo,
                        label_visibility="collapsed"
                    )

                with r4:

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
                "Qt.",
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
                cols[3].write(
                    giocatore["Qt.A"]
                )
                cols[4].write(
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

                with cols[5]:

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

                with cols[6]:
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

                with cols[7]:
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
        "Fonte: GOAL Italia — formazioni tipo stagionali. "
        "I dati sono stagionali, non riferiti alla singola giornata. "
        "Il consenso delle guide viene trasformato in "
        "TITOLARE / BALLOTTAGGIO / RISERVA."
    )

    legenda = (
        '<div style="display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 12px 0;">'
        '<span style="background:#dcfce7;color:#15803d;border-radius:7px;padding:5px 9px;font-weight:900;">'
        '● FORMAZIONE TIPO</span>'
        '<span style="background:#dbeafe;color:#1d4ed8;border-radius:7px;padding:5px 9px;font-weight:900;">'
        '● ALTRO POSSIBILE TITOLARE</span>'
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
