import { defineStore } from 'pinia'
import { useAuthStore } from '~/stores/auth'
import type { ProductListItem } from '~/types/catalog'

/**
 * Избранное. Гостю — в cookie браузера; после входа — в аккаунте (переносится автоматически).
 * Хранится только список slug, сами товары грузятся при открытии страницы избранного.
 */
export const useWishlistStore = defineStore('wishlist', () => {
  const auth = useAuthStore()
  const guest = useCookie<string[]>('maison_wishlist', { default: () => [], maxAge: 60 * 60 * 24 * 365, sameSite: 'lax' })
  const account = ref<string[]>([])
  const accountLoaded = ref(false)

  const slugs = computed(() => (auth.isLoggedIn ? account.value : guest.value))
  const count = computed(() => slugs.value.length)
  const has = (slug: string) => slugs.value.includes(slug)

  function applyServer(products: ProductListItem[]) {
    account.value = products.map((p) => p.slug)
    accountLoaded.value = true
    return products
  }

  async function loadAccount() {
    if (!auth.isLoggedIn || accountLoaded.value) return
    applyServer(await useApi()<ProductListItem[]>('/account/wishlist'))
  }

  async function toggle(slug: string) {
    if (!auth.isLoggedIn) {
      guest.value = has(slug) ? guest.value.filter((s) => s !== slug) : [...guest.value, slug]
      return
    }
    const api = useApi()
    if (has(slug)) {
      account.value = account.value.filter((s) => s !== slug)
      await api(`/account/wishlist/${slug}`, { method: 'DELETE' })
    } else {
      account.value = [...account.value, slug]
      applyServer(await api<ProductListItem[]>('/account/wishlist', { method: 'POST', body: { slug } }))
    }
  }

  /** После входа: гостевое избранное переносится в аккаунт. */
  async function syncAfterLogin() {
    const api = useApi()
    const products = guest.value.length
      ? await api<ProductListItem[]>('/account/wishlist/merge', { method: 'POST', body: { slugs: guest.value } })
      : await api<ProductListItem[]>('/account/wishlist')
    applyServer(products)
    guest.value = []
  }

  return { slugs, count, has, toggle, loadAccount, syncAfterLogin, applyServer }
})
