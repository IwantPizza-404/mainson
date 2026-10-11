import { defineStore } from 'pinia'
import type { components } from '~/types/api'

export const CURRENCIES = ['USD', 'UZS', 'EUR', 'RUB'] as const
export type Currency = (typeof CURRENCIES)[number]

/**
 * Выбранная валюта отображения и курсы относительно USD.
 * Цены приходят из API в USD; пересчёт — только для показа, заказ фиксируется в USD.
 */
export const useCurrencyStore = defineStore('currency', () => {
  const cookie = useCookie<Currency>('maison_currency', {
    default: () => 'USD',
    maxAge: 60 * 60 * 24 * 365,
  })

  // Сколько единиц валюты за 1 USD
  const rates = ref<Partial<Record<Currency, number>>>({ USD: 1 })

  async function load() {
    try {
      const data = await useApi()<components['schemas']['RatesOut']>('/currency/rates')
      rates.value = Object.fromEntries(Object.entries(data.rates).map(([code, rate]) => [code, Number(rate)]))
    } catch (error) {
      // Без курсов витрина продолжает работать в USD
      console.error('Failed to load exchange rates', error)
    }
  }

  const current = computed<Currency>(() => (rates.value[cookie.value] ? cookie.value : 'USD'))

  function set(currency: Currency) {
    cookie.value = currency
  }

  function convert(amountUsd: number): number {
    return amountUsd * (rates.value[current.value] ?? 1)
  }

  return { current, rates, set, convert, load }
})
