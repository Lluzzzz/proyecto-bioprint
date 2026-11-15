'use strict';
const $=id=>document.getElementById(id), M=BioMotor;
const presets={
 NORMAL:{L:.15,D:.002,k:.04,C0:1,N:4,tol:1e-11},
 ESTRES:{L:.4,D:.002,k:.04,C0:1,N:4,tol:1e-11},
 MAL_CONDICIONADO:{L:.15,D:.002,k:.04,C0:1,N:4,tol:1e-11}
};
const hints={
 NORMAL:'Normal: configuración sintética base. La separación equivalente entre canales es 2L = 0,30 mm.',
 ESTRES:'Estrés: la semidistancia aumenta a L = 0,40 mm, manteniendo D y k. El centro queda más lejos del canal.',
 MAL_CONDICIONADO:'Mal condicionado: misma física del caso normal, pero se aplica A′ = S A S, b′ = S b y C = S y, con S = diag(1; 0,05; 0,005; 1).'
};
let latest;
const sci=v=>Number.isFinite(v)?v.toExponential(3):'—';
const decimal=(v,d=6)=>Number.isFinite(v)?v.toFixed(d):'—';
function getParams(){return {L:Number($('L').value),D:Number($('D').value),k:Number($('k').value),C0:Number($('C0').value),N:Number($('N').value),tol:Number($('tol').value)};}
function resetScenario(s){for(const [key,val] of Object.entries(presets[s]))$(key).value=val;$('sceneHint').textContent=hints[s];}
function axes(canvas,xmax,yMin,yMax,xLabel,yLabel,{log=false}={}){
 const ctx=canvas.getContext('2d');const w=canvas.width,h=canvas.height;
 ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);
 const l=70,r=w-32,t=25,b=h-55;
 ctx.font='12px Arial';ctx.lineWidth=1;
 for(let i=0;i<=5;i++){
  const x=l+i*(r-l)/5,y=b-i*(b-t)/5;
  ctx.strokeStyle='#ede8e4';ctx.beginPath();ctx.moveTo(l,y);ctx.lineTo(r,y);ctx.stroke();
  ctx.fillStyle='#6b7477';ctx.fillText((yMin+(yMax-yMin)*i/5).toFixed(log?0:2),10,y+4);
  ctx.fillText((xmax*i/5).toFixed(xmax<2?2:0),x-11,h-30);
 }
 ctx.fillStyle='#6b7477';ctx.fillText(xLabel,(l+r)/2-60,h-5);
 ctx.save();ctx.translate(19,(t+b)/2+50);ctx.rotate(-Math.PI/2);ctx.fillText(yLabel,0,0);ctx.restore();
 const X=x=>l+x/xmax*(r-l);
 const Y=y=>b-(y-yMin)/(yMax-yMin)*(b-t);
 return {ctx,X,Y,l,r,t,b};
}
function drawProfile(res){
 const p=res.p,{ctx,X,Y}=axes($('profileChart'),p.L,0,1.05,'Distancia x (mm)','Concentración normalizada');
 ctx.beginPath();for(let i=0;i<=120;i++){const x=i*p.L/120,y=M.exact(p,x);i===0?ctx.moveTo(X(x),Y(y)):ctx.lineTo(X(x),Y(y));}
 ctx.strokeStyle='#783b45';ctx.lineWidth=3;ctx.stroke();
 res.x.forEach((x,i)=>{ctx.beginPath();ctx.fillStyle='#bd8a51';ctx.arc(X(x),Y(res.profile[i]),4.8,0,Math.PI*2);ctx.fill();ctx.strokeStyle='white';ctx.lineWidth=1;ctx.stroke();});
}
function drawError(res){
 const keys=['Jacobi','Gauss-Seidel','Gradiente conjugado'];
 const count=Math.max(...keys.map(k=>res.methods[k].history.length),2);
 const plot=axes($('errorChart'),count,-14,1,'Iteraciones','log₁₀ del residuo',{log:true});
 const {ctx,X,Y}=plot;
 const colors=['#8b4550','#bd8a51','#427e70'];
 keys.forEach((k,i)=>{
  const h=res.methods[k].history;
  ctx.beginPath();h.forEach((v,j)=>{const xx=X(j+1),yy=Y(Math.max(-14,Math.log10(Math.max(v,1e-14))));j===0?ctx.moveTo(xx,yy):ctx.lineTo(xx,yy)});
  ctx.lineWidth=2.5;ctx.strokeStyle=colors[i];ctx.stroke();
  ctx.fillStyle=colors[i];ctx.fillRect(plot.r-205,plot.t+7+i*20,16,3);ctx.fillStyle='#56666b';ctx.font='12px Arial';ctx.fillText(k,plot.r-181,plot.t+12+i*20);
 });
}
function execute(){
 try{
  $('errorMessage').textContent='';const p=getParams(),s=$('scenario').value;
  latest=M.run(p,s);const r=latest;
  $('cmin').textContent=decimal(r.minExact,6);$('meshError').textContent=sci(r.gridError);$('condition').textContent=sci(r.condition);
  $('methodRows').innerHTML=Object.entries(r.methods).map(([k,m])=>`<tr><td><b>${k}</b></td><td>${m.iterations||'—'}</td><td class="${m.converged?'good':'bad'}">${m.converged?'Sí':'No'}</td><td>${sci(m.residual)}</td><td>${sci(m.absoluteError)}</td><td>${sci(m.percentError)} %</td></tr>`).join('');
  const all=['Jacobi','Gauss-Seidel','Gradiente conjugado'];
  $('iterationRows').innerHTML=Array.from({length:5},(_,i)=>`<tr><td>${i+1}</td>${all.map(k=>`<td>${r.methods[k].history[i]===undefined?'—':sci(r.methods[k].history[i])}</td>`).join('')}</tr>`).join('');
  const n=Math.min(p.N,7);
  $('matrixPrint').textContent=`A (primeras ${n} filas, hasta ${n} columnas):\n`+r.A.slice(0,n).map(row=>row.slice(0,n).map(v=>v.toFixed(5).padStart(10)).join(' ')).join('\n')+'\n\nb (primeros valores): '+r.b.slice(0,n).map(v=>v.toFixed(5)).join(', ');
  const badd=s==='MAL_CONDICIONADO';
  $('interpretation').textContent=badd?
   `Interpretación numérica: la transformación de variables hace más sensible el sistema (κ∞ = ${sci(r.condition)}), pero el perfil físico recuperado sigue siendo el del caso normal. Amplificación observada en la prueba de perturbación sintética: ${decimal(r.amplification,3)}. Un sistema mal condicionado no equivale a una condición de salud peligrosa.`:
   `Interpretación del modelo: para L=${decimal(p.L,2)} mm, la concentración exacta en la posición más alejada del canal es ${decimal(r.minExact,6)}. Este es un resultado de un modelo educativo idealizado: no permite asegurar supervivencia celular o vascularización funcional.`;
  drawProfile(r);drawError(r);
 }catch(error){latest=null;$('errorMessage').textContent=error.message;}
}
function compare(){
 const out=Object.entries(presets).map(([key,p])=>{
  const r=M.run(p,key);return `<tr><td>${key.replace('_',' ')}</td><td>${decimal(r.minExact,6)}</td><td>${sci(r.condition)}</td><td>${r.methods.Jacobi.iterations}</td><td>${r.methods['Gradiente conjugado'].iterations}</td><td>${sci(r.gridError)}</td></tr>`;
 });
 $('compareRows').innerHTML=out.join('');
}
function exportJSON(){
 if(!latest){$('errorMessage').textContent='Ejecuta un experimento antes de exportar.';return;}
 const payload={proyecto:'BIOPRINT-VASC',nivel:'Semana 1',fecha:new Date().toISOString(),nota:'Datos sintéticos sin uso clínico',...latest};
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob);
 const a=document.createElement('a');a.href=url;a.download=`BIOPRINT_${latest.scenario}_${Date.now()}.json`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
}
$('scenario').addEventListener('change',()=>{resetScenario($('scenario').value);execute()});
$('calculate').addEventListener('click',execute);
$('compare').addEventListener('click',compare);
$('export').addEventListener('click',exportJSON);
execute();
