import { defineStore } from 'pinia'
import type { Brand, SiteSettings } from '~/types/catalog'

/** Настройки сайта (контакты, соцсети) и бренды для меню — грузятся один раз при SSR. */
export const useSiteStore = defineStore('site', () => {
  const settings = ref<SiteSettings | null>(null)
  const brands = ref<Brand[]>([])

  async function load() {
    const api = useApi()
    const [settingsResult, brandsResult] = await Promise.allSettled([
      api<SiteSettings>('/content/settings'),
      api<Brand[]>('/catalog/brands'),
    ])
    if (settingsResult.status === 'fulfilled') settings.value = settingsResult.value
    if (brandsResult.status === 'fulfilled') brands.value = brandsResult.value
  }

  const telegramLink = (text?: string) =>
    settings.value?.telegram_username
      ? `https://t.me/${settings.value.telegram_username}${text ? `?text=${encodeURIComponent(text)}` : ''}`
      : null

  const whatsappLink = (text?: string) =>
    settings.value?.whatsapp_number
      ? `https://wa.me/${settings.value.whatsapp_number}${text ? `?text=${encodeURIComponent(text)}` : ''}`
      : null

  return { settings, brands, load, telegramLink, whatsappLink }
})
