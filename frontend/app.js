const API = "https://egg-app.onrender.com";

/* ================= CACHE ================= */
const getCache = k => JSON.parse(localStorage.getItem(k) || "{}");
const setCache = (k, v) => localStorage.setItem(k, JSON.stringify(v));

/* ================= TOAST ================= */
function notify(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.innerText = msg;
  toast.className = `toast show ${type}`;
  setTimeout(() => (toast.className = "toast"), 2500);
}

/* ================= INIT ================= */
(function () {
  const d = new Date().toISOString().slice(0, 10);
  eggDate.value = d;
  eggPrice.value = localStorage.getItem("eggPrice") || "";
  loadAll();
})();

async function loadAll() {
  await Promise.all([
    loadPeople(),
    loadDailyHistory(),
    loadDue(),
    loadTotalBalance()
  ]);
}

/* ================= PEOPLE ================= */
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
        <input id="pay-${p.id}" placeholder="₹" class="pay-input" type="number"/>
        <button class="mini" data-pay="${p.id}">Pay</button>
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
    inp.type = "number";
    inp.placeholder = p.name;
    inp.value = cache[p.id] || 0;
    eggInputs.appendChild(inp);
  });

  document.querySelectorAll("[data-history]").forEach(btn => {
    btn.onclick = () =>
      viewHistory(btn.dataset.history, btn.dataset.name);
  });

  document.querySelectorAll("[data-pay]").forEach(btn => {
    btn.onclick = () => pay(btn.dataset.pay);
  });
}

async function addPerson() {
  if (!personName.value.trim()) {
    notify("Name required", "error");
    return;
  }

  await fetch(`${API}/people`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: personName.value })
  });

  personName.value = "";
  notify("Person added");
  loadPeople();
}

/* ================= RECHARGE ================= */
async function pay(id) {
  const input = document.getElementById(`pay-${id}`);
  const amt = Number(input.value);

  if (!amt || amt <= 0) {
    notify("Enter valid amount", "error");
    return;
  }

  await fetch(`${API}/people/${id}/recharge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount: amt })
  });

  input.value = "";
  notify("Payment recorded");
  loadPeople();
  loadTotalBalance();
}

/* ================= DAILY EGGS ================= */
async function submitDailyEggs() {
  if (!eggPrice.value) {
    notify("Egg price required", "error");
    return;
  }

  const people = await fetch(`${API}/people`).then(r => r.json());
  const eggs = {};
  let hasEggs = false;

  people.forEach(p => {
    const val = Number(document.getElementById(`egg-${p.id}`).value || 0);
    eggs[p.id] = val;
    if (val > 0) hasEggs = true;
  });

  if (!hasEggs) {
    notify("Enter at least one egg count", "error");
    return;
  }

  const res = await fetch(`${API}/daily-eggs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      date: eggDate.value,
      egg_price: Number(eggPrice.value),
      eggs
    })
  });

  if (!res.ok) {
    const err = await res.json();
    notify(err.detail || "Failed to save", "error");
    return;
  }

  setCache("eggs", eggs);
  localStorage.setItem("eggPrice", eggPrice.value);

  notify("Daily entry saved");
  loadAll();
}

async function undoDailyEggs() {
  if (!confirm("Undo last daily entry?")) return;

  const res = await fetch(`${API}/daily-eggs/undo`, { method: "POST" });
  if (!res.ok) {
    notify("Nothing to undo", "error");
    return;
  }

  notify("Last entry undone", "info");
  loadAll();
}

/* ================= DAILY HISTORY ================= */
async function loadDailyHistory() {
  const rows = await fetch(`${API}/reports/daily-eggs`).then(r => r.json());
  dailyHistory.innerHTML = "";

  if (!rows.length) {
    dailyHistory.innerHTML =
      `<tr><td colspan="4">No history</td></tr>`;
    return;
  }

  rows.forEach(r => {
    dailyHistory.innerHTML += `
      <tr>
        <td>${r.date}</td>
        <td>₹${r.egg_price}</td>
        <td>${r.total_eggs}</td>
        <td>₹${r.total_cost}</td>
      </tr>`;
  });
}

/* ================= PERSON HISTORY ================= */
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
  if (!rows.length) {
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
      </tr>`;
  });

  notify("History loaded", "info");
}

function closeModal() {
  modal.style.display = "none";
}

/* ================= REPORTS ================= */
async function loadDue() {
  const data = await fetch(`${API}/reports/dues`).then(r => r.json());
  dueTable.innerHTML = "";

  if (Object.keys(data).length === 0) {
    dueTable.innerHTML =
      `<tr><td colspan="2">No dues 🎉</td></tr>`;
    return;
  }

  Object.entries(data).forEach(([n, v]) => {
    dueTable.innerHTML += `
      <tr>
        <td>${n}</td>
        <td class="negative">₹${v}</td>
      </tr>`;
  });
}

async function loadTotalBalance() {
  const d = await fetch(`${API}/reports/total-balance`).then(r => r.json());
  credit.innerText = `₹${d.total_credit}`;
  due.innerText = `₹${d.total_due}`;
  net.innerText = `₹${d.net_balance}`;
}
