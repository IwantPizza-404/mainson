import { defineStore } from 'pinia'

export interface CartItem {
  slug: string
  quantity: number
}

/**
 * Корзина хранится в cookie (доступна и при SSR) и содержит только slug и количество.
 * Цены и наличие всегда берутся с сервера через /cart/quote.
 */
export const useCartStore = defineStore('cart', () => {
  const items = useCookie<CartItem[]>('maison_cart', {
    default: () => [],
    maxAge: 60 * 60 * 24 * 30,
    sameSite: 'lax',
  })

  const count = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))

  function has(slug: string) {
    return items.value.some((item) => item.slug === slug)
  }

  function add(slug: string, quantity = 1) {
    const existing = items.value.find((item) => item.slug === slug)
    items.value = existing
      ? items.value.map((item) => (item.slug === slug ? { ...item, quantity: item.quantity + quantity } : item))
      : [...items.value, { slug, quantity }]
  }

  function setQuantity(slug: string, quantity: number) {
    items.value = items.value.map((item) => (item.slug === slug ? { ...item, quantity } : item))
  }

  function remove(slug: string) {
    items.value = items.value.filter((item) => item.slug !== slug)
  }

  function clear() {
    items.value = []
  }

  return { items, count, has, add, setQuantity, remove, clear }
})
