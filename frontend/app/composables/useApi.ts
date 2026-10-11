/**
 * Клиент API бэкенда. На сервере ходит по внутреннему адресу, в браузере — по публичному.
 * Язык интерфейса передаётся в Accept-Language, чтобы API отдавал переводы.
 *
 * Сессия покупателя — HttpOnly-cookie: при SSR пробрасываем её из запроса браузера,
 * в браузере отправляем с credentials (локально API на другом порту).
 */
export function useApi() {
  const config = useRuntimeConfig()
  const { $i18n } = useNuxtApp()
  const forwarded = import.meta.server ? useRequestHeaders(['cookie']) : {}

  return $fetch.create({
    baseURL: import.meta.server ? config.apiBase : config.public.apiBase,
    credentials: 'include',
    onRequest({ options }) {
      options.headers.set('Accept-Language', $i18n.locale.value)
      if (forwarded.cookie) options.headers.set('cookie', forwarded.cookie)
    },
  })
}
