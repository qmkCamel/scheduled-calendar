import json
import re
import secrets
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from server import CalendarServer, Handler


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.server=CalendarServer(('127.0.0.1',0),Handler)
        cls.server.home=Path(cls.temp.name)
        cls.server.token=secrets.token_urlsafe(32)
        cls.server.instance=secrets.token_hex(16)
        cls.server.demo=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.api='/api/calendar?start=2026-09-01T00:00:00Z&end=2026-09-08T00:00:00Z'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()

    def fetch(self,path,headers=None,method='GET'):
        request=urllib.request.Request(self.base+path,headers=headers or {},method=method)
        try:
            with urllib.request.urlopen(request) as response:return response.status,response.headers,response.read()
        except urllib.error.HTTPError as response:
            with response:return response.code,response.headers,response.read()

    def test_index_includes_token_and_security_headers(self):
        code,headers,body=self.fetch('/')
        self.assertEqual(code,200);self.assertIn(self.server.token.encode(),body)
        self.assertEqual(headers['Cache-Control'],'no-store');self.assertIn("default-src 'self'",headers['Content-Security-Policy'])

    def test_api_requires_page_token(self):
        self.assertEqual(self.fetch(self.api)[0],403)
        code,_,body=self.fetch(self.api,{'X-Calendar-Token':self.server.token})
        self.assertEqual(code,200);self.assertEqual(json.loads(body)['tasks'],[])

    def test_cross_origin_rejected(self):
        self.assertEqual(self.fetch(self.api,{'Origin':'https://example.com','X-Calendar-Token':self.server.token})[0],403)

    def test_rebinding_host_rejected(self):
        self.assertEqual(self.fetch('/',{'Host':'malicious.example'})[0],403)

    def test_no_mutation_endpoint(self):
        self.assertEqual(self.fetch(self.api,method='POST')[0],501)

    def test_no_arbitrary_file_reads(self):
        self.assertEqual(self.fetch('/../../auth.json')[0],404)

    def test_bad_range_is_400(self):
        self.assertEqual(self.fetch('/api/calendar?start=bad&end=bad',{'X-Calendar-Token':self.server.token})[0],400)


if __name__=='__main__':unittest.main()
