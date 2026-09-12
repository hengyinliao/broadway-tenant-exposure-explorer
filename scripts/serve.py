from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/health':self.send_response(200);self.end_headers();self.wfile.write(b'broadway-tenant-exposure');return
        super().do_GET()
    def log_message(self,*args):pass
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',5190),partial(Handler,directory=str(ROOT/'frontend/dist'))).serve_forever()
