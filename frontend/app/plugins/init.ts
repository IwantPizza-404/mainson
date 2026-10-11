import { useAuthStore } from '~/stores/auth'
import { useCurrencyStore } from '~/stores/currency'
import { useSiteStore } from '~/stores/site'
import { useWishlistStore } from '~/stores/wishlist'

// Общие данные грузятся один раз при SSR и попадают в браузер вместе с состоянием Pinia.
// Бренды и настройки зависят от языка — перезагружаем их при его смене.
export default defineNuxtPlugin(async (nuxtApp) => {
  const site = useSiteStore()
  const auth = useAuthStore()
  // Покупателя грузим, только если есть cookie сессии — гостям лишний запрос не нужен
  const hasSession = import.meta.server && !!useRequestHeaders(['cookie']).cookie?.includes('maison_session=')
  // Избранное вошедшего — сразу после покупателя: счётчик в шапке верный уже при SSR.
  // После await контекст Nuxt теряется — поэтому стор берём заранее, а запрос — через runWithContext
  const wishlist = useWishlistStore()
  const loadCustomer = async () => {
    await auth.load()
    if (auth.isLoggedIn) await nuxtApp.runWithContext(() => wishlist.loadAccount())
  }
  await callOnce('init', () =>
    Promise.all([useCurrencyStore().load(), site.load(), hasSession ? loadCustomer() : Promise.resolve()]),
  )

  nuxtApp.hook('i18n:localeSwitched', () => site.load())
})
