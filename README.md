# Karate Manager

Sistema di gestione per atleti di karate e pagamenti mensili.

## Funzionalità principali

- Gestione dati atleti (anagrafica, cintura, data iscrizione)
- Tracciamento quote mensili e pagamenti
- Gestione esami di passaggio cintura
- Statistiche e report finanziari
- Autenticazione utenti con email/password o PIN numerico

## Tecnologie utilizzate

- Backend: Flask (Python)
- Database: PostgreSQL (web) / SQLite (versione Android)
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Grafici: Chart.js

## Installazione locale

1. Clona il repository
2. Installa le dipendenze: `pip install -r render_requirements.txt`
3. Avvia l'applicazione: `gunicorn main:app`

## Deployment su Render

Vedi il file [RENDER_DEPLOY_GUIDE.md](RENDER_DEPLOY_GUIDE.md) per le istruzioni dettagliate.