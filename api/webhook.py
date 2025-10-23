from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Leggi il body della richiesta
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Estrai i dati dal body
            body = data.get('body', {})
            to_email = body.get('to', '')
            subject = body.get('subject', '')
            message = body.get('message', '')
            
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
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "Email inviata con successo"
                }).encode())
                
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": f"SendGrid error: {e.code} - {error_body}"
                }).encode())
                
        except Exception as e:
            self.send_response(500)
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

