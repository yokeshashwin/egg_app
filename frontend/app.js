const API = "http://127.0.0.1:8000";

/* ========= LAST USED EGGS ========= */
function getLastEggs() {
  return JSON.parse(localStorage.getItem("lastEggs") || "{}");
}
function saveLastEggs(eggs) {
  localStorage.setItem("lastEggs", JSON.stringify(eggs));
}

/* ========= LAST USED EGG PRICE ========= */
function getLastEggPrice() {
  return localStorage.getItem("lastEggPrice") || "";
}
function saveLastEggPrice(price) {
  localStorage.setItem("lastEggPrice", price);
}

/* ========= TOAST ========= */
function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = `toast show ${type}`;
  setTimeout(() => (toast.className = "toast"), 2500);
}

/* ========= THEME ========= */
function toggleTheme() {
  document.body.classList.toggle("dark");
  const isDark = document.body.classList.contains("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  document.getElementById("themeToggle").textContent = isDark ? "☀️" : "🌙";
}
(function () {
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
    document.getElementById("themeToggle").textContent = "☀️";
  }
})();

/* ========= SET TODAY'S DATE + LAST EGG PRICE ========= */
function setTodayDate() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  eggDate.value = `${yyyy}-${mm}-${dd}`;

  // 🔥 Auto-fill egg price from cache
  const lastPrice = getLastEggPrice();
  if (lastPrice) {
    eggPrice.value = lastPrice;
  }
}

/* ========= WALLET ========= */
async function createWallet() {
  const amount = walletAmount.value;
  await fetch(`${API}/wallet/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount: Number(amount) })
  });
  loadWallet();
  showToast("Wallet created");
}

async function rechargeWallet() {
  const amount = walletAmount.value;
  await fetch(`${API}/wallet/recharge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount: Number(amount) })
  });
  loadWallet();
  showToast("Wallet recharged");
}

async function loadWallet() {
  const res = await fetch(`${API}/wallet`);
  const data = await res.json();
  walletBalance.innerText = `₹${data.balance}`;
}

/* ========= PEOPLE ========= */
async function loadPeople() {
  const res = await fetch(`${API}/people`);
  const people = await res.json();
  const lastEggs = getLastEggs();

  const peopleTable = document.getElementById("peopleTable");
  const eggInputs = document.getElementById("eggInputs");

  peopleTable.innerHTML = "";
  eggInputs.innerHTML = "";

  people.forEach((p, index) => {
    // TABLE ROW
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${p.name}</td>
      <td><span class="badge">${p.total_eggs}</span></td>
    `;
    peopleTable.appendChild(tr);

    // DAILY EGG INPUT
    const input = document.createElement("input");
    input.type = "number";
    input.min = 0;
    input.id = `egg-${p.id}`;
    input.placeholder = `${p.name} eggs`;
    input.value = lastEggs[p.id] ?? 0;

    eggInputs.appendChild(input);
  });
}

async function addPerson() {
  if (!personName.value.trim()) {
    showToast("Name required", "error");
    return;
  }
  await fetch(`${API}/people`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: personName.value })
  });
  personName.value = "";
  loadPeople();
  showToast("Person added");
}

/* ========= UNDO DAILY EGGS ========= */
async function undoDailyEggs() {
  if (!confirm("Undo last daily egg entry? This cannot be reverted.")) return;

  const res = await fetch(`${API}/daily-eggs/undo`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json();
    showToast(err.detail || "Nothing to undo", "error");
    return;
  }

  loadWallet();
  loadPeople();
  showToast("Last daily entry undone");
}

/* ========= DAILY EGGS ========= */
async function submitDailyEggs() {
  if (!eggDate.value || !eggPrice.value) {
    showToast("Date & price required", "error");
    return;
  }

  const res = await fetch(`${API}/people`);
  const people = await res.json();
  const eggs = {};

  people.forEach(p => {
    eggs[p.id] = Number(document.getElementById(`egg-${p.id}`).value || 0);
  });

  await fetch(`${API}/daily-eggs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      date: eggDate.value,
      egg_price: Number(eggPrice.value),
      eggs
    })
  });

  // 🔥 SAVE TO CACHE
  saveLastEggs(eggs);
  saveLastEggPrice(eggPrice.value);

  loadWallet();
  loadPeople();
  showToast("Daily entry saved");
}

/* ========= RECHARGE SPLIT ========= */
async function calculateSplit() {
  if (!rechargeAmount.value) {
    showToast("Enter recharge amount", "error");
    return;
  }

  const res = await fetch(
    `${API}/recharge-split?amount=${rechargeAmount.value}`,
    { method: "POST" }
  );

  const data = await res.json();
  const splitTable = document.getElementById("splitTable");
  splitTable.innerHTML = "";

  Object.entries(data).forEach(([name, amount]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${name}</td>
      <td class="amount">₹${amount.toFixed(2)}</td>
    `;
    splitTable.appendChild(tr);
  });

  showToast("Recharge split calculated");
}

/* ========= INIT ========= */
setTodayDate();
loadWallet();
loadPeople();
