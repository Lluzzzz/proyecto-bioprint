/* Modelo analítico y estadísticas de una franja 1D entre microcanales ideales.
 * -D C'' + k C = 0, C(0)=C0 y C'(L)=0, L = separación / 2.
 * En el mapa 2D solo se repite periódicamente esta solución 1D; NO es PDE 2D.
 * Las regiones por debajo de un umbral son EXPLORATORIAS, no viabilidad celular. */
(function (root) {
  'use strict';
  const O={};
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  function valid(L,D,k,C0){
    if (![L,D,k,C0].every(Number.isFinite) || L<=0 || D<=0 || k<0 || C0<=0) throw new Error('Parámetros no físicos para la simulación.');
  }
  function conc(x,L,D=0.002,k=0.04,C0=1){
    valid(L,D,k,C0); const dist=clamp(x,0,L),eta=Math.sqrt(k/D);
    if (eta===0) return C0;
    // Los controles mantienen eta L bajo para estabilidad de cosh.
    return C0*Math.cosh(eta*(L-dist))/Math.cosh(eta*L);
  }
  function cMin(L,D=0.002,k=0.04,C0=1){return conc(L,L,D,k,C0)}
  // Fracción de la sección simétrica con C(x)< umbral, sin incluir los canales.
  function lowFraction(L,threshold,D=0.002,k=0.04,C0=1){
    valid(L,D,k,C0);
    if(!Number.isFinite(threshold))throw new Error('Umbral no válido');
    const min=cMin(L,D,k,C0);
    if(threshold<=min) return 0;
    if(threshold>=C0) return 1;
    const eta=Math.sqrt(k/D);
    if(eta<1e-14)return 0;
    const boundary=L-Math.acosh((threshold/C0)*Math.cosh(eta*L))/eta;
    return clamp((L-boundary)/L,0,1);
  }
  // Concentración en sección transversal repetida con canales en h/6, h/2, 5h/6.
  // La mitad de la distancia entre dos canales representa L: exactamente el punto medio C(L).
  function sectionAt(y,height,L,D=0.002,k=0.04,C0=1){
    const yy=clamp(y,0,height),half=height/6;
    const dy=Math.min(Math.abs(yy-half),Math.abs(yy-3*half),Math.abs(yy-5*half));
    return conc(L*clamp(dy/half,0,1),L,D,k,C0);
  }
  // Campo periódico en una ventana de altura física FIJA. A medida que la separación crece,
  // disminuye la cantidad de canales que aparece en el mismo recorte.
  function sectionFixed(y,height,separationMM,viewHeightMM=2.4,D=0.002,k=0.04,C0=1){
    const L=separationMM/2;
    valid(L,D,k,C0);
    if(!Number.isFinite(viewHeightMM)||viewHeightMM<=0||height<=0)throw Error('Altura inválida');
    const phys=clamp(y,0,height)/height*viewHeightMM;
    const phase=phys%separationMM;
    const distance=Math.abs(phase-L);
    return conc(distance,L,D,k,C0);
  }
  // Las líneas se ubican en los centros físicos de las celdas periódicas.
  function channelPositions(separationMM,viewHeightMM=2.4){
    if(!(separationMM>0&&viewHeightMM>0))throw Error('Distancia inválida');
    const vals=[];
    for(let y=separationMM/2;y<viewHeightMM;y+=separationMM)vals.push(y/viewHeightMM);
    return vals;
  }
  Object.assign(O,{conc,cMin,lowFraction,sectionAt,sectionFixed,channelPositions});
  root.BioprintOxygen=O;
  if(typeof module!=='undefined'&&module.exports)module.exports=O;
})(typeof window!=='undefined'?window:globalThis);
