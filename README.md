# ElevenLabs Email Webhook

Webhook serverless per ricevere chiamate da ElevenLabs e inviare email di riepilogo tramite SendGrid.

## Deployment su Vercel

### 1. Installa Vercel CLI (se non l'hai già)
```bash
npm install -g vercel
```

### 2. Login su Vercel
```bash
vercel login
```

### 3. Deploy del progetto
```bash
cd /home/ubuntu/elevenlabs-webhook
vercel
```

### 4. Configura la variabile d'ambiente SendGrid
Dopo il primo deploy, vai su:
- Vercel Dashboard → Il tuo progetto → Settings → Environment Variables
- Aggiungi: `SENDGRID_API_KEY` = la tua API key di SendGrid

Oppure via CLI:
```bash
vercel env add SENDGRID_API_KEY
```

### 5. Redeploy per applicare le variabili
```bash
vercel --prod
```

## Configurazione in ElevenLabs

Una volta deployato, Vercel ti darà un URL tipo:
```
https://elevenlabs-webhook-xxx.vercel.app
```

Usa questo URL nel tool di ElevenLabs al posto del webhook n8n:
```
https://elevenlabs-webhook-xxx.vercel.app/
```

## Formato dati atteso

Il webhook si aspetta questo formato JSON:
```json
{
  "body": {
    "to": "destinatario@email.com",
    "subject": "Oggetto email",
    "message": "Contenuto del messaggio",
    "cc": ""
  }
}
```

## Test locale

Per testare localmente:
```bash
export SENDGRID_API_KEY="your_api_key_here"
vercel dev
```

Poi invia una richiesta POST a `http://localhost:3000`

