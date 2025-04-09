# Guida per caricare il codice su GitHub

## Configurazione del repository remoto

Per caricare il codice su GitHub, devi:

1. **Creare un repository su GitHub**:
   - Vai su [github.com](https://github.com) e accedi
   - Clicca sul pulsante "+" in alto a destra
   - Seleziona "New repository"
   - Assegna un nome al repository (es: "karate-manager")
   - Scegli se renderlo pubblico o privato
   - Clicca "Create repository"

2. **Copia l'URL del repository**:
   - Dopo aver creato il repository, vedrai una pagina di guida rapida
   - Copia l'URL del repository (es: `https://github.com/tuousername/karate-manager.git`)

3. **Esegui questi comandi in Replit Shell**:
   ```bash
   # Imposta la tua identità Git (sostituisci con i tuoi dati)
   git config --global user.name "Il Tuo Nome"
   git config --global user.email "tua.email@esempio.com"

   # Aggiungi il repository remoto (sostituisci con l'URL del tuo repository)
   git remote add origin https://github.com/tuousername/karate-manager.git

   # Fai il commit delle modifiche
   git commit -m "Commit iniziale: Karate Manager App"

   # Pusha il codice sul repository remoto
   git push -u origin main
   ```

4. **Autenticazione**:
   - GitHub ti chiederà di autenticarti
   - Puoi usare:
     - Username e password (se hai abilitato la 2FA, dovrai usare un token)
     - Token di accesso personale (consigliato)
     - SSH (configurazione più avanzata)

## Generare un token di accesso personale (consigliato)

1. Vai su GitHub > Settings > Developer settings > Personal access tokens
2. Clicca "Generate new token"
3. Dai un nome al token (es. "Replit Access")
4. Seleziona gli scope "repo" per accesso completo ai repository
5. Clicca "Generate token"
6. **IMPORTANTE**: Copia il token generato e salvalo in un luogo sicuro (sarà mostrato solo una volta)
7. Quando ti viene richiesta l'autenticazione durante il push, usa il tuo username GitHub e il token come password

## Verificare il caricamento

Dopo aver completato il push, vai alla pagina del tuo repository su GitHub per verificare che tutti i file siano stati caricati correttamente.

## Aggiornamenti futuri

Per aggiornare il repository dopo modifiche future:
```bash
git add .
git commit -m "Descrizione delle modifiche"
git push
```