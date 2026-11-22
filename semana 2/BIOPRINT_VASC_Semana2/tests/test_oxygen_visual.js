'use strict';
const assert=require('node:assert/strict');
const O=require('../src/oxygen_model.js');
const D=.002,k=.04;
const approx=(got,want,tol=1e-10)=>assert(Math.abs(got-want)<=tol,`${got} !== ${want}`);
for(const L of [.10,.15,.2,.3,.4]){
  approx(O.conc(0,L,D,k),1);
  approx(O.conc(L,L,D,k),1/Math.cosh(Math.sqrt(k/D)*L));
  approx(O.sectionAt(0,360,L,D,k),O.cMin(L,D,k));
  approx(O.sectionAt(60,360,L,D,k),1);
  approx(O.sectionAt(120,360,L,D,k),O.cMin(L,D,k));
  approx(O.sectionAt(180,360,L,D,k),1);
  approx(O.sectionAt(240,360,L,D,k),O.cMin(L,D,k));
  approx(O.sectionAt(300,360,L,D,k),1);
  approx(O.sectionAt(360,360,L,D,k),O.cMin(L,D,k));
  const T=.6,low=O.lowFraction(L,T,D,k);
  // Independent quadrature: fraction from sampled (spatial, not cellular) points.
  const N=30001;
  const approxFraction=Array.from({length:N},(_,i)=>O.conc(L*i/(N-1),L,D,k)<T?1:0).reduce((a,b)=>a+b,0)/N;
  assert(Math.abs(low-approxFraction)<2/N,`${L}, lowFrac=${low}, grid=${approxFraction}`);
}
assert(O.cMin(.4,D,k)<O.cMin(.15,D,k));
approx(O.cMin(.15,D,k),.8106584828525429,1e-9);
approx(O.cMin(.4,D,k),.32521666668732585,1e-9);
for(const L of [.15,.4]){
  approx(O.lowFraction(L,0),0);
  approx(O.lowFraction(L,1),1);
  approx(O.cMin(L,D,0),1);
}
console.log('OK: continuidad analítica, frontera de canal, simetría, campo periódico y porcentaje umbral validado.');
