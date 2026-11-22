"""Servidor local + SQLite de BIOPRINT-VASC semana 2 (Python 3, sin paquetes externos)."""
import argparse
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from numericos import simulate, CASES

ROOT=Path(__file__).resolve().parent
DEFAULT_DB=Path(os.environ.get('BIOPRINT_DB_PATH',str(ROOT/'data'/'bioprint.sqlite3'))).expanduser()
APP_VERSION='2.3.0'


def jsondump(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)

def connect(db_path):
    path=Path(db_path);path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(str(path),timeout=10)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript((ROOT/'docs'/'esquema.sql').read_text(encoding='utf-8'))
    for case,title in [('extrusion','Parada de extrusión'),('hidrogel','Degradación del hidrogel'),('oscilaciones','Oscilaciones del cabezal'),('sensores','Sensores de oxígeno')]:
        db.execute('INSERT OR IGNORE INTO caso_estudio(id,nombre,modelo_version) VALUES(?,?,?)',(case,title,'2.0.0'))
    db.commit();return db


@contextmanager
def session(db_path):
    db=connect(db_path)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def save(db_path,entry,team='Equipo UMSA'):
    if not isinstance(entry,dict):raise ValueError('Entrada inválida')
    case=entry.get('case');scenario=entry.get('scenario','NORMAL');params=entry.get('params',{})
    # Always compute server-side; never trust a client-supplied result.
    result=simulate(case,scenario,params)
    payload={'case':case,'scenario':scenario,'params':params}
    text=jsondump(result);digest=hashlib.sha256(text.encode('utf-8')).hexdigest()
    with session(db_path) as db:
        cur=db.execute('INSERT INTO escenario(caso_id,tipo,parametros_json,fuente_datos) VALUES(?,?,?,?)',
                       (case,scenario,jsondump(result['params']),'sintético'))
        sid=cur.lastrowid
        cur=db.execute('INSERT INTO simulacion(escenario_id,fecha,equipo,entrada_json,resultado_json,sha256_resultado) VALUES(?,?,?,?,?,?)',
                       (sid,datetime.now(timezone.utc).isoformat(),team,jsondump(payload),text,digest))
        sim_id=cur.lastrowid
        for method in result['methods']:
            cur=db.execute('''INSERT INTO ejecucion_metodo(simulacion_id,metodo,tolerancia,paso,max_iter,iteraciones,convergio,valor,residual,error_abs,error_rel)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)''',(sim_id,method['method'],1e-10,result['params'].get('T',None),250,method['iterations'],
                                            1 if method['converged'] else 0,method['value'],method['residual'],method['error_abs'],method['error_rel_pct']))
            method_id=cur.lastrowid
            for ix,row in enumerate(method.get('details',[])):
                db.execute('INSERT INTO iteracion_resultado(ejecucion_id,numero,aproximacion_json,residual,error_abs,error_rel) VALUES(?,?,?,?,?,?)',
                           (method_id,ix+1,jsondump(row),row[-1] if len(row)>1 else None,None,None))
        db.execute('''INSERT INTO resultado_resumen(simulacion_id,referencia_json,metricas_json,interpretacion_numerica,interpretacion_problema)
                   VALUES(?,?,?,?,?)''',(sim_id,jsondump(result['reference']),jsondump([{'metodo':m['method'],'error':m['error_abs']} for m in result['methods']]),
                                       result['numerical_conclusion'],result['problem_conclusion']))
        db.commit()
    return {'id':sim_id,'sha256':digest,'result':result}


def history(db_path,limit=50):
    with session(db_path) as db:
        rows=db.execute('''SELECT s.id,s.fecha,e.caso_id,e.tipo,s.equipo,s.sha256_resultado
                        FROM simulacion s JOIN escenario e ON e.id=s.escenario_id
                        ORDER BY s.id DESC LIMIT ?''',(min(max(1,limit),100),)).fetchall()
        return [dict(x) for x in rows]


