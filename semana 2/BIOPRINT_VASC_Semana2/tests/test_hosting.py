"""Comprueba el arranque tipo Render con PORT y HOST automáticos.
Es una prueba HTTP REAL, sin navegador ni librerías externas.
"""
import os,sys,time,json,socket,subprocess,urllib.request,urllib.error,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class RenderBoot(unittest.TestCase):
 def test_port_autobinding_and_api(self):
  with tempfile.TemporaryDirectory(prefix='bioprint_qa_') as td:
   with socket.socket() as s:
    s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   env=os.environ.copy();env.update({'PORT':str(port),'RENDER':'true','BIOPRINT_DB_PATH':str(Path(td)/'prueba.sqlite3'),'BIOPRINT_QUIET':'1'})
   p=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   try:
    for _ in range(100):
     try:
      with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health',timeout=.4) as res:
       data=json.load(res)
      if data.get('ok'):break
     except Exception:time.sleep(.05)
    else:self.fail('Servidor no respondió con PORT suministrado')
    self.assertEqual(data['db'],'SQLite')
    self.assertTrue(data['persistencia_garantizada'])
    for path in ('/','/index.html','/src/app.js','/src/estilos.css','/src/oxygen_model.js','/src/visual.js','/semana1/index.html','/assets/concepto_extrusion.webp','/assets/concepto_hidrogel.webp','/assets/concepto_oscilaciones.webp','/assets/concepto_sensores.webp'):
     with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=5) as r:self.assertEqual(r.status,200,path)
    for path in ('/app.py','/numericos.py','/docs/esquema.sql','/data/prueba.sqlite3','/.gitignore'):
     with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=5)
     self.assertEqual(cm.exception.code,403,path)
    body=json.dumps({'case':'extrusion','scenario':'NORMAL','params':{'q0':1.2,'a':.4,'n':24}}).encode('utf8')
    rq=urllib.request.Request(f'http://127.0.0.1:{port}/api/save',body,{'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(rq,timeout=10) as resp:saved=json.load(resp)
    self.assertEqual(saved['id'],1)
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/history/1',timeout=5) as resp:record=json.load(resp)
    self.assertEqual(record['sha256'],saved['sha256'])
   finally:
    p.terminate()
    try:p.wait(timeout=4)
    except subprocess.TimeoutExpired:p.kill()
    if p.stderr is not None:p.stderr.close()

if __name__=='__main__': unittest.main()
