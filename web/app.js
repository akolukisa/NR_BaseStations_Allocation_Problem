const map = L.map('map').setView([38.43, 27.20], 11)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map)
const layerGroup = L.layerGroup().addTo(map)
const ueLayer = L.layerGroup().addTo(map)
let resultsData = null
const state = { users: 10, beams: 8, sites: null }
const colors = ['#ef4444','#22c55e','#3b82f6']
function deg2rad(d){return d*Math.PI/180}
function sectorPolygon(lat, lon, centerDeg, radiusM){
  const latR = lat
  const start = centerDeg - 60
  const end = centerDeg + 60
  const step = 5
  const pts = [[lat, lon]]
  for(let a=start;a<=end;a+=step){
    const r = deg2rad(a)
    const dLat = (radiusM*Math.cos(r))/111320
    const dLon = (radiusM*Math.sin(r))/(111320*Math.cos(deg2rad(latR)))
    pts.push([lat + dLat, lon + dLon])
  }
  pts.push([lat, lon])
  return pts
}
function drawSites(sites){
  layerGroup.clearLayers()
  ueLayer.clearLayers()
  sites.forEach((s,j)=>{
    L.circleMarker([s.lat, s.lon], { radius: 6, color: '#f59e0b' }).addTo(layerGroup)
    s.sectors.forEach((az,idx)=>{
      const poly = L.polygon(sectorPolygon(s.lat, s.lon, az, 600), { color: colors[idx%colors.length], weight: 1, fillOpacity: 0.2 })
      poly.addTo(layerGroup)
    })
  })
}
function drawUEs(ue){
  ueLayer.clearLayers()
  ue.forEach(u=>{
    L.circleMarker([u.lat, u.lon], { radius: 3, color: '#fbbf24', opacity: 0.9 }).addTo(ueLayer)
  })
}
function buildControls(sites){
  const controls = document.getElementById('controls')
  const row = document.createElement('div')
  row.style.display = 'flex'
  row.style.gap = '8px'
  const selUsers = document.createElement('select')
  for(let u=10;u<=100;u+=10){ const opt=document.createElement('option'); opt.value=u; opt.textContent=`Users ${u}`; selUsers.appendChild(opt) }
  selUsers.value = state.users
  selUsers.onchange = ()=>{ state.users = parseInt(selUsers.value,10); loadScenario() }
  const selBeams = document.createElement('select')
  ;[8,16].forEach(b=>{ const opt=document.createElement('option'); opt.value=b; opt.textContent=`Beams ${b}`; selBeams.appendChild(opt) })
  selBeams.value = state.beams
  selBeams.onchange = ()=>{ state.beams = parseInt(selBeams.value,10); loadScenario() }
  const runBtn = document.createElement('button')
  runBtn.textContent = 'Run'
  runBtn.onclick = ()=>{ loadResults(); loadComparison(); loadNrFlows(); loadProgress(); loadPositions() }
  const rndBtn = document.createElement('button')
  rndBtn.textContent = 'Rastgele sahalar'
  rndBtn.onclick = ()=>{ 
    const c = map.getCenter(); 
    const generated = generateRandomSites(sites.length, c.lat, c.lng);
    state.sites = generated;
    drawSites(state.sites);
  }
  const fitBtn = document.createElement('button')
  fitBtn.className = 'secondary'
  fitBtn.textContent = 'Tüm sahaları göster'
  fitBtn.onclick = ()=>{
    const bounds = L.latLngBounds([])
    const arr = state.sites || sites
    arr.forEach(s=>bounds.extend([s.lat, s.lon]))
    map.fitBounds(bounds.pad(0.2))
  }
  row.appendChild(selUsers)
  row.appendChild(selBeams)
  row.appendChild(runBtn)
  row.appendChild(rndBtn)
  row.appendChild(fitBtn)
  controls.appendChild(row)
}
function loadResults(){
  const el = document.getElementById('results')
  const path = `../results/sample_u${state.users}_b${state.beams}.csv`
  fetch(path).then(r=>{
    if(!r.ok) throw new Error('no results')
    return r.text()
  }).then(txt=>{
    const rows = txt.trim().split('\n').slice(1).map(l=>l.split(','))
    resultsData = rows
    const total = rows.reduce((a,r)=>a+parseFloat(r[3]),0)
    const denom = rows.length? (rows.length * rows.reduce((a,r)=>{const b=parseFloat(r[3]);return a+b*b},0)) : 0
    const jain = denom? (total*total)/denom : 0
    const summary = document.getElementById('metrics')
    summary.innerHTML = `<div class="metrics"><span class="metric">Toplam: ${(total/1e6).toFixed(2)} Mbps</span><span class="metric">Jain: ${jain.toFixed(2)}</span></div>`
    const table = document.createElement('table')
    const thead = document.createElement('thead')
    const trh = document.createElement('tr')
    ;['Kullanıcı','gNB','Beam','Mbps'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
    thead.appendChild(trh)
    table.appendChild(thead)
    const tbody = document.createElement('tbody')
    rows.forEach(r=>{
      const tr=document.createElement('tr')
      r.forEach((v,idx)=>{const td=document.createElement('td');td.textContent= idx===3 ? (parseFloat(v)/1e6).toFixed(2) : v;tr.appendChild(td)})
      tbody.appendChild(tr)
    })
    table.appendChild(tbody)
    el.innerHTML = ''
    el.appendChild(table)
  }).catch(()=>{
    fetch('../results/sample.csv').then(r=>r.text()).then(txt=>{
      const rows = txt.trim().split('\n').slice(1).map(l=>l.split(','))
      resultsData = rows
      const total = rows.reduce((a,r)=>a+parseFloat(r[3]),0)
      const denom = rows.length? (rows.length * rows.reduce((a,r)=>{const b=parseFloat(r[3]);return a+b*b},0)) : 0
      const jain = denom? (total*total)/denom : 0
      const summary = document.getElementById('metrics')
      summary.innerHTML = `<div class="metrics"><span class="metric">Toplam: ${(total/1e6).toFixed(2)} Mbps</span><span class="metric">Jain: ${jain.toFixed(2)}</span></div>`
      const table = document.createElement('table')
      const thead = document.createElement('thead')
      const trh = document.createElement('tr')
      ;['Kullanıcı','gNB','Beam','Mbps'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
      thead.appendChild(trh)
      table.appendChild(thead)
      const tbody = document.createElement('tbody')
      rows.forEach(r=>{
        const tr=document.createElement('tr')
        r.forEach((v,idx)=>{const td=document.createElement('td');td.textContent= idx===3 ? (parseFloat(v)/1e6).toFixed(2) : v;tr.appendChild(td)})
        tbody.appendChild(tr)
      })
      table.appendChild(tbody)
      el.innerHTML = ''
      el.appendChild(table)
    }).catch(()=>{ el.textContent = 'Sonuç dosyası yok.' })
  })
}
function loadNrFlows(){
  const el = document.getElementById('nr')
  const path = `../results/nr_demo_u${state.users}_b${state.beams}.csv?v=${Date.now()}`
  fetch(path).then(r=>{
    if(!r.ok) throw new Error('no flows')
    return r.text()
  }).then(txt=>{
    const rows = txt.trim().split('\n').slice(1).map(l=>l.split(','))
    const total = rows.reduce((a,r)=>a+parseFloat(r[1]),0)
    const denom = rows.length? (rows.length * rows.reduce((a,r)=>{const b=parseFloat(r[1]);return a+b*b},0)) : 0
    const jain = denom? (total*total)/denom : 0
    const info = document.createElement('div')
    info.textContent = `Akış sayısı: ${rows.length} • Toplam: ${total.toFixed(2)} Mbps • Jain: ${jain.toFixed(2)}`
    const table = document.createElement('table')
    const thead = document.createElement('thead')
    const trh = document.createElement('tr')
    ;['Flow','Mbps','Delay (ms)','Jitter (ms)'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
    thead.appendChild(trh)
    table.appendChild(thead)
    const tbody = document.createElement('tbody')
    rows.forEach(r=>{
      const tr=document.createElement('tr')
      r.forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)})
      tbody.appendChild(tr)
    })
    table.appendChild(tbody)
    el.innerHTML = ''
    el.appendChild(info)
    el.appendChild(table)
  }).catch(()=>{
    fetch('../results/nr_demo/flows.csv?v=' + Date.now()).then(r=>{
      if(!r.ok) throw new Error('no flows')
      return r.text()
    }).then(txt=>{
      const rows = txt.trim().split('\n').slice(1).map(l=>l.split(','))
      const total = rows.reduce((a,r)=>a+parseFloat(r[1]),0)
      const denom = rows.length? (rows.length * rows.reduce((a,r)=>{const b=parseFloat(r[1]);return a+b*b},0)) : 0
      const jain = denom? (total*total)/denom : 0
      const info = document.createElement('div')
      info.textContent = `Akış sayısı: ${rows.length} • Toplam: ${total.toFixed(2)} Mbps • Jain: ${jain.toFixed(2)}`
      const table = document.createElement('table')
      const thead = document.createElement('thead')
      const trh = document.createElement('tr')
      ;['Flow','Mbps','Delay (ms)','Jitter (ms)'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
      thead.appendChild(trh)
      table.appendChild(thead)
      const tbody = document.createElement('tbody')
      rows.forEach(r=>{
        const tr=document.createElement('tr')
        r.forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)})
        tbody.appendChild(tr)
      })
      table.appendChild(tbody)
      el.innerHTML = ''
      el.appendChild(info)
      el.appendChild(table)
    }).catch(()=>{ el.textContent = 'NR demo akış CSV bulunamadı.' })
  })
}
fetch('sites.json').then(r=>r.json()).then(sites=>{ drawSites(sites); buildControls(sites); loadResults(); loadNrFlows(); loadPositions() })
function loadComparison(){
  const el = document.getElementById('compare')
  const path = `../results/comparison_u${state.users}_b${state.beams}.csv`
  fetch(path).then(r=>{
    if(!r.ok) throw new Error('no comparison')
    return r.text()
  }).then(txt=>{
    const rows = txt.trim().split('\n').slice(1).map(l=>l.split(','))
    let bestObj = -1
    let bestMethod = ''
    let bestFair = -1
    let fairMethod = ''
    rows.forEach(r=>{const obj=parseFloat(r[4]);const j=parseFloat(r[3]);if(obj>bestObj){bestObj=obj;bestMethod=r[0]}if(j>bestFair){bestFair=j;fairMethod=r[0]}})
    const info = document.createElement('div')
    info.className = 'kpi'
    const k1 = document.createElement('div'); k1.textContent = `En iyi skor: ${bestMethod} (${bestObj.toFixed(2)})`
    const k2 = document.createElement('div'); k2.textContent = `En adil: ${fairMethod} (Jain=${bestFair.toFixed(2)})`
    info.appendChild(k1); info.appendChild(k2)
    const table = document.createElement('table')
    const thead = document.createElement('thead')
    const trh = document.createElement('tr')
    ;['Yöntem','Durum','Toplam Mbps','Jain','Skor','Users','Beams'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
    thead.appendChild(trh)
    table.appendChild(thead)
    const tbody = document.createElement('tbody')
    rows.forEach(r=>{
      const tr=document.createElement('tr')
      if(r[0]===bestMethod) tr.className = 'row-best'
      const cells=[r[0], r[1], (parseFloat(r[2])/1e6).toFixed(2), parseFloat(r[3]).toFixed(2), parseFloat(r[4]).toFixed(2), r[5], r[6]]
      cells.forEach((v,idx)=>{
        const td=document.createElement('td')
        if(idx===1){
          const tag=document.createElement('span'); tag.className = 'tag ' + (v==='True'?'true':'false'); tag.textContent = v==='True'?'Feasible':'Infeasible'; td.appendChild(tag)
        }else{ td.textContent=v }
        tr.appendChild(td)
      })
      tbody.appendChild(tr)
    })
    table.appendChild(tbody)
    el.innerHTML = ''
    el.appendChild(info)
    el.appendChild(table)
    try{ pushHistory({ ts: Date.now(), users: state.users, beams: state.beams, bestMethod, bestObj: parseFloat(bestObj.toFixed(2)), fairMethod, bestFair: parseFloat(bestFair.toFixed(2)) }); renderHistory() }catch(e){}
  }).catch(()=>{
    fetch('../results/comparison.csv').then(r=>r.text()).then(txt=>{
      const rows = txt.trim().split('\n').slice(1).map(l=>l.split(','))
      let bestObj = -1, bestMethod = '', bestFair = -1, fairMethod = ''
      rows.forEach(r=>{const obj=parseFloat(r[4]);const j=parseFloat(r[3]);if(obj>bestObj){bestObj=obj;bestMethod=r[0]}if(j>bestFair){bestFair=j;fairMethod=r[0]}})
      const info = document.createElement('div')
      info.className = 'kpi'
      const k1 = document.createElement('div'); k1.textContent = `En iyi skor: ${bestMethod} (${bestObj.toFixed(2)})`
      const k2 = document.createElement('div'); k2.textContent = `En adil: ${fairMethod} (Jain=${bestFair.toFixed(2)})`
      info.appendChild(k1); info.appendChild(k2)
      const table = document.createElement('table')
      const thead = document.createElement('thead')
      const trh = document.createElement('tr')
      ;['Yöntem','Durum','Toplam Mbps','Jain','Skor','Users','Beams'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
      thead.appendChild(trh)
      table.appendChild(thead)
      const tbody = document.createElement('tbody')
      rows.forEach(r=>{
        const tr=document.createElement('tr')
        const cells=[r[0], r[1], (parseFloat(r[2])/1e6).toFixed(2), parseFloat(r[3]).toFixed(2), parseFloat(r[4]).toFixed(2), r[5], r[6]]
        cells.forEach((v,idx)=>{const td=document.createElement('td'); if(idx===1){const tag=document.createElement('span');tag.className='tag '+(v==='True'?'true':'false');tag.textContent=v==='True'?'Feasible':'Infeasible';td.appendChild(tag)} else {td.textContent=v} tr.appendChild(td)})
        tbody.appendChild(tr)
      })
      table.appendChild(tbody)
      el.innerHTML = ''
      el.appendChild(info)
      el.appendChild(table)
      try{ pushHistory({ ts: Date.now(), users: state.users, beams: state.beams, bestMethod, bestObj: parseFloat(bestObj.toFixed(2)), fairMethod, bestFair: parseFloat(bestFair.toFixed(2)) }); renderHistory() }catch(e){}
    }).catch(()=>{ el.textContent = 'Karşılaştırma CSV yok.' })
  })
}
function safeGetHistory(){
  try{
    const raw = localStorage.getItem('history')
    if(!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  }catch(e){ return [] }
}
function pushHistory(entry){
  const arr = safeGetHistory()
  arr.unshift(entry)
  try{ localStorage.setItem('history', JSON.stringify(arr.slice(0,10))) }catch(e){}
}
function renderHistory(){
  const el=document.getElementById('history')
  const arr = safeGetHistory()
  if(!arr.length){ el.textContent='Henüz geçmiş yok'; return }
  const table=document.createElement('table')
  const thead=document.createElement('thead')
  const trh=document.createElement('tr')
  ;['Zaman','Users','Beams','En iyi skor','Skor','En adil','Jain'].forEach(h=>{const th=document.createElement('th');th.textContent=h;trh.appendChild(th)})
  thead.appendChild(trh); table.appendChild(thead)
  const tbody=document.createElement('tbody')
  arr.forEach(x=>{
    const tr=document.createElement('tr')
    const d=new Date(x.ts)
    const cells=[d.toLocaleString(), x.users, x.beams, x.bestMethod, x.bestObj ? x.bestObj.toFixed(2) : '-', x.fairMethod, x.bestFair ? x.bestFair.toFixed(2) : '-']
    cells.forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)})
    tbody.appendChild(tr)
  })
  table.appendChild(tbody)
  el.innerHTML=''
  el.appendChild(table)
}
loadComparison()
function loadScenario(){
  const el = document.getElementById('scenario')
  fetch('../configs/simulation.json').then(r=>{
    if(!r.ok) throw new Error('no cfg')
    return r.json()
  }).then(cfg=>{
    const bwMHz = (cfg.bandwidth_hz/1e6).toFixed(2)
    const ratio = Array.isArray(cfg.dl_ul_ratio)? cfg.dl_ul_ratio.join(':') : '4:1'
    el.textContent = `Senaryo • Users=${cfg.users_min} • Beams=${cfg.beams_per_cell} • Band=${cfg.frequency_band} • BW=${bwMHz} MHz • TDD=${cfg.tdd_pattern} (${ratio})`
  }).catch(()=>{ el.textContent = 'Senaryo bilgisi bulunamadı' })
}
loadScenario()

