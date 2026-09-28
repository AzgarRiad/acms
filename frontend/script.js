let products = [];
let orders = [];

function bdDate(){
  const d = new Date();
  const pad = n => String(n).padStart(2,'0');
  return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()}`;
}
function seedData(){
  products = [
    {id:'p1', name:'RTX 4060 GPU', price:38700, stock:12},
    {id:'p2', name:'Ryzen 5 7600 CPU', price:19700, stock:8},
    {id:'p3', name:'32GB DDR5 RAM Kit', price:14200, stock:25}
  ];
  orders = [
    {id:1001, customer:'Fahim R.', phone:'01711-223344', items:[{name:'RTX 4060 GPU',qty:1,price:38700},{name:'32GB DDR5 RAM Kit',qty:1,price:14200}], total:52900, status:'paid', date:bdDate()},
    {id:1002, customer:'Nusrat J.', phone:'01822-334455', items:[{name:'32GB DDR5 RAM Kit',qty:1,price:14200}], total:14200, status:'pending', date:bdDate()},
    {id:1003, customer:'Tanvir A.', phone:'01933-445566', items:[{name:'RTX 4060 GPU',qty:1,price:38700},{name:'Ryzen 5 7600 CPU',qty:1,price:19700},{name:'32GB DDR5 RAM Kit',qty:1,price:14200}], total:72600, status:'cancelled', date:bdDate()}
  ];
  save();
}
function resetData(){
  showConfirm('This will replace your current products and orders with the sample data. Continue?', ()=>{
    seedData();
    orderLines = [];
    renderAll(); renderOrderForm();
    showToast('Sample data restored.');
  });
}
function load(){
  let hasProducts = true, hasOrders = true;
  try{
    const raw = localStorage.getItem('cm_products');
    hasProducts = raw !== null;
    products = JSON.parse(raw || '[]');
  }catch(e){ products = []; }
  try{
    const raw = localStorage.getItem('cm_orders');
    hasOrders = raw !== null;
    orders = JSON.parse(raw || '[]');
  }catch(e){ orders = []; }

  // First run: seed with sample data so the app isn't empty
  if(!hasProducts && !hasOrders){
    seedData();
  }
}
function save(){
  try{
    localStorage.setItem('cm_products', JSON.stringify(products));
    localStorage.setItem('cm_orders', JSON.stringify(orders));
  }catch(e){ console.error('Storage error', e); }
}

function showTab(t){
  document.getElementById('tabCatalog').classList.toggle('hidden', t!=='catalog');
  document.getElementById('tabOrders').classList.toggle('hidden', t!=='orders');
  document.getElementById('tabCatalogBtn').classList.toggle('active', t==='catalog');
  document.getElementById('tabOrdersBtn').classList.toggle('active', t==='orders');
  if(t==='orders') renderOrderForm();
}

function showToast(msg){
  let t = document.getElementById('toast');
  if(!t){
    t = document.createElement('div');
    t.id = 'toast';
    t.style.cssText = 'position:fixed; left:50%; bottom:24px; transform:translateX(-50%); background:var(--text); color:var(--bg); padding:10px 16px; border-radius:8px; font-size:13px; z-index:1000; box-shadow:var(--shadow); max-width:90%; text-align:center;';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(t._timer);
  t._timer = setTimeout(()=>{ t.style.display='none'; }, 2500);
}

function showConfirm(msg, onYes){
  const old = document.getElementById('confirmModal');
  if(old) old.remove();
  const overlay = document.createElement('div');
  overlay.id = 'confirmModal';
  overlay.style.cssText = 'position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:1001; padding:16px;';
  overlay.innerHTML = `<div style="background:var(--card); border:1px solid var(--border); border-radius:12px; padding:18px; max-width:320px; box-shadow:var(--shadow);">
    <div style="margin-bottom:14px; font-size:14px;">${escapeHtml(msg)}</div>
    <div style="display:flex; gap:8px; justify-content:flex-end;">
      <button class="secondary" id="confirmNo">Cancel</button>
      <button class="danger" id="confirmYes">Confirm</button>
    </div>
  </div>`;
  document.body.appendChild(overlay);
  overlay.addEventListener('click', e=>{ if(e.target===overlay) overlay.remove(); });
  document.getElementById('confirmNo').onclick = ()=> overlay.remove();
  document.getElementById('confirmYes').onclick = ()=>{ overlay.remove(); onYes(); };
}

function addProduct(){
  const name = document.getElementById('pName').value.trim();
  const price = parseFloat(document.getElementById('pPrice').value);
  const stock = parseInt(document.getElementById('pStock').value);
  if(!name || isNaN(price) || price<0 || isNaN(stock) || stock<0){
    showToast('Enter a valid name, price and stock.'); return;
  }
  products.push({id: Date.now().toString(36), name, price, stock});
  document.getElementById('pName').value='';
  document.getElementById('pPrice').value='';
  document.getElementById('pStock').value='';
  save(); renderAll();
}
function deleteProduct(id){
  products = products.filter(p=>p.id!==id);
  save(); renderAll();
}
let editingProductId = null;
function editProduct(id){
  editingProductId = id;
  renderProducts();
}
function saveProductEdit(id){
  const p = products.find(x=>x.id===id);
  if(!p) return;
  const name = document.getElementById('edit-name-'+id).value.trim();
  const price = parseFloat(document.getElementById('edit-price-'+id).value);
  const stock = parseInt(document.getElementById('edit-stock-'+id).value);
  if(!name || isNaN(price) || price<0 || isNaN(stock) || stock<0){
    showToast('Enter a valid name, price and stock.'); return;
  }
  p.name = name; p.price = price; p.stock = stock;
  editingProductId = null;
  save(); renderAll();
}
function cancelProductEdit(){
  editingProductId = null;
  renderProducts();
}

function renderProducts(){
  const tbody = document.querySelector('#productTable tbody');
  tbody.innerHTML='';
  document.getElementById('productEmpty').classList.toggle('hidden', products.length>0);
  products.forEach(p=>{
    const tr = document.createElement('tr');
    if(editingProductId===p.id){
      tr.innerHTML = `<td><input id="edit-name-${p.id}" value="${escapeHtml(p.name)}" style="min-width:90px"></td>
        <td><input id="edit-price-${p.id}" type="number" step="0.01" value="${p.price}" style="width:80px"></td>
        <td><input id="edit-stock-${p.id}" type="number" value="${p.stock}" style="width:60px"></td>
        <td><button onclick="saveProductEdit('${p.id}')">Save</button></td>
        <td><button class="secondary" onclick="cancelProductEdit()">Cancel</button></td>`;
    } else {
      tr.innerHTML = `<td>${escapeHtml(p.name)}</td><td>${money(p.price)}</td><td>${p.stock}</td>
        <td><button class="secondary" onclick="editProduct('${p.id}')">Edit</button></td>
        <td><button class="danger" onclick="deleteProduct('${p.id}')">Delete</button></td>`;
    }
    tbody.appendChild(tr);
  });
}

let orderLines = [];
function addOrderLine(){
  if(products.length===0){ showToast('Add a product first.'); return; }
  orderLines.push({productId: products[0].id, qty:1});
  renderOrderForm();
}
function removeOrderLine(idx){
  orderLines.splice(idx,1);
  renderOrderForm();
}
function updateOrderLine(idx, field, value){
  orderLines[idx][field] = field==='qty' ? parseInt(value)||1 : value;
}
function renderOrderForm(){
  const wrap = document.getElementById('orderItems');
  wrap.innerHTML='';
  if(orderLines.length===0 && products.length>0) orderLines.push({productId:products[0].id, qty:1});
  if(products.length===0){
    wrap.innerHTML = '<div class="empty">Add products in the Catalog tab first.</div>';
    return;
  }
  orderLines.forEach((line, idx)=>{
    const div = document.createElement('div');
    div.className='itemrow';
    const options = products.map(p=>`<option value="${p.id}" ${p.id===line.productId?'selected':''}>${escapeHtml(p.name)} (${money(p.price)})</option>`).join('');
    div.innerHTML = `<select onchange="updateOrderLine(${idx},'productId',this.value)">${options}</select>
      <input class="qty" type="number" min="1" value="${line.qty}" onchange="updateOrderLine(${idx},'qty',this.value)">
      <button class="secondary" onclick="removeOrderLine(${idx})">✕</button>`;
    wrap.appendChild(div);
  });
}

function createOrder(){
  if(orderLines.length===0){ showToast('Add at least one item.'); return; }
  let total = 0;
  const items = [];
  for(const line of orderLines){
    const p = products.find(x=>x.id===line.productId);
    if(!p) continue;
    total += p.price * line.qty;
    items.push({name:p.name, qty:line.qty, price:p.price});
  }
  const customer = document.getElementById('customerName').value.trim() || 'Walk-in';
  const phone = document.getElementById('customerPhone').value.trim();
  const nextId = orders.length ? Math.max(...orders.map(o=>o.id)) + 1 : 1001;
  orders.push({id: nextId, customer, phone, items, total, status:'pending', date: bdDate()});
  orderLines = [];
  document.getElementById('customerName').value='';
  document.getElementById('customerPhone').value='';
  save(); renderAll(); renderOrderForm();
}
function toggleStatus(id){
  const cycle = {pending:'paid', paid:'cancelled', cancelled:'pending'};
  const o = orders.find(x=>x.id===id);
  if(o) o.status = cycle[o.status] || 'pending';
  save(); renderOrders(); renderStats();
}
function deleteOrder(id){
  orders = orders.filter(o=>o.id!==id);
  save(); renderAll();
}

function renderOrders(){
  const tbody = document.querySelector('#orderTable tbody');
  tbody.innerHTML='';
  document.getElementById('orderEmpty').classList.toggle('hidden', orders.length>0);
  orders.slice().reverse().forEach(o=>{
    const itemCount = o.items.reduce((s,i)=>s+i.qty,0);
    const tr = document.createElement('tr');
    tr.title = o.items.map(i=>`${i.qty}× ${i.name}`).join(', ');
    tr.innerHTML = `<td>ORD-${o.id}</td><td>${escapeHtml(o.customer)}</td><td>${escapeHtml(o.phone||'—')}</td><td>${itemCount}</td><td>${money(o.total)}</td>
      <td><span class="pill ${o.status}" style="cursor:pointer" onclick="toggleStatus(${o.id})">${o.status}</span></td>
      <td><button class="danger" onclick="deleteOrder(${o.id})">Delete</button></td>`;
    tbody.appendChild(tr);
  });
}

function renderStats(){
  document.getElementById('statProducts').textContent = products.length;
  document.getElementById('statStock').textContent = products.reduce((s,p)=>s+p.stock,0);
  document.getElementById('statOrders').textContent = orders.length;
  const rev = orders.filter(o=>o.status==='paid').reduce((s,o)=>s+o.total,0);
  document.getElementById('statRevenue').textContent = money(rev);
}
// revenue counts 'paid' orders

function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function money(n){
  return '৳' + Number(n).toLocaleString('en-US', {maximumFractionDigits:2});
}

function renderAll(){
  renderProducts(); renderOrders(); renderStats();
}

load();
renderAll();
renderOrderForm();
