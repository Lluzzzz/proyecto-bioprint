"""Prueba visual del front-end con servidor simulado + capturas normal/estrés/células.
No reemplaza las pruebas reales de HTTP y SQLite incluidas en tests/test_*.py.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import sys,re
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from numericos import simulate,CASES,SCENARIOS
fixtures={f'{c}|{s}':simulate(c,s) for c in CASES for s in SCENARIOS}
html=(root/'index.html').read_text(encoding='utf8')
html=re.sub(r'<script defer src="src/[^\"]+\.js"></script>','',html)
html=html.replace('<link rel="stylesheet" href="src/estilos.css">','')
css=(root/'src/estilos.css').read_text(encoding='utf8')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1360,'height':960},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='domcontentloaded');page.add_style_tag(content=css)
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
    }''',fixtures)
    page.add_script_tag(content=(root/'src/oxygen_model.js').read_text())
    page.add_script_tag(content=(root/'src/visual.js').read_text())
    page.add_script_tag(content=(root/'src/app.js').read_text())
    page.locator('#backendStatus.connected').wait_for(timeout=5000)
    assert page.locator('.moduleCard').count()==4
    normal=page.locator('#oxygenMin').inner_text()
    assert normal.startswith('0,811'),normal
    assert page.locator('#oxygenLowArea').inner_text()=='0,0 %'
    page.screenshot(path=str(root/'docs/captura_tejido_normal.png'),full_page=True,timeout=20000)
    page.locator('#distanceRange').evaluate("el => {el.value = '0.8'; el.dispatchEvent(new Event('input',{bubbles:true}));}")
    stress=page.locator('#oxygenMin').inner_text()
    area=page.locator('#oxygenLowArea').inner_text()
    assert stress.startswith('0,325'),stress
    assert float(area.replace('%','').replace(',','.'))>60,area
    page.screenshot(path=str(root/'docs/captura_tejido_estres.png'),full_page=True,timeout=20000)
    page.locator('.oxygenStudio').screenshot(path=str(root/'docs/preview_simulacion_tejido.png'),timeout=20000)
    page.locator('#showCells').click()
    assert page.locator('#showCells').get_attribute('aria-pressed')=='true'
    page.screenshot(path=str(root/'docs/captura_tejido_celulas.png'),full_page=True,timeout=20000)
    page.locator('#openSensors').click()
    assert page.locator('#lab').is_visible()
    assert 'Sensores' in page.locator('#modTitle').inner_text()
    page.wait_for_function("document.querySelector('#methodRows tr')?.dataset.method !== undefined")
    count=page.locator('#methodRows tr[data-method]').count()
    assert count>=3,count
    assert not errors,errors
    page.set_viewport_size({'width':390,'height':844})
    page.locator('button[data-action="home"]').first.click()
    page.wait_for_timeout(100)
    dimensions=page.evaluate('''()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})''')
    assert dimensions['scroll']<=dimensions['client']+2,dimensions
    page.screenshot(path=str(root/'docs/captura_visual_movil.png'),full_page=True,timeout=20000)
    print('QA visual OK: 4 módulos, oxígeno normal/estrés, área calculada',area,'vistas, navegación,',count,'métodos; sin errores JS')
    browser.close()
