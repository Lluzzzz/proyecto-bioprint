from playwright.sync_api import sync_playwright
from pathlib import Path
import os
folder=Path(__file__).resolve().parents[1]
url='http://127.0.0.1:8710'
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1380,'height':920},device_scale_factor=1)
 errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
 page.goto(url,wait_until='domcontentloaded')
 assert page.locator('.moduleCard').count()==4
 page.screenshot(path=str(folder/'docs'/'captura_inicio.png'),full_page=True)
 rows=[]
 for i,mod in enumerate(['extrusion','hidrogel','oscilaciones','sensores']):
  page.locator('[data-open="'+mod+'"]').last.click()
  page.wait_for_function("document.querySelector('#methodRows tr')?.dataset.method !== undefined")
  assert page.locator('#methodRows tr[data-method]').count()>=3
  page.locator('#methodRows tr[data-method]').first.click()
  assert page.locator('#methodDetails .detailsTitle').count()==1
  page.locator('#compareBtn').click()
  page.wait_for_function("document.querySelectorAll('#compareArea tbody tr').length === 3")
  rows.append((mod,page.locator('#methodRows tr[data-method]').count(),page.locator('#compareArea tbody tr').count()))
  if mod=='extrusion':page.screenshot(path=str(folder/'docs'/'captura_extrusion.png'),full_page=True)
  if mod=='hidrogel':page.screenshot(path=str(folder/'docs'/'captura_hidrogel.png'),full_page=True)
  if mod=='oscilaciones':page.screenshot(path=str(folder/'docs'/'captura_oscilaciones.png'),full_page=True)
  if mod=='sensores':page.screenshot(path=str(folder/'docs'/'captura_sensores.png'),full_page=True)
 # Persistencia: guardar un experimento, recuperar de la base, relanzar y comparar hash.
 page.locator('#saveBtn').click()
 page.wait_for_function("document.querySelector('#alert').textContent.includes('Guardado en SQLite')")
 page.locator('.topnav button[data-action="history"]').click()
 page.wait_for_function("document.querySelectorAll('.historyRecord').length>0")
 assert page.locator('.historyRecord').count()>=1
 page.screenshot(path=str(folder/'docs'/'captura_historial.png'),full_page=True)
 page.locator('.historyRecord [data-replay]').first.click()
 page.wait_for_function("document.querySelector('#alert').textContent.includes('SHA-256 idéntico')")
 assert page.locator('#plot0').count()==1
 # Actualizar de nuevo para confirmar persistencia fuera de variables JS.
 page.reload(wait_until='domcontentloaded')
 page.locator('.topnav button[data-action="history"]').click()
 page.wait_for_function("document.querySelectorAll('.historyRecord').length>0")
 page.locator('.historyRecord [data-load]').first.click()
 page.wait_for_function("document.querySelector('#alert').textContent.includes('recuperada')")
 assert page.locator('#methodRows tr[data-method]').count()==3
 print('QA_BROWSER OK:',rows,'persistencia, recarga, replay SHA256; JS errors=',errs)
 assert not errs,errs
 browser.close()
