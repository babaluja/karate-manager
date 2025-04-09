# Guida al Deployment su Render - Karate Manager

## Istruzioni passo-passo

### Fase 1: Account e registrazione

1. Vai su [render.com](https://render.com) e registra un account gratuito
   - Puoi registrarti con email o GitHub
   - Si consiglia l'accesso GitHub per facilitare il deploy

2. Una volta registrato e loggato, vai alla dashboard

### Fase 2: Configurare l'applicazione

1. Clicca su "New +" e seleziona "Web Service"

2. Collega il tuo repository GitHub
   - Se non hai già caricato il codice su GitHub, dovrai farlo prima
   - Puoi usare l'opzione "Import from GitHub" per creare un nuovo repository

3. Configura il servizio web:
   - **Nome**: `karate-manager` (o il nome che preferisci)
   - **Runtime**: Python
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `gunicorn main:app`
   - **Piano**: Free

4. Sezione "Advanced" -> Environment Variables:
   - Aggiungi `SESSION_SECRET` con un valore sicuro e casuale
   - Lascia per ora vuota `DATABASE_URL` (la aggiungeremo dopo)

5. Clicca su "Create Web Service"

### Fase 3: Configurare il database PostgreSQL

1. Dalla dashboard Render, clicca su "New +" e seleziona "PostgreSQL"

2. Configura il database:
   - **Nome**: `karate-manager-db` (o il nome che preferisci)
   - **Database**: `karate_manager`
   - **User**: `karate_user`
   - **Piano**: Free
   - **Regione**: Seleziona la regione più vicina a te

3. Clicca su "Create Database"

4. Dopo la creazione, vai alla pagina del database e copia il valore "Internal Database URL"

5. Torna al tuo web service, vai alle "Environment Variables" e:
   - Aggiungi `DATABASE_URL` con il valore copiato dal database

6. Riavvia il web service per applicare le modifiche

### Fase 4: Verifica e test

1. L'applicazione verrà deployata automaticamente
   - Ci vorrà qualche minuto per completare il deploy

2. Una volta completato, clicca sull'URL generato per aprire la tua applicazione

3. Registra un nuovo utente e verifica che tutto funzioni correttamente

## Note importanti

- Il piano gratuito di Render mette in sospensione il servizio dopo 15 minuti di inattività
- Il servizio si riattiva automaticamente quando riceve una richiesta, ma ci vuole circa 1 minuto
- Il database gratuito ha un limite di 1GB di storage
- I log del deploy e dell'applicazione sono accessibili dalla dashboard di Render

## Risoluzione problemi

- Se incontri errori di connessione al database, verifica che la variabile `DATABASE_URL` sia impostata correttamente
- Se l'applicazione non si avvia, controlla i log nella dashboard di Render
- Se devi modificare il codice, aggiorna il repository GitHub e Render farà automaticamente un nuovo deploy

## Aggiornamenti futuri

Per aggiornare l'applicazione in futuro:
1. Modifica il codice nel tuo repository locale
2. Fai commit e push su GitHub
3. Render aggiornerà automaticamente l'applicazione