import {
  startTransition,
  useDeferredValue,
  useEffect,
  useMemo,
  useState,
} from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const FREE_SHIPPING_THRESHOLD = 69

function currency(value) {
  return `¥${value}`
}

function spicyLabel(level) {
  if (level <= 0) return '不辣'
  if (level === 1) return '微辣'
  if (level === 2) return '小辣'
  return '香辣'
}

export default function App() {
  const [catalog, setCatalog] = useState([])
  const [catalogTotal, setCatalogTotal] = useState(0)
  const [categories, setCategories] = useState([])
  const [spotlight, setSpotlight] = useState([])
  const [cart, setCart] = useState([])
  const [searchInput, setSearchInput] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('全部')
  const [sort, setSort] = useState('featured')
  const [featuredOnly, setFeaturedOnly] = useState(false)
  const [status, setStatus] = useState({ kind: '', text: '' })
  const [isCatalogLoading, setIsCatalogLoading] = useState(true)
  const [isCheckingOut, setIsCheckingOut] = useState(false)
  const [latestOrder, setLatestOrder] = useState(null)

  const deferredSearch = useDeferredValue(searchInput.trim())

  useEffect(() => {
    let cancelled = false

    async function loadMeta() {
      try {
        const resp = await fetch(`${API_BASE}/api/snacks/meta`)
        if (!resp.ok) throw new Error('meta_failed')
        const data = await resp.json()
        if (cancelled) return
        setCategories(data.categories || [])
        setSpotlight(data.spotlight || [])
      } catch {
        if (!cancelled) {
          setStatus({ kind: 'error', text: '商城信息加载失败，请稍后重试。' })
        }
      }
    }

    loadMeta()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const params = new URLSearchParams()

    if (selectedCategory !== '全部') {
      params.set('category', selectedCategory)
    }
    if (deferredSearch) {
      params.set('search', deferredSearch)
    }
    if (sort) {
      params.set('sort', sort)
    }
    if (featuredOnly) {
      params.set('featured', 'true')
    }

    async function loadCatalog() {
      setIsCatalogLoading(true)
      try {
        const suffix = params.toString() ? `?${params.toString()}` : ''
        const resp = await fetch(`${API_BASE}/api/snacks${suffix}`)
        if (!resp.ok) throw new Error('catalog_failed')
        const data = await resp.json()
        if (cancelled) return
        setCatalog(data.items || [])
        setCatalogTotal(data.total || 0)
        if (data.total === 0) {
          setStatus({ kind: 'info', text: '当前筛选下还没有匹配商品，试试换个分类或关键词。' })
        } else {
          setStatus((prev) => (
            prev.kind === 'error' ? prev : { kind: '', text: '' }
          ))
        }
      } catch {
        if (!cancelled) {
          setStatus({ kind: 'error', text: '商品加载失败，请检查后端服务是否已启动。' })
        }
      } finally {
        if (!cancelled) {
          setIsCatalogLoading(false)
        }
      }
    }

    loadCatalog()
    return () => {
      cancelled = true
    }
  }, [deferredSearch, featuredOnly, selectedCategory, sort])

  const cartCount = useMemo(
    () => cart.reduce((sum, item) => sum + item.quantity, 0),
    [cart]
  )
  const subtotal = useMemo(
    () => cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0),
    [cart]
  )
  const shippingFee = subtotal >= FREE_SHIPPING_THRESHOLD || subtotal === 0 ? 0 : 8
  const discount = subtotal >= 120 ? 12 : 0
  const total = subtotal + shippingFee - discount
  const remainingForFreeShipping = Math.max(FREE_SHIPPING_THRESHOLD - subtotal, 0)

  function addToCart(product) {
    setStatus({ kind: 'success', text: `${product.name} 已加入购物袋。` })
    setCart((prev) => {
      const existing = prev.find((item) => item.product.id === product.id)
      if (existing) {
        return prev.map((item) => (
          item.product.id === product.id
            ? { ...item, quantity: Math.min(item.quantity + 1, product.stock) }
            : item
        ))
      }
      return [...prev, { product, quantity: 1 }]
    })
  }

  function updateQuantity(productId, nextQuantity) {
    setCart((prev) => prev
      .map((item) => (
        item.product.id === productId
          ? {
              ...item,
              quantity: Math.max(0, Math.min(nextQuantity, item.product.stock)),
            }
          : item
      ))
      .filter((item) => item.quantity > 0))
  }

  function clearCart() {
    setCart([])
    setLatestOrder(null)
    setStatus({ kind: 'info', text: '购物袋已清空，可以重新挑选零食。' })
  }

  async function checkout() {
    if (!cart.length) return

    setIsCheckingOut(true)
    setStatus({ kind: '', text: '' })

    try {
      const resp = await fetch(`${API_BASE}/api/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: cart.map((item) => ({
            id: item.product.id,
            quantity: item.quantity,
          })),
        }),
      })

      const data = await resp.json()
      if (!resp.ok) {
        throw new Error(data.detail || '下单失败，请稍后重试。')
      }

      setLatestOrder(data)
      setCart([])
      setStatus({
        kind: 'success',
        text: `下单成功，订单 ${data.order_id} 已生成，预计 ${data.eta_minutes} 分钟内送达。`,
      })
    } catch (error) {
      setStatus({
        kind: 'error',
        text: error instanceof Error ? error.message : '下单失败，请稍后重试。',
      })
    } finally {
      setIsCheckingOut(false)
    }
  }

  const categoryTabs = useMemo(
    () => [{ name: '全部', count: catalogTotal }, ...categories],
    [catalogTotal, categories]
  )

  return (
    <div className="page-shell">
      <div className="page-noise" />
      <div className="page">
        <header className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Snack Store 2.0</p>
            <h1>零食小铺升级版</h1>
            <p className="hero-lead">
              不再只是一个商品列表和下单按钮，而是一套可以逛、可以筛、可以组合购买的网页版零食商城。
            </p>

            <div className="hero-search">
              <label className="search-box">
                <span>搜索零食、口味或场景</span>
                <input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="例如：抹茶、低卡、追剧"
                />
              </label>

              <div className="hero-actions">
                <button type="button" onClick={() => setFeaturedOnly((prev) => !prev)}>
                  {featuredOnly ? '查看全部商品' : '只看店长主推'}
                </button>
              </div>
            </div>

            <div className="hero-metrics">
              <div>
                <strong>{catalogTotal}</strong>
                <span>当前可选商品</span>
              </div>
              <div>
                <strong>{categories.length}</strong>
                <span>分类主题</span>
              </div>
              <div>
                <strong>{currency(FREE_SHIPPING_THRESHOLD)}</strong>
                <span>满额包邮门槛</span>
              </div>
            </div>
          </div>

          <div className="hero-panel">
            <p className="panel-title">今日零食路线</p>
            <ul className="panel-list">
              <li>先选分类和口味，缩小决策成本</li>
              <li>支持数量步进，购物袋更接近真实商城</li>
              <li>下单后返回订单摘要、运费和加购推荐</li>
            </ul>
          </div>
        </header>

        <section className="spotlight">
          <div className="section-heading">
            <div>
              <p className="section-kicker">主推清单</p>
              <h2>适合先逛的 3 款零食</h2>
            </div>
          </div>

          <div className="spotlight-grid">
            {spotlight.map((item) => (
              <article className="spotlight-card" key={item.id}>
                <div className="spotlight-topline">
                  <span className="spotlight-emoji">{item.image}</span>
                  <span className="badge">主推</span>
                </div>
                <h3>{item.name}</h3>
                <p>{item.description}</p>
                <div className="spotlight-meta">
                  <span>{item.category}</span>
                  <span>{item.rating.toFixed(1)} 分</span>
                  <span>{spicyLabel(item.spicy_level)}</span>
                </div>
                <button type="button" onClick={() => addToCart(item)}>
                  加入购物袋 {currency(item.price)}
                </button>
              </article>
            ))}
          </div>
        </section>

<<<<<<< HEAD
        <aside className="cart">
          <h2>购物车</h2>
          <ul>
            {cart.map((item, index) => (
              <li key={`${item.id}-${index}`}>{item.name} - ¥{item.price}</li>
            ))}
          </ul>
          <p className="cart-count">当前件数：{cart.length}</p>
          <p className="total">合计：¥{total}</p>
          <div className="cart-actions">
            <button disabled={!cart.length} onClick={checkout}>立即下单</button>
            <button type="button" disabled={!cart.length} onClick={clearCart}>清空购物车</button>
          </div>
          <p className="status">{status}</p>
        </aside>
      </main>
=======
        <main className="content">
          <section className="catalog-panel">
            <div className="filters">
              <div className="section-heading">
                <div>
                  <p className="section-kicker">筛选浏览</p>
                  <h2>按口味、分类和排序方式挑零食</h2>
                </div>
                <label className="sort-box">
                  <span>排序</span>
                  <select
                    value={sort}
                    onChange={(event) => {
                      const nextSort = event.target.value
                      startTransition(() => setSort(nextSort))
                    }}
                  >
                    <option value="featured">店长推荐</option>
                    <option value="rating">评分优先</option>
                    <option value="price_asc">价格从低到高</option>
                    <option value="price_desc">价格从高到低</option>
                    <option value="stock">库存充足优先</option>
                  </select>
                </label>
              </div>

              <div className="category-row">
                {categoryTabs.map((category) => (
                  <button
                    key={category.name}
                    type="button"
                    className={category.name === selectedCategory ? 'pill active' : 'pill'}
                    onClick={() => {
                      const nextCategory = category.name
                      startTransition(() => setSelectedCategory(nextCategory))
                    }}
                  >
                    <span>{category.name}</span>
                    <strong>{category.count}</strong>
                  </button>
                ))}
              </div>
            </div>

            {isCatalogLoading ? (
              <div className="empty-state">商品加载中，正在整理今日零食柜...</div>
            ) : (
              <div className="product-grid">
                {catalog.map((item) => (
                  <article className="product-card" key={item.id}>
                    <div className="product-top">
                      <span className="product-emoji">{item.image}</span>
                      <div className="product-badges">
                        {item.featured ? <span className="badge warm">主推</span> : null}
                        <span className="badge ghost">{spicyLabel(item.spicy_level)}</span>
                      </div>
                    </div>

                    <div className="product-copy">
                      <p className="product-category">{item.category}</p>
                      <h3>{item.name}</h3>
                      <p>{item.description}</p>
                    </div>

                    <div className="product-tags">
                      {item.tags.map((tag) => (
                        <span key={tag}>{tag}</span>
                      ))}
                    </div>

                    <div className="product-meta">
                      <span>{item.origin}</span>
                      <span>{item.rating.toFixed(1)} 分</span>
                      <span>库存 {item.stock}</span>
                    </div>

                    <div className="product-footer">
                      <div>
                        <strong>{currency(item.price)}</strong>
                        <span>每份</span>
                      </div>
                      <button type="button" onClick={() => addToCart(item)}>
                        加入购物袋
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          <aside className="cart-panel">
            <div className="cart-card">
              <div className="section-heading compact">
                <div>
                  <p className="section-kicker">购物袋</p>
                  <h2>{cartCount} 件待结算</h2>
                </div>
              </div>

              {cart.length ? (
                <ul className="cart-list">
                  {cart.map((item) => (
                    <li className="cart-item" key={item.product.id}>
                      <div>
                        <strong>{item.product.name}</strong>
                        <p>
                          {currency(item.product.price)} / 件
                          <span> · {item.product.category}</span>
                        </p>
                      </div>

                      <div className="quantity-stepper">
                        <button type="button" onClick={() => updateQuantity(item.product.id, item.quantity - 1)}>
                          -
                        </button>
                        <span>{item.quantity}</span>
                        <button type="button" onClick={() => updateQuantity(item.product.id, item.quantity + 1)}>
                          +
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="empty-state small">
                  购物袋还是空的。先从主推区或商品列表里挑几样试试看。
                </div>
              )}

              <div className="summary">
                <div>
                  <span>商品小计</span>
                  <strong>{currency(subtotal)}</strong>
                </div>
                <div>
                  <span>运费</span>
                  <strong>{shippingFee ? currency(shippingFee) : '免运费'}</strong>
                </div>
                <div>
                  <span>优惠</span>
                  <strong>{discount ? `-${currency(discount)}` : '暂无'}</strong>
                </div>
                <div className="summary-total">
                  <span>应付合计</span>
                  <strong>{currency(total)}</strong>
                </div>
              </div>

              <div className="shipping-hint">
                {remainingForFreeShipping > 0
                  ? `再买 ${currency(remainingForFreeShipping)} 即可包邮`
                  : '已达包邮门槛，适合顺手加购一款主推小食'}
              </div>

              <div className="cart-actions">
                <button
                  type="button"
                  className="primary"
                  disabled={!cart.length || isCheckingOut}
                  onClick={checkout}
                >
                  {isCheckingOut ? '正在生成订单...' : '立即结算'}
                </button>
                <button type="button" className="secondary" disabled={!cart.length} onClick={clearCart}>
                  清空购物袋
                </button>
              </div>

              {status.text ? (
                <p className={`status ${status.kind}`}>{status.text}</p>
              ) : null}
            </div>

            <div className="order-card">
              <p className="section-kicker">订单回执</p>
              {latestOrder ? (
                <>
                  <h3>{latestOrder.order_id}</h3>
                  <p>
                    共 {latestOrder.total_items} 件，预计 {latestOrder.eta_minutes} 分钟内送达。
                  </p>
                  <ul className="recommend-list">
                    {latestOrder.recommendations.map((item) => (
                      <li key={item.id}>
                        <span>{item.image}</span>
                        <div>
                          <strong>{item.name}</strong>
                          <p>{currency(item.price)} · {item.category}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <p className="muted">
                  完成下单后，这里会显示订单编号、送达时间和适合继续加购的推荐零食。
                </p>
              )}
            </div>
          </aside>
        </main>
      </div>
>>>>>>> 11e5607 (feat: expand snack store web experience)
    </div>
  )
}
