const assert=require('node:assert/strict');
const m=require('../src/motor.js');
for(const s of ['NORMAL','ESTRES','MAL_CONDICIONADO']){
 const p={L:s==='ESTRES'?.4:.15,D:.002,k:.04,C0:1,N:4,tol:1e-11};
 const r=m.run(p,s);
 for(const [method,val] of Object.entries(r.methods)){
  assert(val.converged,`${s}/${method} no converge`);
  assert(val.residual/m.norm(r.b)<1.1e-11,`${s}/${method} residual: ${val.residual}`);
  assert(val.absoluteError<1e-8,`${s}/${method} error: ${val.absoluteError}`);
 }
 assert(r.condition>1);
 console.log(s,'Cmin',r.minExact,'k∞',r.condition,'error_malla',r.gridError);
}
// Solución fabricada de 4 incógnitas: valida el solucionador con una x* conocida.
const p={L:.15,D:.002,k:.04,C0:1,N:4,tol:1e-11};
const A=m.assemble(p).A;const expected=[.2,.4,.6,.8];const b=A.map(row=>m.dot(row,expected));
const x=m.solveDirect(A,b);assert(x.every((v,i)=>Math.abs(v-expected[i])<1e-12));
// Caso k=0: perfil espacial constante C(x)=C0.
const z=m.run({...p,k:0},'NORMAL');assert(z.profile.every(v=>Math.abs(v-1)<1e-11));
// Condicionamiento: perfil físico igual tras reescalamiento, mayor k∞.
const n=m.run(p,'NORMAL'),bad=m.run(p,'MAL_CONDICIONADO');
assert(n.profile.every((v,i)=>Math.abs(v-bad.profile[i])<1e-9));
assert(bad.condition>1e3*n.condition);
// Refinamiento de malla: converge hacia solución analítica.
const errors=[];
for(const N of [4,8,16,32])errors.push(m.run({...p,L:.4,N},'ESTRES').gridError);
assert(errors.every((v,i)=>i===0||v<errors[i-1]),String(errors));
// Validación de entradas.
assert.throws(()=>m.run({...p,N:3},'NORMAL'));
console.log('PRUEBAS SUPERADAS: 3 escenarios, 5 métodos, referencia, k=0, SPD, sensibilidad y refinamiento.');
