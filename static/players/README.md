# Archivio foto giocatori FantaEleganza

Percorso runtime:

`static/players/<player_id>.jpg`

## Regola prestazionale

Le fotografie sono asset statici preparati prima dell'asta. Il percorso live dell'asta non deve:
- interrogare Turso per la fotografia;
- cercare immagini sul web;
- chiamare API fotografiche;
- leggere o convertire immagini in Python;
- introdurre polling o rerun Streamlit.

Il browser richiede direttamente il JPG statico associato al player_id.

## Aggiornamento Listone

Il manifest usa l'Id Fantacalcio come chiave stabile. A ogni nuovo Listone:
1. gli ID già presenti mantengono la foto;
2. per gli ID nuovi si aggiunge solo il nuovo asset;
3. nome, squadra e ruoli possono essere aggiornati senza rinominare la foto;
4. gli ID usciti dal Listone possono restare nell'archivio senza impatto sul runtime.

Formato consigliato: JPG RGB ottimizzato, circa 300-500 px, qualità 80-85.
