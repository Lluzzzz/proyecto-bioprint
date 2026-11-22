/* Cortes de un hidrogel bioimpreso: representación 2D de solución analítica 1D.
   C(x)=C0 cosh(sqrt(k/D)(L-x)) / cosh(sqrt(k/D)L).
   Un mismo perfil 1D se repite perpendicularmente a 3 microcanales.
   CÉLULAS Y PARTÍCULAS DIBUJADAS SON ILUSTRATIVAS. NO PREDICE VIABILIDAD. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const slider=$('distanceRange'),field=$('oxygenField'),curve=$('oxygenCurve');
  if(!slider||!field||!curve||!window.BioprintOxygen)return;
  const O=window.BioprintOxygen,ctx=field.getContext('2d',{alpha:false}),cctx=curve.getContext('2d');
  const D=.002,k=.04,C0=1,threshold=$('oxygenThreshold'),VIEW_MM=2.4;
  const clamp=(n,a,b)=>Math.min(b,Math.max(a,n));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const W=field.width,H=field.height;
  const refMini=$('oxygenReferenceMini'),currentMini=$('oxygenCurrentMini');
  let mode='gradiente',canvasCache=null,lastDraw=0,visible=true;
  const reduceMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches||false;
  const digits=(x,n=2)=>Number(x).toLocaleString('es-BO',{minimumFractionDigits:n,maximumFractionDigits:n});
  const stops=[[0,[49,44,84]],[.35,[86,61,119]],[.60,[171,83,104]],[.80,[236,157,121]],[1,[252,228,183]]];
  function rgb(c){const value=clamp(c,0,1);for(let i=1;i<stops.length;i++)if(value<=stops[i][0]){
    const [x0,a]=stops[i-1],[x1,b]=stops[i],t=(value-x0)/(x1-x0);
    return a.map((v,j)=>Math.round(lerp(v,b[j],t)));
  }return stops[stops.length-1][1]}
  function prepareCache(){
    const s=Number(slider.value),L=s/2,T=Number(threshold.value),mid=O.cMin(L,D,k,C0);
    const ratio=O.lowFraction(L,T,D,k,C0);
    const off=document.createElement('canvas');off.width=W;off.height=H;
    const layer=off.getContext('2d',{alpha:false});
    const image=layer.createImageData(W,H);
    for(let y=0;y<H;y++){
      const c=O.sectionFixed(y+.5,H,s,VIEW_MM,D,k,C0),cmap=rgb(c);
      // Sin ruido aleatorio: la correspondencia de color se obtiene del modelo analítico.
      for(let x=0;x<W;x++){
        const i=(y*W+x)*4;
        image.data[i]=cmap[0];image.data[i+1]=cmap[1];image.data[i+2]=cmap[2];image.data[i+3]=255;
      }
    }
    layer.putImageData(image,0,0);
    // Estructura visual de fibras del hidrogel, sin alterar la solución numérica.
    layer.strokeStyle='rgba(255,241,224,.09)';layer.lineWidth=1;
    for(let x=15;x<W;x+=32){layer.beginPath();layer.moveTo(x,0);layer.lineTo(x,H);layer.stroke()}
    for(let y=13;y<H;y+=27){layer.beginPath();layer.moveTo(0,y);layer.lineTo(W,y);layer.stroke()}
    canvasCache=off;
    $('oxygenMin').textContent=digits(mid,3);
    $('oxygenLowArea').textContent=digits(ratio*100,1)+' %';
    const baseline=O.cMin(.15,D,k,C0);
    const delta=((mid-baseline)/baseline)*100;
    $('oxygenDelta').textContent=(delta>0?'+':'')+digits(delta,1)+' %';
    $('oxygenDelta').classList.toggle('isLower',delta<-.01);
    const sep=digits(s,2)+' mm';
    $('oxygenDistance').textContent='Separación: '+sep;
    $('rangeValue').textContent=sep;
    $('thresholdValue').textContent=digits(T,2);
    $('oxygenMiniDistance').textContent=sep;
    $('oxygenMiniCurrent').textContent=digits(mid,3);
    drawMini(refMini,.30);drawMini(currentMini,s);
    drawCurve(L,T);
    drawField(performance.now());
  }
  function drawMini(canvas,separation){
    if(!canvas)return;
    const cx=canvas.getContext('2d'),w=canvas.width,h=canvas.height,miniViewMm=1.2;
    const image=cx.createImageData(w,h);
    for(let y=0;y<h;y++){
      const color=rgb(O.sectionFixed(y+.5,h,separation,miniViewMm,D,k,C0));
      for(let x=0;x<w;x++){const i=(y*w+x)*4;image.data[i]=color[0];image.data[i+1]=color[1];image.data[i+2]=color[2];image.data[i+3]=255}
    }
    cx.putImageData(image,0,0);
    for(const proportion of O.channelPositions(separation,miniViewMm)){
      const y=proportion*h;
      cx.strokeStyle='#65324b';cx.lineWidth=7;cx.beginPath();cx.moveTo(0,y);cx.lineTo(w,y);cx.stroke();
      cx.strokeStyle='#e7b49a';cx.lineWidth=2;cx.beginPath();cx.moveTo(0,y);cx.lineTo(w,y);cx.stroke();
    }
  }
  function pathsField(separation){return O.channelPositions(separation,VIEW_MM).map(proportion=>proportion*H)}
  const cells=Array.from({length:480},(_,i)=>{
    const c=i%32,r=Math.floor(i/32);
    const hash=(n)=>{const k=Math.sin(n*82.3181+19.332)*43758.5453;return k-Math.floor(k)};
    return {x:(c+.36+.35*(hash(i*3)-.5))*W/32,
      y:(r+.42+.45*(hash(i*5+4)-.5))*H/15,
      radius:2.8+2.4*hash(i*11+8)};
  });
  function cellsOverlay(L,T){
    ctx.save();
    for(let i=0;i<cells.length;i++){
      const cell=cells[i],c=O.sectionFixed(cell.y,H,L*2,VIEW_MM,D,k,C0),low=c<T;
      const r=cell.radius;
      ctx.strokeStyle=mode==='celulas'?(low?'rgba(85,39,73,.85)':'rgba(255,245,229,.95)'):(low?'rgba(62,43,83,.45)':'rgba(255,244,225,.45)');
      ctx.fillStyle=mode==='celulas'?(low?'rgba(90,43,90,.49)':'rgba(255,234,199,.28)'):(low?'rgba(69,44,87,.21)':'rgba(255,235,210,.14)');
      ctx.lineWidth=mode==='celulas'?1.6:1;
      ctx.beginPath();ctx.ellipse(cell.x,cell.y,r*1.35,r,0,0,Math.PI*2);ctx.fill();ctx.stroke();
      if(mode==='celulas'){
        ctx.fillStyle=low?'rgba(36,20,49,.75)':'rgba(106,69,83,.72)';ctx.beginPath();ctx.arc(cell.x,cell.y,r*.32,0,Math.PI*2);ctx.fill();
      }
    }
    ctx.restore();
  }
  function thresholdLines(L,T){
    const min=O.cMin(L,D,k,C0);
    if(T<=min||T>=C0)return;
    const dcrit=L-Math.acosh((T/C0)*Math.cosh(Math.sqrt(k/D)*L))/Math.sqrt(k/D);
    const separation=2*L;
    ctx.save();ctx.setLineDash([7,6]);ctx.strokeStyle='rgba(255,250,236,.86)';ctx.lineWidth=1.4;
    for(let channel=L;channel<VIEW_MM;channel+=separation){
      for(const side of [-1,1]){
        const mm=channel+side*dcrit,y=mm/VIEW_MM*H;
        if(y<0||y>H)continue;
        ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();
      }
    }
    ctx.restore();
  }
  function drawField(t){
    if(!canvasCache)return;
    const L=Number(slider.value)/2,T=Number(threshold.value);
    ctx.drawImage(canvasCache,0,0);
    cellsOverlay(L,T);
    thresholdLines(L,T);
    const channels=pathsField(2*L);
    channels.forEach((y,j)=>{
      ctx.save();
      ctx.shadowBlur=18;ctx.shadowColor='rgba(47,21,48,.65)';
      ctx.lineWidth=11;ctx.lineCap='round';ctx.strokeStyle='#643049';
      ctx.beginPath();ctx.moveTo(4,y);ctx.lineTo(W-4,y);ctx.stroke();
      ctx.shadowBlur=0;ctx.strokeStyle='#e9b0a3';ctx.lineWidth=4;
      ctx.beginPath();ctx.moveTo(6,y);ctx.lineTo(W-6,y);ctx.stroke();
      ctx.strokeStyle='rgba(255,255,255,.55)';ctx.lineWidth=1.2;
      ctx.beginPath();ctx.moveTo(6,y-3);ctx.lineTo(W-6,y-3);ctx.stroke();
      if(!reduceMotion && visible){
        const speed=(t/15000)%1;
        for(let i=0;i<15;i++){
          const x=(i/15 + speed + j*.08)%1*W;
          ctx.fillStyle='rgba(255,245,215,.9)';ctx.beginPath();ctx.arc(x,y,2.1+(i%3)*.55,0,Math.PI*2);ctx.fill();
        }
      }
      ctx.restore();
    });
    ctx.fillStyle='rgba(35,29,42,.68)';ctx.beginPath();ctx.roundRect(14,12,240,31,8);ctx.fill();
    ctx.fillStyle='#fff1e7';ctx.font='600 13px system-ui';ctx.fillText('Corte de 2,40 mm de hidrogel',25,32);
    ctx.fillStyle='rgba(35,29,42,.65)';ctx.beginPath();ctx.roundRect(W-191,H-43,176,29,7);ctx.fill();
    ctx.fillStyle='#fff1e7';ctx.font='12px system-ui';ctx.fillText('Oxígeno calculado: C(x)',W-181,H-24);
  }
  function drawCurve(L,T){
    const w=curve.width,h=curve.height,padL=42,padR=14,padT=15,padB=30;
    cctx.clearRect(0,0,w,h);
    cctx.fillStyle='#fbf7f3';cctx.fillRect(0,0,w,h);
    const minC=Math.min(O.cMin(L,D,k,C0),T,.3)-.02,ymin=clamp(minC,.2,.95),ymax=1.05;
    const sx=x=>padL+(x/L)*(w-padL-padR),sy=c=>h-padB-(c-ymin)/(ymax-ymin)*(h-padT-padB);
    cctx.strokeStyle='#e7ddd5';cctx.lineWidth=1;cctx.font='10px system-ui';cctx.textAlign='right';cctx.fillStyle='#6c6162';
    for(let i=0;i<=3;i++){const c=ymin+(ymax-ymin)*i/3,y=sy(c);cctx.beginPath();cctx.moveTo(padL,y);cctx.lineTo(w-padR,y);cctx.stroke();cctx.fillText(digits(c,2),padL-5,y+3)}
    const thresholdY=sy(T);if(thresholdY>=padT&&thresholdY<=h-padB){cctx.setLineDash([5,4]);cctx.strokeStyle='#a66c85';cctx.beginPath();cctx.moveTo(padL,thresholdY);cctx.lineTo(w-padR,thresholdY);cctx.stroke();cctx.setLineDash([])}
    const pts=Array.from({length:121},(_,i)=>{const x=L*i/120;return [sx(x),sy(O.conc(x,L,D,k,C0))]});
    cctx.strokeStyle='#713849';cctx.lineWidth=3;cctx.beginPath();pts.forEach((p,i)=>i?cctx.lineTo(...p):cctx.moveTo(...p));cctx.stroke();
    cctx.fillStyle='#713849';cctx.beginPath();cctx.arc(...pts[pts.length-1],4.2,0,2*Math.PI);cctx.fill();
    cctx.textAlign='center';cctx.fillStyle='#6c6162';cctx.font='11px system-ui';
    cctx.fillText('Canal',padL,h-12);cctx.fillText('Plano medio',w-padR-25,h-12);
  }
  function update(){prepareCache()}
  slider.addEventListener('input',update);
  threshold.addEventListener('input',update);
  $('showHeatmap').addEventListener('click',()=>{mode='gradiente';setMode()});
  $('showCells').addEventListener('click',()=>{mode='celulas';setMode()});
  function setMode(){for(const [id,name] of [['showHeatmap','gradiente'],['showCells','celulas']]){
    const active=name===mode;$(id).classList.toggle('active',active);$(id).setAttribute('aria-pressed',String(active));
  }drawField(performance.now())}
  const open=$('openSensors');if(open)open.addEventListener('click',()=>{
    const card=document.querySelector('[data-open="sensores"]');if(card)card.click();
  });
  const home=$('home');if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>{visible=entries.some(e=>e.isIntersecting);if(visible)drawField(performance.now())},{threshold:0.02});observer.observe(home);
  }
  function animate(t){if(visible && !reduceMotion && t-lastDraw>55){drawField(t);lastDraw=t}
    requestAnimationFrame(animate);
  }
  update();if(!reduceMotion)requestAnimationFrame(animate);
})();
