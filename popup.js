
function render(data){
  const circle=document.getElementById('circle');
  const color=data.verdict==='RED'?'#ef4444':data.verdict==='YELLOW'?'#f59e0b':'#10b981';
  circle.style.borderColor=color; circle.style.color=color; circle.textContent=data.trust;
  document.getElementById('verdict').textContent=data.verdict+' - '+data.trust+'/100';
  document.getElementById('verdict').style.color=color;
  document.getElementById('mainReason').textContent=data.reasons[0];
  document.getElementById('reasons').innerHTML=data.reasons.map(r=>'• '+r).join('<br>');
  const engDiv=document.getElementById('engines');
  engDiv.innerHTML='';
  Object.entries(data.all).forEach(([k,v])=>{
    const d=document.createElement('div');
    d.className='bg-black/40 rounded-lg p-1.5 text-center';
    d.innerHTML=`<div class="text-[9px] opacity-50 uppercase">${k}</div><div class="text-[11px] font-bold" style="color:${v.score>20?'#ef4444':'#10b981'}">${v.score}</div>`;
    engDiv.appendChild(d);
  });
}
async function scan(){
  const [tab]=await chrome.tabs.query({active:true, currentWindow:true});
  const result=await chrome.storage.local.get(['lastScan','lastUrl']);
  if(result.lastScan && result.lastUrl===tab.url){ render(result.lastScan); return; }
  setTimeout(async()=>{
    const r=await chrome.storage.local.get(['lastScan']); if(r.lastScan) render(r.lastScan);
  }, 800);
}
document.getElementById('rescan').onclick=async()=>{
  const [tab]=await chrome.tabs.query({active:true, currentWindow:true});
  chrome.tabs.reload(tab.id);
  window.close();
};
document.getElementById('report').onclick=async()=>{
  const [tab]=await chrome.tabs.query({active:true, currentWindow:true});
  alert('1930 Report Ready\nURL: '+tab.url);
};
scan();
