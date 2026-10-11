import { useCartStore } from '~/stores/cart'
import type { CartQuote } from '~/types/catalog'

/** Актуальный расчёт корзины с сервера: цены, наличие, ошибки по позициям. */
export function useCartQuote() {
  const api = useApi()
  const cart = useCartStore()
  const { locale } = useI18n()

  return useAsyncData(
    'cart-quote',
    () =>
      cart.items.length
        ? api<CartQuote>('/cart/quote', { method: 'POST', body: { items: cart.items } })
        : Promise.resolve<CartQuote>({ lines: [], subtotal: '0', is_valid: false }),
    { watch: [() => cart.items, locale], deep: true },
  )
}
