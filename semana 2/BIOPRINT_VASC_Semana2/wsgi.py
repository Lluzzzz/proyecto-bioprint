"""Entrada WSGI para PythonAnywhere. Reutiliza la API y SQLite de BIOPRINT-VASC.

Sin dependencias externas; no usar `python wsgi.py` para arrancar en local.
"""
from __future__ import annotations
import hashlib
import json
import mimetypes
import os
import sqlite3
from pathlib import Path
from urllib.parse import unquote
from app import (
    ROOT, DEFAULT_DB, APP_VERSION, Handler, jsondump,
    history, load, save, session,
)
from numericos import simulate

DB_PATH = Path(os.getenv('BIOPRINT_DB_PATH', str(DEFAULT_DB))).expanduser()

STATUS = {200:'200 OK',400:'400 Bad Request',403:'403 Forbidden',404:'404 Not Found',
          405:'405 Method Not Allowed',413:'413 Content Too Large',500:'500 Internal Server Error'}


def reply(start_response, status, payload, head=False):
    body=jsondump(payload).encode('utf-8')
    start_response(STATUS[status],[('Content-Type','application/json; charset=utf-8'),
                                   ('Content-Length',str(len(body))),('Cache-Control','no-store'),
                                   ('X-Content-Type-Options','nosniff')])
    return [b'' if head else body]


def static_file(start_response,path,head=False):
    # Reutiliza exactamente el filtro de rutas estáticas del servidor original.
    if not Handler.static_allowed(path):
        return reply(start_response,403,{'error':'Recurso restringido'},head=head)
    decoded=unquote(path)
    if decoded == '/':decoded='/index.html'
    file=(ROOT / decoded.lstrip('/')).resolve()
    try:
        file.relative_to(ROOT.resolve())
    except ValueError:
        return reply(start_response,403,{'error':'Recurso restringido'},head=head)
    if not file.is_file():
        return reply(start_response,404,{'error':'Archivo no encontrado'},head=head)
    media=mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
    if media.startswith('text/') or media == 'application/javascript':media+='; charset=utf-8'
    size=file.stat().st_size
    headers=[('Content-Type',media),('Content-Length',str(size)),
             ('X-Content-Type-Options','nosniff')]
    start_response(STATUS[200],headers)
    # Un solo worker gratuito: archivos relativamente pequeños.
    return [b'' if head else file.read_bytes()]


def application(environ,start_response):
    """API real + frontend; la BD permanece en el almacenamiento del usuario."""
    method=environ.get('REQUEST_METHOD','GET').upper()
    path=environ.get('PATH_INFO','/') or '/'
    try:
        if method in ('GET','HEAD'):
            head=(method=='HEAD')
            if path == '/api/health':
                with session(DB_PATH) as db:
                    db.execute('SELECT COUNT(*) FROM caso_estudio').fetchone()
                return reply(start_response,200,{'ok':True,'version':APP_VERSION,
                    'db':'SQLite','almacenamiento':'archivo persistente de PythonAnywhere',
                    'persistencia_garantizada':True,   # Se conserva en disco entre recargas y reinicios normales.
                    'nota':'Los datos sobreviven a recargas/reinicios normales, sujetos a la cuota y estado de la cuenta'},head)
            if path == '/api/history':
                return reply(start_response,200,{'items':history(DB_PATH)},head)
            if path.startswith('/api/history/'):
                try: ident=int(path.split('/')[-1])
                except ValueError: return reply(start_response,400,{'error':'ID inválido'},head)
                record=load(DB_PATH,ident)
                return reply(start_response,200 if record else 404,record or {'error':'No encontrado'},head)
            if path.startswith('/api/'):
                return reply(start_response,404,{'error':'Ruta desconocida'},head)
            return static_file(start_response,path,head)
        if method!='POST':return reply(start_response,405,{'error':'Método HTTP no permitido'})
        if path not in ('/api/simulate','/api/save','/api/replay'):
            return reply(start_response,404,{'error':'Ruta desconocida'})
        size=int(environ.get('CONTENT_LENGTH') or '0')
        if size < 1 or size > 10000:return reply(start_response,400,{'error':'Tamaño de entrada inválido'})
        raw=environ['wsgi.input'].read(size)
        entry=json.loads(raw)
        if not isinstance(entry,dict):raise ValueError('Entrada JSON inválida')
        if path == '/api/simulate':
            result=simulate(entry.get('case'),entry.get('scenario','NORMAL'),entry.get('params',{}))
        elif path == '/api/save':
            result=save(DB_PATH,entry)
        else:
            ident=entry.get('id')
            if type(ident) is not int or ident < 1:raise ValueError('ID de histórico inválido')
            record=load(DB_PATH,ident)
            if record is None:return reply(start_response,404,{'error':'Registro no encontrado'})
            inp=record['input']
            fresh=simulate(inp['case'],inp['scenario'],inp['params'])
            digest=hashlib.sha256(jsondump(fresh).encode('utf-8')).hexdigest()
            result={'id':ident,'coincide':digest==record['sha256'],
                    'sha256_original':record['sha256'],'sha256_repeticion':digest,'result':fresh}
        return reply(start_response,200,result)
    except (ValueError,TypeError,KeyError,sqlite3.Error,OverflowError) as exc:
        return reply(start_response,400,{'error':str(exc)})
    except Exception:
        # No exponer datos internos de servidor en respuestas públicas.
        import logging
        logging.exception('Error inesperado en BIOPRINT-VASC')
        return reply(start_response,500,{'error':'Error interno del servidor'})
