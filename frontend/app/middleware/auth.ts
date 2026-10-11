import { useAuthStore } from '~/stores/auth'

/** Страницы кабинета — только для вошедших; иначе на вход с возвратом обратно. */
export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (!auth.isLoggedIn) {
    const localePath = useLocalePath()
    return navigateTo(localePath({ path: '/login', query: { redirect: to.fullPath } }))
  }
})
