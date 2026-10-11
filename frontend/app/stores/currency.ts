import { defineStore } from 'pinia'

export const CURRENCIES = ['USD', 'UZS', 'EUR', 'RUB'] as const
export type Currency = (typeof CURRENCIES)[number]

/** Выбранная валюта отображения. Цены хранятся в USD, остальное — пересчёт по курсу. */
export const useCurrencyStore = defineStore('currency', () => {
  const cookie = useCookie<Currency>('maison_currency', {
    default: () => 'USD',
    maxAge: 60 * 60 * 24 * 365,
  })

  const current = computed(() => cookie.value)

  function set(currency: Currency) {
    cookie.value = currency
  }

  return { current, set }
})