def load(db_path,id):
    with session(db_path) as db:
        row=db.execute('SELECT * FROM simulacion WHERE id=?',(id,)).fetchone()
        if not row:return None
        saved=row['resultado_json'];digest=hashlib.sha256(saved.encode('utf-8')).hexdigest()
        if digest!=row['sha256_resultado']:raise ValueError('Integridad de historial fallida')
        return {'id':id,'fecha':row['fecha'],'input':json.loads(row['entrada_json']),
                'result':json.loads(saved),'sha256':digest}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,db_path=None,**kwargs):
        self.db_path=db_path or DEFAULT_DB
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def _reply(self,status,payload):
        body=jsondump(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(body)
    @staticmethod
    def static_allowed(path):
        # En producción publicar solo los archivos necesarios para la interfaz.
        # Desactiva la exposición de base de datos, código Python, pruebas y configuración.
        from urllib.parse import unquote
        import posixpath
        decoded=unquote(path)
        clean=posixpath.normpath(decoded)
        if decoded != clean and not (decoded.endswith('/') and decoded.rstrip('/') == clean):
            return False
        return (clean in ('/','/index.html','/favicon.ico')
                or clean.startswith(('/src/','/assets/','/semana1/')) and
                clean.endswith(('.html','.js','.css','.png','.jpg','.jpeg','.svg','.ico','.webp')))
    def do_HEAD(self):
        path=urlsplit(self.path).path
        if not self.static_allowed(path):return self._reply(403,{'error':'Recurso restringido'})
        return super().do_HEAD()
    def do_GET(self):
        path=urlsplit(self.path).path
        try:
            if path=='/api/health':
                with session(self.db_path) as db:
                    db.execute('SELECT COUNT(*) FROM caso_estudio').fetchone()
                return self._reply(200,{'ok':True,'version':APP_VERSION,'db':'SQLite',
                                        'almacenamiento':('temporal (se pierde al reiniciar o redesplegar)' if os.getenv('RENDER') and not os.getenv('BIOPRINT_DB_PATH') else 'configurado localmente'),
                                        'persistencia_garantizada':not bool(os.getenv('RENDER') and not os.getenv('BIOPRINT_DB_PATH'))})
            if path=='/api/history':return self._reply(200,{'items':history(self.db_path)})
            if path.startswith('/api/history/'):
                try:id=int(path.split('/')[-1])
                except ValueError:return self._reply(400,{'error':'ID inválido'})
                record=load(self.db_path,id)
                return self._reply(200 if record else 404,record or {'error':'No encontrado'})
            if path.startswith('/api/'):return self._reply(404,{'error':'Ruta desconocida'})
            if not self.static_allowed(path):return self._reply(403,{'error':'Recurso restringido'})
            return super().do_GET()
        except (ValueError,sqlite3.Error) as exc:return self._reply(400,{'error':str(exc)})
    def do_POST(self):
        path=urlsplit(self.path).path
        if path not in ('/api/simulate','/api/save','/api/replay'):return self._reply(404,{'error':'Ruta desconocida'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<1 or size>10000:raise ValueError('Tamaño de entrada inválido')
            entry=json.loads(self.rfile.read(size))
            if not isinstance(entry,dict):raise ValueError('Entrada JSON inválida')
            if path=='/api/simulate':
                result=simulate(entry.get('case'),entry.get('scenario','NORMAL'),entry.get('params',{}))
            elif path=='/api/save':
                result=save(self.db_path,entry)
            else:
                ident=entry.get('id')
                if type(ident) is not int or ident < 1:raise ValueError('ID de histórico inválido')
                record=load(self.db_path,ident)
                if record is None:return self._reply(404,{'error':'Registro no encontrado'})
                old=record['result'];inp=record['input']
                fresh=simulate(inp['case'],inp['scenario'],inp['params'])
                new_digest=hashlib.sha256(jsondump(fresh).encode('utf-8')).hexdigest()
                result={'id':ident,'coincide':new_digest==record['sha256'],'sha256_original':record['sha256'],
                        'sha256_repeticion':new_digest,'result':fresh}
            return self._reply(200,result)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError,sqlite3.Error) as exc:
            return self._reply(400,{'error':str(exc)})
    def log_message(self,fmt,*args):
        if os.getenv('BIOPRINT_QUIET')!='1':super().log_message(fmt,*args)

def serve(host='127.0.0.1',port=8000,db_path=DEFAULT_DB):
    from functools import partial
    with ThreadingHTTPServer((host,port),partial(Handler,db_path=db_path)) as server:
        print(f'BIOPRINT-VASC S2: http://{host}:{port} | BD: {db_path}',flush=True)
        server.serve_forever()

if __name__=='__main__':
    p=argparse.ArgumentParser(description='BIOPRINT-VASC Semana 2')
    # En local escucha solo en localhost. En Render escucha por defecto en todas las interfaces
    # y utiliza el PORT inyectado por el alojamiento para evitar fallos de despliegue.
    default_host=os.environ.get('HOST','0.0.0.0' if 'PORT' in os.environ else '127.0.0.1')
    default_port=int(os.environ.get('PORT','8000'))
    p.add_argument('--host',default=default_host);p.add_argument('--port',type=int,default=default_port)
    p.add_argument('--db',default=str(DEFAULT_DB))
    args=p.parse_args();serve(args.host,args.port,args.db)
