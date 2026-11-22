/* BIOPRINT-VASC S2 — interfaz sin bibliotecas externas; API Python+SQLite.
   La base SQLite está en el servidor local, nunca en el cliente. */
'use strict';
const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const state={module:'extrusion',scenario:'NORMAL',current:null,entry:null,view:'home',lastSaved:null,runId:0,backendReady:false};
const modules=[
 {id:'extrusion',icon:'◉',number:'01',title:'Parada de extrusión',short:'Volumen adicional, tiempo de parada y velocidad de respuesta.',desc:'Simula el apagado controlado de un cabezal que deposita biotinta, comparando raíces, integración y Runge-Kutta.'},
 {id:'hidrogel',icon:'⌁',number:'02',title:'Degradación del hidrogel',short:'Umbrales de deterioro y sistemas lineales de calibración.',desc:'Estima cuándo un indicador de estabilidad del hidrogel alcanza un umbral sintético. Incluye una calibración 4×4 SPD.'},
 {id:'oscilaciones',icon:'∿',number:'03',title:'Oscilaciones del cabezal',short:'Dinámica de vibraciones y amortiguamiento.',desc:'Estudia las vibraciones libres de un cabezal idealizado con RK2, RK4 e integrales de desplazamiento cuadrático.'},
 {id:'sensores',icon:'⌗',number:'04',title:'Sensores de oxígeno',short:'Interpolación, reconstrucción y sensibilidad de señales.',desc:'Recupera mediciones faltantes a partir de una señal sintética mediante Lagrange, Newton y splines cúbicos.'}
];
// Ilustraciones conceptuales: no sustituyen gráficos ni valores del solucionador.
const conceptInfo={
 extrusion:{alt:'Boquilla de bioimpresión depositando un entramado de biotinta rosada',title:'¿Qué pasa al detener la extrusión?',explain:'La boquilla deposita biotinta. Aunque se ordene detener el flujo, el modelo permite calcular cuánto material adicional podría salir durante la desaceleración.',output:'Tiempo de parada, volumen depositado y comparación de raíces, integrales y RK2/RK4.'},
 hidrogel:{alt:'Hidrogel poroso conceptual que pasa de una estructura intacta a una red deteriorada',title:'¿Cuándo se deteriora el hidrogel?',explain:'Representamos el cambio de un indicador de deterioro a lo largo del tiempo. Buscamos cuándo alcanza un umbral de revisión definido para el ejercicio.',output:'Instante de cruce del umbral, errores de raíces y comparación de sistemas lineales.'},
 oscilaciones:{alt:'Cabezal de bioimpresora vibrando sobre una estructura de hidrogel',title:'¿Cómo influye la vibración del cabezal?',explain:'Modelamos el movimiento oscilatorio de una boquilla idealizada. La masa, la rigidez y el amortiguamiento modifican la trayectoria matemática.',output:'Desplazamiento temporal, magnitud acumulada y errores comparados de RK2 y RK4.'},
 sensores:{alt:'Hidrogel conceptual con microcanales de oxígeno y sondas de medición',title:'¿Cómo reconstruimos lecturas perdidas?',explain:'Los sensores pueden dejar espacios en una serie de datos. Aquí ocultamos puntos de una señal sintética y probamos métodos para reconstruirlos.',output:'Curvas interpoladas, puntos de validación ocultos y error frente a la referencia conocida.'}
};
const parameterConfig={
 extrusion:[['q0','Caudal inicial','mL/s',1.2,0.05,10,.05],['a','Desaceleración','mL/s²',.4,.01,3,.01],['n','Subintervalos (par)','n',24,8,500,2]],
 hidrogel:[['d0','Deterioro inicial','índice',.1,0,.95,.01],['alpha','Coef. lineal α','1/día',.07,.005,1,.005],['beta','Coef. cuadrático β','1/día²',.004,0,.1,.001],['umbral','Umbral de inspección','índice',.65,.1,2,.01]],
 oscilaciones:[['m','Masa del cabezal','kg',1,.1,10,.1],['c','Amortiguamiento','N·s/m',.8,.0001,50,'any'],['k','Rigidez','N/m',16,.1,100,'any'],['x0','Posición inicial','m',.015,-1,1,.005],['v0','Velocidad inicial','m/s',0,-1,1,.05],['T','Duración','s',8,1,20,.5],['n','Pasos (pares)','n',80,8,400,2]],
 sensores:[['ruido','Amplitud de ruido sintético','adimensional',0,0,.07,.002]]
};
const presets={
 NORMAL:{extrusion:{q0:1.2,a:.4,n:24},hidrogel:{d0:.1,alpha:.07,beta:.004,umbral:.65},oscilaciones:{m:1,c:.8,k:16,x0:.015,v0:0,T:8,n:80},sensores:{ruido:0}},
 ESTRES:{extrusion:{q0:1.5,a:.22,n:24},hidrogel:{d0:.1,alpha:.11,beta:.007,umbral:.65},oscilaciones:{m:1,c:.3,k:16,x0:.03,v0:0,T:10,n:80},sensores:{ruido:.012}},
 MAL_CONDICIONADO:{extrusion:{q0:1.2,a:.4,n:24},hidrogel:{d0:.1,alpha:.07,beta:.004,umbral:.65},oscilaciones:{m:1,c:7.999992,k:16,x0:.015,v0:0,T:8,n:80},sensores:{ruido:0}}
};
const scenarioInfo={NORMAL:'Parámetros de referencia y datos sintéticos consistentes. Se comparan soluciones con valores analíticos.',ESTRES:'Condición más exigente en el modelo. No debe confundirse automáticamente con mal condicionamiento matemático.',MAL_CONDICIONADO:'Subexperimento numéricamente sensible (raíz múltiple, matriz reescalada, casi amortiguamiento crítico o interpolación de Runge).'};
const colors=['#713849','#c59b59','#4d8177','#8c829c','#c77c6b','#668eaf'];
function esc(s){return String(s??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function fmt(v){if(v===null||v===undefined||!Number.isFinite(Number(v)))return '—';let a=Math.abs(Number(v));if(a>0&&(a<.0001||a>=100000))return Number(v).toExponential(3);return Number(v).toLocaleString('es-BO',{maximumFractionDigits:6});}
function setView(view){state.view=view;$$('.view').forEach(e=>e.classList.toggle('hidden',e.id!==view));$$('.topnav button').forEach(e=>e.classList.toggle('active',e.dataset.action===view));window.scrollTo({top:0,behavior:'instant'});if(view==='history')listHistory();}
function homeCards(){
  const paths={
    extrusion:'M2 10 C35 10 40 18 68 25 S120 44 166 50 S218 55 251 55',
    hidrogel:'M2 14 C35 14 49 16 72 20 S118 34 154 42 S214 51 251 57',
    oscilaciones:'M2 36 C18 0 27 0 41 36 S68 72 83 36 S112 5 129 36 S165 61 183 36 S218 17 251 36',
    sensores:'M2 40 C18 40 18 40 29 40 L47 30 L62 41 L80 37 L100 20 L118 32 L132 18 L156 34 L183 21 L206 33 L251 10'
  };
  const labels={extrusion:'CONTROL DE FLUJO',hidrogel:'BIOMATERIALES',oscilaciones:'DINÁMICA',sensores:'BIOSEÑALES'};
  const images=Object.fromEntries(modules.map(m=>[m.id,`assets/concepto_${m.id}.webp`]));
  const grid=$('#homeCards');
  grid.innerHTML=modules.map(m=>`<button class="moduleCard theme-${m.id}" data-open="${m.id}" aria-label="Abrir módulo ${esc(m.title)}">
    <span class="cardTopline"><span class="moduleNumber">MÓDULO ${m.number}</span><span class="cardSymbol">${m.icon}</span></span>
    <span class="cardVisual"><img src="${images[m.id]}" alt="" loading="lazy" decoding="async" width="768" height="512"><span>ILUSTRACIÓN CONCEPTUAL</span></span>
    <span class="cardDiscipline">${labels[m.id]}</span>
    <h3>${m.title}</h3><p>${m.short}</p>
    <svg class="cardSpark" viewBox="0 0 255 74" aria-hidden="true" preserveAspectRatio="none"><path class="sparkBaseline" d="M0 61H255"/><path class="sparkStroke" d="${paths[m.id]}"/></svg>
    <span class="go">EXPLORAR MÓDULO <b aria-hidden="true">↗</b></span>
  </button>`).join('');
}
function tabs(){let c=$('#moduleTabs');c.innerHTML=modules.map(m=>`<button role="tab" aria-selected="${m.id===state.module}" data-open="${m.id}" class="${m.id===state.module?'active':''}"><span>${m.number}</span>${m.title}</button>`).join('');}
function setConcept(mod){
 const c=conceptInfo[mod];if(!c)return;
 const picture=$('#moduleVisual');picture.src=`assets/concepto_${mod}.webp`;picture.alt=c.alt;
 $('#moduleVisualTitle').textContent=c.title;
 $('#moduleVisualExplain').textContent=c.explain;
 $('#moduleVisualOutput').textContent=c.output;
}
function chooseModule(mod,doRun=true){if(!modules.some(m=>m.id===mod))return;state.runId++;state.module=mod;state.current=null;state.entry=null;$('#saveBtn').disabled=true;const item=modules.find(x=>x.id===mod);$('#modTitle').textContent=item.title;$('#modDescription').textContent=item.desc;setConcept(mod);tabs();buildForm();clearResults();setView('lab');if(doRun)runSimulation();}
function buildForm(values){let p=values||presets[state.scenario][state.module];$('#scenario').value=state.scenario;$('#scenarioHint').textContent=scenarioInfo[state.scenario];$('#paramFields').innerHTML=parameterConfig[state.module].map(([key,label,unit,def,min,max,step])=>`<div class="inputRow"><label for="p_${key}">${esc(label)}<small>${esc(unit)}</small></label><input required id="p_${key}" name="${key}" type="number" min="${min}" max="${max}" step="${step}" value="${p[key]??def}"></div>`).join('');
if(state.module==='sensores'&&state.scenario==='MAL_CONDICIONADO'){$('#scenarioHint').textContent+=' Se usa el benchmark adimensional de Runge; el ruido editable solo se aplica en ESTRÉS.'}}
function readParams(){const obj={};for(const [key] of parameterConfig[state.module]){const e=$(`#p_${key}`),n=Number(e.value);if(!e.value.trim()||!Number.isFinite(n)||!e.checkValidity())throw Error('Valor fuera de rango: '+key);obj[key]=n;}
if(['extrusion','oscilaciones'].includes(state.module)&&obj.n%2!==0)throw Error('Se requiere un número par de subintervalos para Simpson 1/3.');return obj;}
function alertMessage(text,type='error'){$('#alert').textContent=text;$('#alert').classList.toggle('hidden',!text);$('#alert').style.background=type==='ok'?'#edf8ee':'#fceced';$('#alert').style.color=type==='ok'?'#367658':'#8c3038';}
function connectionError(){return 'No se puede conectar con el servidor Python. Si abriste index.html directamente o publicaste solo en GitHub Pages, la API no funciona. Inicia «python app.py» o publica como servicio web Python (Render).';}
async function readJson(res){
 const text=await res.text();let data;
 try{data=JSON.parse(text);}catch(_){throw Error(res.ok?'El servidor devolvió una respuesta inválida.':connectionError()+` (HTTP ${res.status})`);}
 if(!res.ok)throw Error(data.error||`Error HTTP ${res.status}`);
 return data;
}
async function api(path,body){
 let res;try{res=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});}
 catch(_){throw Error(connectionError());}
 return readJson(res);
}
async function getApi(path){let res;try{res=await fetch(path,{cache:'no-store'});}catch(_){throw Error(connectionError());}return readJson(res);}
async function checkBackend(){
 const status=$('#backendStatus');if(!status)return;
 try{const h=await getApi('/api/health');if(h.ok&&h.db==='SQLite'){
  state.backendReady=true;status.textContent='● Servidor Python conectado · SQLite '+(h.persistencia_garantizada?'':'(almacenamiento temporal en este alojamiento)');
  status.className='backendStatus connected';return;
 }throw Error('Servidor no válido');}
 catch(err){state.backendReady=false;status.textContent='⚠ '+connectionError();status.className='backendStatus offline';}
}
async function runSimulation(){
 const id=++state.runId;state.current=null;state.entry=null;$('#saveBtn').disabled=true;
 try{alertMessage('');const p=readParams();const input={case:state.module,scenario:state.scenario,params:p};
 $('#runBtn').disabled=true;$('#runBtn').textContent='Calculando…';
 const result=await api('/api/simulate',input);
 if(id!==state.runId)return; // Evita mostrar resultados de otro módulo al cambiar muy rápido.
 state.current=result;state.entry=input;renderResult(result);$('#saveBtn').disabled=false;
 }catch(err){if(id===state.runId)alertMessage(err.message);}
 finally{if(id===state.runId){$('#runBtn').disabled=false;$('#runBtn').textContent='Calcular simulación';}}
}
function clearResults(){$('#metrics').innerHTML='';$('#methodRows').innerHTML='<tr><td colspan="7" class="muted">Sin simulación.</td></tr>';$('#methodDetails').innerHTML='';$('#numericInterpretation').textContent='Ejecuta primero el experimento.';$('#physicalInterpretation').textContent='Ejecuta primero el experimento.';$('#compareArea').innerHTML='';for(let i=0;i<2;i++){let c=$(`#plot${i}`);c.getContext('2d').clearRect(0,0,c.width,c.height);$(`#legend${i}`).innerHTML='';}}
function makeMetrics(r){let entries=Object.entries(r.reference);const priority=entries.slice(0,3);return priority.map(([key,val])=>`<div class="metric"><span>${esc(key.replaceAll('_',' '))}</span><strong>${typeof val==='number'?fmt(val):Array.isArray(val)?val.length+' valores':esc(String(val).slice(0,28))}</strong><small>Referencia analítica o verificable</small></div>`).join('');}
function renderResult(result){$('#metrics').innerHTML=makeMetrics(result);$('#numericInterpretation').textContent=result.numerical_conclusion;$('#physicalInterpretation').textContent=result.problem_conclusion+' '+result.scenario_note;
let methods=result.methods;$('#methodRows').innerHTML=methods.map((m,i)=>`<tr data-method="${i}" title="Abrir pasos del método"><td><b>${esc(m.method)}</b></td><td>${fmt(m.value)}</td><td>${fmt(m.reference)}</td><td>${fmt(m.error_abs)}</td><td>${m.error_rel_pct===null?'—':fmt(m.error_rel_pct)+'%'}</td><td>${fmt(m.iterations)}</td><td class="${m.converged?'success':'failed'}">${m.converged?'✓ Sí':'! No'}</td></tr>`).join('');
$('#methodDetails').innerHTML='<p class="muted">Selecciona un método para ver la tabla de iteración o refinamiento. En los métodos directos puede no haber pasos iterativos.</p>';
for(let i=0;i<2;i++){const chart=result.charts[i];$(`#chartTitle${i}`).textContent=chart.title;$(`#chartNote${i}`).textContent=`${chart.xLabel} · ${chart.yLabel}`;drawChart($(`#plot${i}`),chart);$(`#legend${i}`).innerHTML=chart.series.map((s,j)=>`<span class="legendItem"><span class="legendLine" style="background:${colors[j%colors.length]}"></span>${esc(s.name)}</span>`).join('');}
}
function showDetails(i){if(!state.current)return;const m=state.current.methods[i];let rows=m.details||[];const count=rows.length;let caption=esc(m.method);let header=rows[0]?.length===3?['Paso / n','Estimación / t','Residual o error']:['Paso','Residuo / dato'];
$('#methodDetails').innerHTML=`<div class="detailsTitle">${caption} · ${count} registros disponibles</div><div class="detailBox">${count?`<table><thead><tr>${header.map(x=>'<th>'+x+'</th>').join('')}</tr></thead><tbody>${rows.slice(0,120).map(row=>'<tr>'+row.map(v=>`<td>${fmt(v)}</td>`).join('')+'</tr>').join('')}</tbody></table>`:'Método directo o sin iteraciones almacenadas.'}</div><p class="muted">Error absoluto = |aproximación − referencia|. El campo residual es matemático en raíces/sistemas lineales; en las EDO se usa un indicador de error frente a la solución exacta.</p>`;
}
function drawChart(canvas,chart){const ctx=canvas.getContext('2d'),W=canvas.width,H=canvas.height;ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
let series=chart.series.filter(s=>s.points?.length);if(!series.length)return;let all=series.flatMap(s=>s.points.filter(p=>p.every(Number.isFinite)));if(!all.length)return;
const xval=p=>p[0];let ymin=Math.min(...all.map(p=>p[1])),ymax=Math.max(...all.map(p=>p[1])),xmin=Math.min(...all.map(xval)),xmax=Math.max(...all.map(xval));const logScale=/Residuo/.test(chart.yLabel)&&ymin>=0;
const ymapVal=v=>logScale?Math.log10(Math.max(v,1e-16)):v;
let ylo=Math.min(...all.map(p=>ymapVal(p[1]))), yhi=Math.max(...all.map(p=>ymapVal(p[1])));
if(Math.abs(xmax-xmin)<1e-12){xmin-=1;xmax+=1}if(yhi-ylo<1e-10){let a=Math.max(1,Math.abs(ylo));ylo-=.12*a;yhi+=.12*a}else{let a=(yhi-ylo)*.09;ylo-=a;yhi+=a}
const ml=75,mr=21,mt=22,mb=43;const sx=x=>ml+(x-xmin)/(xmax-xmin)*(W-ml-mr);const sy=y=>H-mb-(ymapVal(y)-ylo)/(yhi-ylo)*(H-mt-mb);
ctx.font='12px system-ui';ctx.textAlign='right';ctx.strokeStyle='#efeae6';ctx.lineWidth=1;
for(let i=0;i<=5;i++){const value=ylo+(yhi-ylo)*i/5,y=H-mb-i*(H-mt-mb)/5;ctx.beginPath();ctx.moveTo(ml,y);ctx.lineTo(W-mr,y);ctx.stroke();ctx.fillStyle='#827879';ctx.fillText(logScale?'10^'+fmt(value):fmt(value),ml-9,y+4)}ctx.textAlign='center';for(let i=0;i<=5;i++){let x=ml+i*(W-ml-mr)/5;ctx.fillText(fmt(xmin+i*(xmax-xmin)/5),x,H-mb+19)}ctx.strokeStyle='#bdb4b3';ctx.beginPath();ctx.moveTo(ml,mt);ctx.lineTo(ml,H-mb);ctx.lineTo(W-mr,H-mb);ctx.stroke();
series.forEach((s,i)=>{const c=colors[i%colors.length];ctx.strokeStyle=c;ctx.fillStyle=c;ctx.lineWidth=2.2;const points=s.points.filter(p=>p.every(Number.isFinite));ctx.beginPath();points.forEach((p,j)=>{const x=sx(p[0]),y=sy(p[1]);j?ctx.lineTo(x,y):ctx.moveTo(x,y)});if(s.name.toLowerCase().includes('nodos')){points.forEach(p=>{ctx.beginPath();ctx.arc(sx(p[0]),sy(p[1]),4.5,0,Math.PI*2);ctx.fill()});}else{ctx.stroke();if(points.length<=25)points.forEach(p=>{ctx.beginPath();ctx.arc(sx(p[0]),sy(p[1]),2.7,0,Math.PI*2);ctx.fill()});}});
}
async function saveExperiment(){try{if(!state.entry)throw Error('Primero ejecuta la simulación.');const saved=await api('/api/save',state.entry);state.lastSaved=saved.id;alertMessage(`Guardado en SQLite como ejecución #${saved.id}. Puedes recuperarla desde Historial.`, 'ok');}catch(err){alertMessage(err.message);}}
async function listHistory(){const list=$('#historyList');list.innerHTML='<div class="emptyMessage">Cargando historial…</div>';try{const data=await getApi('/api/history');if(!data.items?.length){list.innerHTML='<div class="emptyMessage">Todavía no hay ejecuciones guardadas. Ejecuta un módulo y pulsa «Guardar en SQLite».</div>';return;}
list.innerHTML=data.items.map(x=>{let m=modules.find(z=>z.id===x.caso_id)||modules[0];return `<article class="historyRecord"><div><h3>#${x.id} · ${esc(m.title)}</h3><p>${esc(x.tipo.replace('_',' '))} · ${esc(new Date(x.fecha).toLocaleString('es-BO'))} · Resultado: ${esc(x.sha256_resultado.slice(0,12))}…</p></div><div class="historyActions"><button class="secondary" data-load="${x.id}">Abrir y recuperar</button><button class="secondary" data-replay="${x.id}">Repetir y verificar</button></div></article>`}).join('');}catch(err){list.innerHTML=`<div class="emptyMessage">${esc(err.message)}</div>`;}}
async function loadHistory(id){try{const record=await getApi('/api/history/'+id);state.scenario=record.input.scenario;chooseModule(record.input.case,false);buildForm(record.input.params);state.entry=record.input;state.current=record.result;renderResult(record.result);$('#saveBtn').disabled=false;alertMessage(`Ejecución #${record.id} recuperada con parámetros, datos de métodos y gráficos guardados.`, 'ok');}catch(err){alertMessage(err.message);}}
async function replayHistory(id){try{const response=await api('/api/replay',{id:Number(id)});if(!response.coincide)throw Error('La repetición NO coincide con el SHA-256 guardado.');await loadHistory(id);alertMessage(`Prueba de persistencia aprobada: ejecución #${id} regenerada y SHA-256 idéntico al almacenado.`, 'ok');}catch(err){alertMessage('Prueba de repetición: '+err.message);}}
async function compare(){const box=$('#compareArea');box.innerHTML='<p class="muted">Ejecutando tres escenarios…</p>';try{const sims=await Promise.all(['NORMAL','ESTRES','MAL_CONDICIONADO'].map(async s=>[s,await api('/api/simulate',{case:state.module,scenario:s,params:presets[s][state.module]})]));
const rows=sims.map(([s,r])=>{let m=r.methods.filter(x=>x.converged),best=m.length?m.reduce((a,b)=>a.error_abs<b.error_abs?a:b):null;const ref=Object.entries(r.reference).find(([k,v])=>typeof v==='number');return `<tr><td><b>${esc(s.replaceAll('_',' '))}</b></td><td>${ref?esc(ref[0])+': '+fmt(ref[1]):'—'}</td><td>${best?esc(best.method):'—'}</td><td>${best?fmt(best.error_abs):'—'}</td><td>${r.methods.filter(x=>!x.converged).length}</td></tr>`});
box.innerHTML=`<table><thead><tr><th>Condición</th><th>Referencia</th><th>Menor error absoluto*</th><th>Error</th><th>No convergieron</th></tr></thead><tbody>${rows.join('')}</tbody></table><p class="muted">*Comparación descriptiva dentro de cada grupo de métodos. Los indicadores de distintas familias tienen unidades y significados diferentes; no deben ordenarse entre sí como si midieran lo mismo.</p>`;
}catch(err){box.innerHTML=`<p class="failed">${esc(err.message)}</p>`;}}
document.addEventListener('click',e=>{const tr=e.target.closest('tr[data-method]');if(tr){showDetails(Number(tr.dataset.method));return;}const btn=e.target.closest('button');if(!btn)return;if(btn.dataset.open)chooseModule(btn.dataset.open);else if(btn.dataset.action==='home')setView('home');else if(btn.dataset.action==='lab')chooseModule(state.module);else if(btn.dataset.action==='history')setView('history');else if(btn.dataset.method!==undefined)showDetails(Number(btn.dataset.method));else if(btn.dataset.load)loadHistory(Number(btn.dataset.load));else if(btn.dataset.replay)replayHistory(Number(btn.dataset.replay));else if(btn.closest('tr[data-method]'))showDetails(Number(btn.closest('tr[data-method]').dataset.method));});
$('#parameterForm').addEventListener('submit',e=>{e.preventDefault();runSimulation()});
$('#paramFields').addEventListener('input',()=>{if(state.entry){state.current=null;state.entry=null;$('#saveBtn').disabled=true;alertMessage('Cambiaste parámetros: ejecuta «Calcular simulación» antes de guardar.', 'ok');}});$('#scenario').addEventListener('change',e=>{state.scenario=e.target.value;state.current=null;$('#saveBtn').disabled=true;buildForm();clearResults();runSimulation()});$('#saveBtn').addEventListener('click',saveExperiment);$('#compareBtn').addEventListener('click',compare);$('#refreshHistory').addEventListener('click',listHistory);$('#brandHome').addEventListener('click',e=>{e.preventDefault();setView('home')});homeCards();checkBackend();
