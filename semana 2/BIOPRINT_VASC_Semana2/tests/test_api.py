"""Prueba HTTP real: correr, guardar, cerrar servidor, reiniciar, recuperar y repetir.
No publica la aplicación en Internet.
"""
from pathlib import Path
import sys,json,threading,tempfile,urllib.request,urllib.error
from functools import partial
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app import Handler

def post(port,path,payload):
 body=json.dumps(payload).encode('utf-8')
 req=urllib.request.Request(f'http://127.0.0.1:{port}{path}',body,{'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
def get(port,path):
 with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=8) as r:return json.load(r)
def start(db):
 srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,db_path=db))
 t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
 return srv,t,srv.server_address[1]
def stop(srv,t):srv.shutdown();srv.server_close();t.join(timeout=3)

def main():
 with tempfile.TemporaryDirectory() as td:
  db=Path(td)/'real.sqlite3';srv,t,port=start(db)
  try:
   assert get(port,'/api/health')['db']=='SQLite'
   for scenario in ('NORMAL','ESTRES','MAL_CONDICIONADO'):
    for case in ('extrusion','hidrogel','oscilaciones','sensores'):
     q={'case':case,'scenario':scenario,'params':{}}
     run=post(port,'/api/simulate',q)
     assert run['scenario']==scenario and run['case']==case
   input={'case':'extrusion','scenario':'NORMAL','params':{'q0':1.8,'a':.45,'n':48}}
   rec=post(port,'/api/save',input)
   assert rec['id']>=1
   assert get(port,'/api/history')['items'][0]['id']==rec['id']
   try:get(port,'/data/real.sqlite3');raise AssertionError('Base de datos expuesta')
   except urllib.error.HTTPError as exc:assert exc.code==403
  finally:stop(srv,t)
  # REINICIO REAL del servidor: la BD sigue en el mismo archivo.
  srv2,t2,port2=start(db)
  try:
   loaded=get(port2,f"/api/history/{rec['id']}")
   assert loaded['input']==input
   assert len(loaded['result']['methods'])==8
   assert len(loaded['result']['charts'])==2
   compare=post(port2,'/api/replay',{'id':rec['id']})
   assert compare['coincide']
   assert compare['sha256_original']==compare['sha256_repeticion']==rec['sha256']
   print('HTTP REAL + SQLite + REINICIO + INTEGRIDAD: OK',str(db))
  finally:stop(srv2,t2)

if __name__=='__main__':main()
