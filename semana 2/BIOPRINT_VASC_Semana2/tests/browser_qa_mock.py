"""QA visual/funcional del frontend con API simulada. No verifica la red real.
API HTTP y SQLite se prueban aparte con test_api.py.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
from sys import path
import json
root=Path(__file__).resolve().parents[1]
path.insert(0,str(root))
from numericos import simulate,CASES,SCENARIOS
fixture={f'{c}|{s}':simulate(c,s) for c in CASES for s in SCENARIOS}
# Los parámetros por defecto enviados coinciden con los escenarios en simulaciones de prueba.
import re
html=(root/'index.html').read_text(encoding='utf8')
html=re.sub(r'<script defer src="src/[^\"]+\.js"></script>','',html)
html=html.replace('<link rel="stylesheet" href="src/estilos.css">','')
css=(root/'src'/'estilos.css').read_text(encoding='utf8')
js=(root/'src'/'app.js').read_text(encoding='utf8')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1360,'height':940},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html,wait_until='domcontentloaded')
 page.add_style_tag(content=css)
 page.evaluate('''(dataset) => {window.__dataset=dataset;window.__records=[];
 window.fetch=async (url,opts={})=>{let data;
  if(url==='/api/health'){data={ok:true,db:'SQLite',version:'2.1.0',persistencia_garantizada:true};}
  else if(url==='/api/simulate'){let q=JSON.parse(opts.body);data=window.__dataset[q.case+'|'+q.scenario];}
  else if(url==='/api/save'){let q=JSON.parse(opts.body);const rec={id:window.__records.length+1,input:q,result:window.__dataset[q.case+'|'+q.scenario],sha256:'dummySha256'};window.__records.push(rec);data={id:rec.id,sha256:rec.sha256,result:rec.result};}
  else if(url==='/api/history'){data={items:window.__records.map(r=>({id:r.id,fecha:'2026-11-20T19:00:00Z',caso_id:r.input.case,tipo:r.input.scenario,equipo:'Equipo UMSA',sha256_resultado:r.sha256}))};}
  else if(url.startsWith('/api/history/')){data=window.__records.find(r=>r.id==Number(url.split('/').pop()));}
  else if(url==='/api/replay'){let q=JSON.parse(opts.body),r=window.__records.find(r=>r.id==q.id);data={id:r.id,coincide:true,sha256_original:r.sha256,sha256_repeticion:r.sha256,result:r.result};}
  else{throw Error('Unexpected URL '+url)};
  return new Response(JSON.stringify(data),{status:200,headers:{'content-type':'application/json'}})
 }
 }''',fixture)
 page.add_script_tag(content=(root/'src'/'oxygen_model.js').read_text(encoding='utf8'))
 page.add_script_tag(content=(root/'src'/'visual.js').read_text(encoding='utf8'))
 page.add_script_tag(content=js)
 assert page.locator('.moduleCard').count()==4
 page.locator('#backendStatus.connected').wait_for()
 page.screenshot(path=str(root/'docs'/'captura_inicio.png'),full_page=True)
 counts=[]
 for c in CASES:
  page.locator('.moduleCard[data-open="'+c+'"]').click() if c=='extrusion' else page.locator('.moduleTabs button[data-open="'+c+'"]').click()
  page.wait_for_function("document.querySelector('#methodRows tr')?.dataset.method !== undefined")
  count=page.locator('#methodRows tr[data-method]').count();assert count>=3,(c,count)
  page.locator('tr[data-method]').first.click();assert page.locator('.detailsTitle').count()==1
  page.locator('#compareBtn').click();page.wait_for_function("document.querySelectorAll('#compareArea tbody tr').length===3")
  page.screenshot(path=str(root/'docs' / f'captura_{c}.png'),full_page=True)
  counts.append((c,count))
 page.locator('#saveBtn').click();page.wait_for_function("document.querySelector('#alert').textContent.includes('Guardado en SQLite')")
 page.locator('.topnav button[data-action="history"]').click();page.wait_for_function("document.querySelectorAll('.historyRecord').length>0")
 page.screenshot(path=str(root/'docs'/'captura_historial.png'),full_page=True)
 page.locator('.historyRecord [data-replay]').click();page.wait_for_function("document.querySelector('#alert').textContent.includes('SHA-256 idéntico')")
 assert not errors,errors
 print('QA VISUAL UI con respuestas simuladas: OK',counts,'repeticion, graficos, escenarios')
 browser.close()
