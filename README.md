# FANTAELEGANZA 26/27 - Cloud

Questa cartella contiene la versione Cloud di FANTAELEGANZA.

## File
- `app.py` — applicazione completa.
- `requirements.txt` — dipendenze Python.
- `.streamlit/config.toml` — configurazione Streamlit.
- `.gitignore` — evita di pubblicare file locali/segreti.

## Database persistente
Su Streamlit Community Cloud il filesystem locale non è garantito.
Questa versione usa quindi Turso/libSQL quando sono presenti i segreti:

- `TURSO_DATABASE_URL`
- `TURSO_AUTH_TOKEN`

Se questi segreti non sono presenti, l'app continua a funzionare localmente con `fantacalcio.db`.

## Secrets su Streamlit Community Cloud

Inserire nelle impostazioni Secrets dell'app:

```toml
TURSO_DATABASE_URL = "libsql://..."
TURSO_AUTH_TOKEN = "..."
```

## Deploy
1. Crea un repository GitHub.
2. Carica tutto il contenuto di questa cartella nel repository.
3. Accedi a https://share.streamlit.io con GitHub.
4. Crea una nuova app scegliendo repository, branch `main` e file `app.py`.
5. In Advanced settings / Secrets inserisci le due credenziali Turso.
6. Deploy.
