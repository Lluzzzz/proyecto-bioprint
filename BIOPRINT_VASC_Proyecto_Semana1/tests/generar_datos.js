const fs=require('fs');const m=require('../src/motor.js');
const data={proyecto:'BIOPRINT-VASC S1',fecha:'2026-11',fuente:'parámetros sintéticos académicos',escenarios:{}};
for(const scenario of ['NORMAL','ESTRES','MAL_CONDICIONADO']){
 const p={L:scenario==='ESTRES'?.4:.15,D:.002,k:.04,C0:1,N:4,tol:1e-11};
 data.escenarios[scenario]=m.run(p,scenario);
}
fs.writeFileSync(require('path').join(__dirname,'..','docs','resultados_prueba.json'),JSON.stringify(data,null,2));
console.log('Resultados de referencia generados.');
