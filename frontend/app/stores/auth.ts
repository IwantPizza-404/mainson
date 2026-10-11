import { defineStore } from 'pinia'
import type { AuthCustomer } from '~/types/catalog'

/** Вошедший покупатель. Загружается при SSR, если в запросе есть cookie сессии. */
export const useAuthStore = defineStore('auth', () => {
  const customer = ref<AuthCustomer | null>(null)
  const isLoggedIn = computed(() => customer.value !== null)

  async function load() {
    try {
      customer.value = await useApi()<AuthCustomer>('/account/me')
    } catch {
      customer.value = null // 401 — не вошёл
    }
  }

  async function logout() {
    await useApi()('/auth/logout', { method: 'POST' }).catch(() => {})
    customer.value = null
  }

  return { customer, isLoggedIn, load, logout, set: (value: AuthCustomer) => (customer.value = value) }
})
