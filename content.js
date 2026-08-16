
(() => {
  const STYLE = `
    #webguard-topbar{position:fixed;top:0;left:0;right:0;z-index:2147483647;padding:12px 20px;font-family:Inter,system-ui;display:flex;justify-content:space-between;align-items:center;backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,255,255,.1);transform:translateY(-100%);transition:transform .5s cubic-bezier(.16,1,.3,1);}
    #webguard-topbar.show{transform:translateY(0);}
    #webguard-blur-overlay{position:fixed;inset:0;z-index:2147483646;background:rgba(10,14,26,.85);backdrop-filter:blur(24px);display:flex;align-items:center;justify-content:center;flex-direction:column;color:white;font-family:Inter;text-align:center;padding:30px;}
    .webguard-img-blur{filter:blur(22px) brightness(.7) !important;transition:.3s;}
  `;
  const styleEl=document.createElement('style'); styleEl.textContent=STYLE; document.documentElement.appendChild(styleEl);
  function createTopBar(data){
    const ex=document.getElementById('webguard-topbar'); if(ex) ex.remove();
    const bar=document.createElement('div'); bar.id='webguard-topbar';
    const color=data.verdict==='RED'?'#ef4444':data.verdict==='YELLOW'?'#f59e0b':'#10b981';
    const bg=data.verdict==='RED'?'rgba(239,68,68,.15)':data.verdict==='YELLOW'?'rgba(245,158,11,.15)':'rgba(16,185,129,.15)';
    bar.style.background=bg; bar.style.color=color;
    bar.innerHTML=`<div style="display:flex;align-items:center;gap:10px;font-weight:700;"><span style="background:${color};color:white;padding:4px 8px;border-radius:999px;font-size:11px;">${data.verdict} ${data.trust}/100</span><span style="font-size:13px;color:white;">WebGuard: ${data.verdict==='GREEN'?'Safe hai':'Khatarnak!'} - ${data.reasons[0]}</span></div><div style="display:flex;gap:8px;"><button id="wg-close" style="background:rgba(255,255,255,.1);color:white;border:0;padding:6px 10px;border-radius:8px;cursor:pointer;">X</button></div>`;
    document.documentElement.appendChild(bar);
    requestAnimationFrame(()=> setTimeout(()=> bar.classList.add('show'), 300));
    document.getElementById('wg-close').onclick=()=> bar.classList.remove('show');
    setTimeout(()=>{ bar.classList.remove('show'); }, 8000);
  }
  function createBlock(type,data){
    const over=document.createElement('div'); over.id='webguard-blur-overlay';
    const isAdult=type==='adult';
    over.innerHTML=`<div style="font-size:64px;">${isAdult?'🔞':'🎰'}</div><h1 style="font-size:32px;font-weight:900;margin:12px 0;">${isAdult?'Adult Content Blocked':'Betting Blocked'}</h1><p style="opacity:.7;max-width:520px;">Score: ${data.trust}/100 - ${data.reasons[0]}</p><div style="display:flex;gap:12px;margin-top:20px;"><button id="wg-back" style="background:white;color:black;padding:10px 18px;border-radius:10px;font-weight:700;border:0;cursor:pointer;">Go Back Safe</button><button id="wg-cont" style="background:rgba(255,255,255,.1);color:white;padding:10px 18px;border-radius:10px;border:0;cursor:pointer;">Continue Anyway</button></div>`;
    document.documentElement.appendChild(over);
    document.getElementById('wg-back').onclick=()=> history.back();
    document.getElementById('wg-cont').onclick=()=> over.remove();
  }
  function blurImgs(data){
    if(!data.all.adult.flag) return;
    document.querySelectorAll('img,video').forEach(el=>{
      el.classList.add('webguard-img-blur');
      el.addEventListener('click', (e)=>{
        e.preventDefault();
        if(confirm('Adult content - WebGuard blurred. Show?')) el.classList.remove('webguard-img-blur');
      });
    });
  }
  async function analyze(){
    const txt=document.body?document.body.innerText.slice(0,6000):'';
    const imgCount=document.images?document.images.length:0;
    chrome.runtime.sendMessage({type:"ANALYZE", url: location.href, pageText: txt, imgCount}, (data)=>{
      if(!data) return;
      createTopBar(data);
      if(data.all.adult.flag){
        blurImgs(data);
        if(data.all.adult.score>=35) createBlock('adult', data);
      }
      if(data.all.betting.flag && data.all.betting.score>=25) createBlock('betting', data);
      chrome.storage.local.set({lastScan:data, lastUrl:location.href});
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', analyze);
  else analyze();
})();
