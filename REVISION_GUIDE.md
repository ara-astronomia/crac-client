# Guida alla Revisione del Codice - crac-client

Questa guida elenca le criticità riscontrate nel client Python e suggerisce miglioramenti per la stabilità e le performance della GUI.

## ✅ 1. Unificazione dei Canali gRPC (COMPLETATO)
- **Stato:** Implementato. Un unico canale `grpc.insecure_channel` viene creato in `app.py` e passato a tutti i retriever.
- **Vantaggio:** Ridotto il consumo di risorse e socket TCP sul server e sul client.
- **Test:** Verificato con suite di test unitari in `tests/unit/retriever/test_retriever_channels.py`.

## ✅ 2. Migrazione a `uv` (COMPLETATO)
- **Stato:** Migrato da Poetry a `uv`. Aggiornato `pyproject.toml` allo standard PEP 621.
- **Nota:** Per eseguire i test o l'app, usare `uv run`. Ricordarsi che il progetto va eseguito dalla cartella `crac_client/` per il corretto caricamento di configurazioni e traduzioni.

## 3. Gestione del Polling e Coda `JOBS`
- **Problema:** Il loop principale in `app.py` invia richieste di polling a tappeto ogni secondo.
- **Rischio:** Flooding della coda `JOBS` e lag della UI se le risposte gRPC arrivano più lentamente di 1s o se il processing delle risposte è lento.
- **Azione:** Implementare un meccanismo di controllo: non inviare una nuova richiesta di polling se quella precedente per lo stesso servizio è ancora in sospeso.

## 4. Ottimizzazione Performance (Plotly Gauges)
- **Problema:** `WeatherConverter` rigenera 6 immagini PNG tramite Plotly ad ogni aggiornamento meteo.
- **Azione:** 
    - Verificare se il valore è cambiato prima di rigenerare l'immagine.
    - Considerare l'uso di widget nativi di `FreeSimpleGUI` per indicatori semplici invece di immagini pesanti.

## 5. Timeout `blocking_deque`
- **Problema:** `blocking_deque()` blocca l'avvio per 10 secondi se il server è offline.
- **Azione:** Ridurre il timeout o rendere l'inizializzazione non bloccante.

## 6. Robustezza gRPC e Error Handling
- **Problema:** `Retriever.callback` non gestisce esplicitamente i codici di errore gRPC (es. `UNAVAILABLE`).
- **Azione:** Gestire le eccezioni `grpc.RpcError` per evitare loop di errore infiniti e informare l'utente nella GUI.

## ✅ 7. Correzioni Minori (COMPLETATO)
- **File System:** Rinominato `crac_client/retriever/__init__.oy` in `__init__.py`.
- **Configurazione:** Verificare la coerenza del parametro `sleep` tra client e cloud.
