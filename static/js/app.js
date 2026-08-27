// Phase2: 商品編集・削除・手動更新を実装

async function fetchProducts(){
  const res = await fetch("/api/products");
  if (!res.ok) {
    document.getElementById("product-list").innerText = "商品一覧の取得に失敗しました。";
    return;
  }
  const products = await res.json();
  renderProductList(products);
}

function renderProductList(products){
  const container = document.getElementById("product-list");
  if (!container) return;
  if (products.length === 0) {
    container.innerHTML = "<div class='small'>登録された商品がありません。右上の＋から追加してください。</div>";
    return;
  }
  container.innerHTML = "";
  products.forEach(p => {
    const div = document.createElement("div");
    div.className = "product-item";
    div.innerHTML = `
      <div>
        <div><strong>${escapeHtml(p.name)}</strong></div>
        <div class="product-meta">${escapeHtml(p.shop || "")}　<a href="${escapeHtml(p.url)}" target="_blank">商品ページ</a></div>
      </div>
      <div style="text-align:right">
        <div class="small">現在価格: ${p.last_price ?? "-"} 円</div>
        <div style="margin-top:6px;">
          <button class="btn-refresh" data-id="${p.id}">今すぐ更新</button>
          <button class="btn-edit" data-id="${p.id}">編集</button>
          <button class="btn-delete" data-id="${p.id}">削除</button>
        </div>
      </div>
    `;
    container.appendChild(div);
  });

  // attach handlers
  document.querySelectorAll(".btn-edit").forEach(b => b.addEventListener("click", (e) => {
    const id = e.currentTarget.getAttribute("data-id");
    showEditDialog(id);
  }));
  document.querySelectorAll(".btn-delete").forEach(b => b.addEventListener("click", (e) => {
    const id = e.currentTarget.getAttribute("data-id");
    confirmAndDelete(id);
  }));
  document.querySelectorAll(".btn-refresh").forEach(b => b.addEventListener("click", (e) => {
    const id = e.currentTarget.getAttribute("data-id");
    manualRefresh(id, e.currentTarget);
  }));
}

function escapeHtml(s){ if(!s) return ""; return s.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;"); }

document.addEventListener("DOMContentLoaded", () => {
  fetchProducts();

  const btn = document.getElementById("btn-add");
  if (btn) btn.addEventListener("click", showAddDialog);
});

// --- Add dialog (unchanged) ---
function showAddDialog(){
  const tpl = document.getElementById("add-dialog");
  const dialog = tpl.content.cloneNode(true);
  const form = dialog.querySelector("#add-form");
  const cancel = dialog.querySelector("#cancel");

  // モーダル
  const modal = createModal();
  modal.querySelector(".modal-inner").appendChild(dialog);
  document.body.appendChild(modal);

  cancel.addEventListener("click", ()=> document.body.removeChild(modal));
  form.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(form);
    const payload = {
      name: fd.get("name"),
      url: fd.get("url"),
      shop: fd.get("shop") || undefined,
      check_interval_minutes: Number(fd.get("check_interval_minutes") || 60)
    };
    const res = await fetch("/api/products", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    if (res.ok){
      await fetchProducts();
      document.body.removeChild(modal);
    } else {
      const txt = await res.text();
      alert("追加に失敗しました: " + txt);
    }
  });
}

// --- Edit dialog ---
async function showEditDialog(id){
  // fetch current product
  const res = await fetch(`/api/products/${id}`);
  if (!res.ok) { alert("商品情報の取得に失敗しました"); return; }
  const p = await res.json();

  const tpl = document.getElementById("edit-dialog");
  const dialog = tpl.content.cloneNode(true);
  const form = dialog.querySelector("#edit-form");
  const cancel = dialog.querySelector("#cancel-edit");

  // fill values
  form.name.value = p.name || "";
  form.url.value = p.url || "";
  form.shop.value = p.shop || "";
  form.check_interval_minutes.value = p.check_interval_minutes || 60;

  const modal = createModal();
  modal.querySelector(".modal-inner").appendChild(dialog);
  document.body.appendChild(modal);

  cancel.addEventListener("click", ()=> document.body.removeChild(modal));
  form.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(form);
    const payload = {
      name: fd.get("name"),
      url: fd.get("url"),
      shop: fd.get("shop") || undefined,
      check_interval_minutes: Number(fd.get("check_interval_minutes") || 60)
    };
    const r = await fetch(`/api/products/${id}`, {
      method: "PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    if (r.ok){
      await fetchProducts();
      document.body.removeChild(modal);
    } else {
      const txt = await r.text();
      alert("更新に失敗しました: " + txt);
    }
  });
}

function createModal(){
  const modal = document.createElement("div");
  modal.style.position = "fixed";
  modal.style.left = "0";
  modal.style.top = "0";
  modal.style.right = "0";
  modal.style.bottom = "0";
  modal.style.background = "rgba(0,0,0,0.6)";
  modal.style.display = "flex";
  modal.style.alignItems = "center";
  modal.style.justifyContent = "center";
  const inner = document.createElement("div");
  inner.className = "modal-inner";
  inner.style.width = "420px";
  modal.appendChild(inner);
  return modal;
}

// --- Delete with confirmation ---
async function confirmAndDelete(id){
  if (!confirm("本当にこの商品を削除しますか？この操作は取り消せません。")) return;
  const res = await fetch(`/api/products/${id}`, { method: "DELETE" });
  if (res.ok) {
    await fetchProducts();
  } else {
    alert("削除に失敗しました");
  }
}

// --- Manual refresh ---
async function manualRefresh(id, btnElem){
  const original = btnElem.innerText;
  try {
    btnElem.disabled = true;
    btnElem.innerText = "取得中...";
    const res = await fetch(`/api/products/${id}/refresh`, { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      alert(data.message || "取得を実行しました（スタブ）。");
    } else {
      const txt = await res.text();
      alert("更新リクエスト失敗: " + txt);
    }
  } catch (e) {
    alert("通信エラー: " + e.message);
  } finally {
    btnElem.disabled = false;
    btnElem.innerText = original;
  }
}
