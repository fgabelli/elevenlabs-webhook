from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
import re

class handler(BaseHTTPRequestHandler):
    def html_to_text(self, html):
        """Converte HTML in testo leggibile"""
        # Rimuovi tag HTML comuni mantenendo il contenuto
        text = html.replace('<br>', '\n')
        text = text.replace('<br/>', '\n')
        text = text.replace('<br />', '\n')
        text = text.replace('</p>', '\n')
        text = text.replace('</div>', '\n')
        text = text.replace('</h1>', '\n')
        text = text.replace('</h2>', '\n')
        text = text.replace('</h3>', '\n')
        text = text.replace('<strong>', '**')
        text = text.replace('</strong>', '**')
        text = text.replace('<b>', '**')
        text = text.replace('</b>', '**')
        text = text.replace('<em>', '_')
        text = text.replace('</em>', '_')
        text = text.replace('<i>', '_')
        text = text.replace('</i>', '_')
        
        # Rimuovi tutti i tag HTML rimanenti
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decodifica entità HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Pulisci spazi multipli e righe vuote
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def do_POST(self):
        try:
            # Leggi il body della richiesta
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            raw_data = post_data.decode('utf-8')
            
            # Log dei dati ricevuti (per debug)
            print(f"Received data: {raw_data}")
            
            data = json.loads(raw_data)
            
            # Estrai i dati - supporta sia formato nested che flat
            if 'body' in data:
                # Formato nested: {"body": {"to": "...", "subject": "...", "message": "..."}}
                body = data['body']
                to_email = body.get('to', '')
                subject = body.get('subject', '')
                message = body.get('message', '')
            else:
                # Formato flat: {"to": "...", "subject": "...", "message": "..."}
                to_email = data.get('to', '')
                subject = data.get('subject', '')
                message = data.get('message', '')
            
            # Validazione
            if not to_email or not subject or not message:
                raise ValueError(f"Missing required fields. to={to_email}, subject={subject}, message={bool(message)}")
            
            # Converti HTML in testo se necessario
            if '<' in message and '>' in message:
                message = self.html_to_text(message)
                print(f"Converted HTML to text: {message[:100]}...")
            
            # Prepara i dati per SendGrid
            sendgrid_data = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {
                    "email": "supporto@revan.it",
                    "name": "Supporto Revan"
                },
                "content": [{
                    "type": "text/plain",
                    "value": message
                }]
            }
            
            # Invia l'email tramite SendGrid
            sendgrid_api_key = os.environ.get('SENDGRID_API_KEY', '')
            
            if not sendgrid_api_key:
                raise ValueError("SENDGRID_API_KEY not configured")
            
            req = urllib.request.Request(
                'https://api.sendgrid.com/v3/mail/send',
                data=json.dumps(sendgrid_data).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {sendgrid_api_key}',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    response_body = response.read()
                    print(f"SendGrid response: {response_body}")
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "Email inviata con successo"
                }).encode())
                
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"SendGrid error: {e.code} - {error_body}")
                self.send_response(200)  # Restituisco 200 per non far fallire ElevenLabs
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": f"SendGrid error: {e.code} - {error_body}"
                }).encode())
                
        except Exception as e:
            print(f"Error: {str(e)}")
            self.send_response(200)  # Restituisco 200 per non far fallire ElevenLabs
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Webhook endpoint is running. Send POST requests to this URL.')

