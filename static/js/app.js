// Phase1: フロントの最小ロジック。Phase2 以降で機能拡張します.

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
        <div style="margin-top:6px;"><a href="/product/${p.id}">詳細</a></div>
      </div>
    `;
    container.appendChild(div);
  });
}

function escapeHtml(s){ if(!s) return ""; return s.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;"); }

document.addEventListener("DOMContentLoaded", () => {
  fetchProducts();

  const btn = document.getElementById("btn-add");
  if (btn) btn.addEventListener("click", showAddDialog);
});

function showAddDialog(){
  const tpl = document.getElementById("add-dialog");
  const dialog = tpl.content.cloneNode(true);
  const form = dialog.querySelector("#add-form");
  const cancel = dialog.querySelector("#cancel");

  // モーダル
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
  modal.appendChild(document.createElement("div")).className = "modal-inner";
  modal.querySelector(".modal-inner").style.width = "420px";
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
      alert("追加に失敗しました");
    }
  });
}