function haversine(lat1, lon1, lat2, lon2){
  const R = 6371000
  const dLat = deg2rad(lat2-lat1)
  const dLon = deg2rad(lon2-lon1)
  const a = Math.sin(dLat/2)**2 + Math.cos(deg2rad(lat1))*Math.cos(deg2rad(lat2))*Math.sin(dLon/2)**2
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}
function metersToDeg(lat, mLat, mLon){
  const dLat = mLat/111320
  const dLon = mLon/(111320*Math.cos(deg2rad(lat)))
  return [dLat, dLon]
}
function generateRandomSites(n, centerLat, centerLon){
  const sites = []
  const maxRadiusM = 8000
  const minDist = 1000
  const maxNN = 5000
  let attempts = 0
  while(sites.length < n && attempts < 10000){
    attempts++
    const r = Math.random() * maxRadiusM
    const theta = Math.random() * 360
    const [dLat, dLon] = metersToDeg(centerLat, r*Math.cos(deg2rad(theta)), r*Math.sin(deg2rad(theta)))
    const lat = centerLat + dLat
    const lon = centerLon + dLon
    let ok = true
    let hasNeighbor = sites.length === 0
    for(const s of sites){
      const d = haversine(lat, lon, s.lat, s.lon)
      if(d < minDist){ ok = false; break }
      if(d <= maxNN){ hasNeighbor = true }
    }
    if(!ok || !hasNeighbor) continue
    sites.push({ name: `Site ${sites.length+1}`, lat, lon, sectors: [0,120,240] })
  }
  return sites.length === n ? sites : sites
}
function loadProgress(){
  const el = document.getElementById('progress')
  const path = `../results/nr_progress_u${state.users}_b${state.beams}.txt?v=${Date.now()}`
  fetch(path).then(r=>{
    if(!r.ok) throw new Error('no progress')
    return r.text()
  }).then(txt=>{
    const lines = txt.trim().split('\n')
    const status = /Done/.test(txt) ? 'NS-3: Done' : 'NS-3: Running'
    const pre = document.createElement('pre')
    pre.textContent = lines.slice(-5).join('\n')
    el.innerHTML = ''
    const h = document.createElement('div')
    h.textContent = status
    el.appendChild(h)
    el.appendChild(pre)
    if(status !== 'NS-3: Done'){
      setTimeout(loadProgress, 1000)
    }
  }).catch(()=>{
    el.textContent = 'NR demo progress bulunamadı.'
  })
}
function loadPositions(){
  const path = `../results/positions_u${state.users}_b${state.beams}.json?v=${Date.now()}`
  fetch(path).then(r=>{
    if(!r.ok) throw new Error('no positions')
    return r.json()
  }).then(data=>{
    drawUEs(data.ue || [])
  }).catch(()=>{
    fetch('../results/positions.json?v=' + Date.now()).then(r=>r.json()).then(data=>{ drawUEs(data.ue || []) }).catch(()=>{})
  })
}
    var cc = document.getElementById('compare-cond')
    if(cc) cc.textContent = `Users=${state.users} • Beams=${state.beams}`
      var cc2 = document.getElementById('compare-cond')
      if(cc2) cc2.textContent = `Users=${state.users} • Beams=${state.beams}`
