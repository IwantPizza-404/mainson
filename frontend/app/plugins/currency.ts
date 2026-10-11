import { useCurrencyStore } from '~/stores/currency'

// Курсы грузятся один раз при SSR и попадают в браузер вместе с состоянием Pinia
export default defineNuxtPlugin(async () => {
  await callOnce('currency-rates', () => useCurrencyStore().load())
})
