const API = "https://egg-app.onrender.com";

/* CACHE */
const getCache = k => JSON.parse(localStorage.getItem(k) || "{}");
const setCache = (k,v) => localStorage.setItem(k, JSON.stringify(v));

/* INIT */
(function () {
  const d = new Date().toISOString().slice(0,10);
  eggDate.value = d;
  eggPrice.value = localStorage.getItem("eggPrice") || "";
  loadAll();
})();

async function loadAll() {
  loadPeople();
  loadDailyHistory();
  loadDue();
  loadTotalBalance();
}

/* PEOPLE */
async function loadPeople() {
  const people = await fetch(`${API}/people`).then(r => r.json());
  const cache = getCache("eggs");

  peopleTable.innerHTML = "";
  eggInputs.innerHTML = "";

  people.forEach((p, i) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${p.name}</td>
      <td>${p.total_eggs}</td>
      <td class="${p.balance < 0 ? "negative" : "positive"}">
        ₹${p.balance.toFixed(2)}
      </td>
      <td>
        <input id="pay-${p.id}" placeholder="₹" class="pay-input"/>
        <button class="mini" data-id="${p.id}">Pay</button>
      </td>
      <td>
        <button class="mini secondary" data-history="${p.id}" data-name="${p.name}">
          View
        </button>
      </td>
    `;

    peopleTable.appendChild(tr);

    const inp = document.createElement("input");
    inp.id = `egg-${p.id}`;
    inp.placeholder = p.name;
    inp.type = "number";
    inp.value = cache[p.id] || 0;
    eggInputs.appendChild(inp);
  });

  // Attach listeners SAFELY
  document.querySelectorAll("[data-history]").forEach(btn => {
    btn.onclick = () =>
      viewHistory(btn.dataset.history, btn.dataset.name);
  });

  document.querySelectorAll(".mini:not(.secondary)").forEach(btn => {
    btn.onclick = () => pay(btn.dataset.id);
  });
}


async function addPerson() {
  await fetch(`${API}/people`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name:personName.value})
  });
  personName.value="";
  loadPeople();
}

/* RECHARGE */
async function pay(id) {
  const amt = document.getElementById(`pay-${id}`).value;
  await fetch(`${API}/people/${id}/recharge`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({amount:Number(amt)})
  });
  loadPeople();
  loadTotalBalance();
}

/* DAILY EGGS */
async function submitDailyEggs() {
  const people = await fetch(`${API}/people`).then(r=>r.json());
  const eggs = {};
  people.forEach(p=>eggs[p.id]=Number(document.getElementById(`egg-${p.id}`).value||0));

  await fetch(`${API}/daily-eggs`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      date:eggDate.value,
      egg_price:Number(eggPrice.value),
      eggs
    })
  });

  setCache("eggs",eggs);
  localStorage.setItem("eggPrice",eggPrice.value);

  loadAll();
}

async function undoDailyEggs() {
  await fetch(`${API}/daily-eggs/undo`,{method:"POST"});
  loadAll();
}

/* HISTORY */
async function loadDailyHistory() {
  const rows = await fetch(`${API}/reports/daily-eggs`).then(r=>r.json());
  dailyHistory.innerHTML="";
  rows.forEach(r=>{
    dailyHistory.innerHTML+=`
      <tr>
        <td>${r.date}</td>
        <td>₹${r.egg_price}</td>
        <td>${r.total_eggs}</td>
        <td>₹${r.total_cost}</td>
      </tr>`;
  });
}

async function viewHistory(id, name) {
  modal.style.display = "flex";
  modalTitle.innerText = `${name} History`;

  personHistory.innerHTML =
    `<tr><td colspan="3">Loading...</td></tr>`;

  const res = await fetch(`${API}/reports/person/${id}`);

  if (!res.ok) {
    personHistory.innerHTML =
      `<tr><td colspan="3">No history found</td></tr>`;
    return;
  }

  const rows = await res.json();

  if (rows.length === 0) {
    personHistory.innerHTML =
      `<tr><td colspan="3">No records</td></tr>`;
    return;
  }

  personHistory.innerHTML = "";
  rows.forEach(r => {
    personHistory.innerHTML += `
      <tr>
        <td>${r.date}</td>
        <td>${r.eggs}</td>
        <td>₹${r.amount.toFixed(2)}</td>
      </tr>
    `;
  });
}


function closeModal() {
  modal.style.display="none";
}

/* REPORTS */
async function loadDue() {
  const data = await fetch(`${API}/reports/dues`).then(r=>r.json());
  dueTable.innerHTML="";
  Object.entries(data).forEach(([n,v])=>{
    dueTable.innerHTML+=`<tr><td>${n}</td><td class="negative">₹${v}</td></tr>`;
  });
}

async function loadTotalBalance() {
  const d = await fetch(`${API}/reports/total-balance`).then(r=>r.json());
  credit.innerText = `₹${d.total_credit}`;
  due.innerText = `₹${d.total_due}`;
  net.innerText = `₹${d.net_balance}`;
}
