/**
 * Клиент API бэкенда. На сервере ходит по внутреннему адресу, в браузере — по публичному.
 * Язык интерфейса передаётся в Accept-Language, чтобы API отдавал переводы.
 */
export function useApi() {
  const config = useRuntimeConfig()
  const { $i18n } = useNuxtApp()

  return $fetch.create({
    baseURL: import.meta.server ? config.apiBase : config.public.apiBase,
    onRequest({ options }) {
      options.headers.set('Accept-Language', $i18n.locale.value)
    },
  })
}
