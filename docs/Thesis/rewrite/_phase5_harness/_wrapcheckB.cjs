
const fs=require('fs');
let src=fs.readFileSync(process.argv[1],'utf8').replace('export const meta','const meta');
try { new Function('agent','parallel','pipeline','log','phase','args','budget','workflow','(async()=>{'+src+'})');
  console.log('[ok] syntax wrap-check passed'); }
catch(e){ console.error('[FAIL] syntax: '+e.message); process.exit(1); }
