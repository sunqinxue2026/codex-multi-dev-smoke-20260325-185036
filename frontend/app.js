const state = { products: [], cart: [] };

function money(value) { return `¥${value}`; }

function renderProducts() {
  const root = document.getElementById('product-list');
  root.innerHTML = state.products.map(item => `
    <article class="card">
      <h3>${item.name}</h3>
      <p>价格：${money(item.price)}</p>
      <p>库存：${item.stock}</p>
      <button data-id="${item.id}">加入购物车</button>
    </article>
  `).join('');
  root.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => addToCart(Number(btn.dataset.id))));
}

function renderCart() {
  const list = document.getElementById('cart-items');
  const total = state.cart.reduce((sum, item) => sum + item.price, 0);
  list.innerHTML = state.cart.map(item => `<li>${item.name} - ${money(item.price)}</li>`).join('');
  document.getElementById('cart-total').textContent = `合计：${money(total)}`;
}

function addToCart(id) {
  const item = state.products.find(product => product.id === id);
  if (!item) return;
  state.cart.push(item);
  renderCart();
}

async function loadProducts() {
  const resp = await fetch('/api/snacks');
  const data = await resp.json();
  state.products = data.items || [];
  renderProducts();
}

async function checkout() {
  const resp = await fetch('/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: state.cart.map(item => ({ id: item.id, quantity: 1 })) }),
  });
  const data = await resp.json();
  document.getElementById('order-status').textContent = data.message === 'order_created' ? '下单成功' : '下单失败';
}

document.getElementById('checkout-btn').addEventListener('click', checkout);
loadProducts();
