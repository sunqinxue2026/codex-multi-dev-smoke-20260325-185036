import { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || ''

export default function App() {
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState([])
  const [status, setStatus] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/api/snacks`)
      .then((resp) => resp.json())
      .then((data) => setProducts(data.items || []))
      .catch(() => setStatus('商品加载失败'))
  }, [])

  const total = useMemo(
    () => cart.reduce((sum, item) => sum + item.price, 0),
    [cart]
  )

  function addToCart(product) {
    setCart((prev) => [...prev, product])
  }

  function clearCart() {
    setCart([])
    setStatus('购物车已清空')
  }

  async function checkout() {
    const items = cart.map((item) => ({ id: item.id, quantity: 1 }))
    const resp = await fetch(`${API_BASE}/api/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items }),
    })
    const data = await resp.json()
    setStatus(data.message === 'order_created' ? `下单成功，共 ${data.total_items} 件` : '下单失败')
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Snack Store MVP</p>
          <h1>零食小铺</h1>
          <p>React 前端 + FastAPI 后端，支持商品列表、购物车和下单。</p>
        </div>
      </header>

      <main className="layout">
        <section>
          <h2>商品列表</h2>
          <div className="grid">
            {products.map((item) => (
              <article className="card" key={item.id}>
                <span className="emoji">{item.image}</span>
                <h3>{item.name}</h3>
                <p>价格：¥{item.price}</p>
                <p>库存：{item.stock}</p>
                <button onClick={() => addToCart(item)}>加入购物车</button>
              </article>
            ))}
          </div>
        </section>

        <aside className="cart">
          <h2>购物车</h2>
          <ul>
            {cart.map((item, index) => (
              <li key={`${item.id}-${index}`}>{item.name} - ¥{item.price}</li>
            ))}
          </ul>
          <p className="total">合计：¥{total}</p>
          <div className="cart-actions">
            <button disabled={!cart.length} onClick={checkout}>立即下单</button>
            <button type="button" disabled={!cart.length} onClick={clearCart}>清空购物车</button>
          </div>
          <p className="status">{status}</p>
        </aside>
      </main>
    </div>
  )
}
