"""Pruebas de aplicación WSGI para alojamiento gratuito en PythonAnywhere."""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import wsgi


class WsgiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original = wsgi.DB_PATH
        wsgi.DB_PATH = Path(self.tmp.name)/'registros.sqlite3'

    def tearDown(self):
        wsgi.DB_PATH = self.original
        self.tmp.cleanup()

    def request(self, method='GET', path='/', payload=None):
        encoded = json.dumps(payload).encode() if payload is not None else b''
        env={'REQUEST_METHOD':method,'PATH_INFO':path,'CONTENT_LENGTH':str(len(encoded)),
             'wsgi.input':io.BytesIO(encoded)}
        out={}
        def start_response(status,headers):
            out['status']=status
            out['headers']=dict(headers)
        data=b''.join(wsgi.application(env,start_response))
        return out['status'],data

    def test_static_and_security(self):
        code,body=self.request(path='/')
        self.assertTrue(code.startswith('200'))
        self.assertIn(b'BIOPRINT',body)
        code,body=self.request(path='/src/oxygen_model.js')
        self.assertTrue(code.startswith('200'))
        code,body=self.request(path='/app.py')
        self.assertTrue(code.startswith('403'))
        code,body=self.request(path='/data/bioprint.sqlite3')
        self.assertTrue(code.startswith('403'))

    def test_end_to_end_save_replay(self):
        code,body=self.request(path='/api/health')
        self.assertTrue(code.startswith('200'))
        self.assertTrue(json.loads(body)['ok'])
        entry={'case':'extrusion','scenario':'NORMAL','params':{}}
        code,body=self.request('POST','/api/simulate',entry)
        self.assertTrue(code.startswith('200'),body)
        self.assertTrue(json.loads(body)['methods'])
        code,body=self.request('POST','/api/save',entry)
        self.assertTrue(code.startswith('200'),body)
        ident=json.loads(body)['id']
        self.assertTrue(wsgi.DB_PATH.exists())
        code,body=self.request(path='/api/history')
        self.assertTrue(any(item['id']==ident for item in json.loads(body)['items']))
        code,body=self.request(path=f'/api/history/{ident}')
        self.assertEqual(json.loads(body)['id'],ident)
        code,body=self.request('POST','/api/replay',{'id':ident})
        self.assertTrue(json.loads(body)['coincide'])
        # Recargar aplicacion no borra el archivo SQLite.
        code,body=self.request(path=f'/api/history/{ident}')
        self.assertTrue(code.startswith('200'))

if __name__=='__main__':unittest.main()
