import { useCurrencyStore } from '~/stores/currency'
import { useSiteStore } from '~/stores/site'

// Общие данные грузятся один раз при SSR и попадают в браузер вместе с состоянием Pinia.
// Бренды и настройки зависят от языка — перезагружаем их при его смене.
export default defineNuxtPlugin(async (nuxtApp) => {
  const site = useSiteStore()
  await callOnce('init', () => Promise.all([useCurrencyStore().load(), site.load()]))

  nuxtApp.hook('i18n:localeSwitched', () => site.load())
})
