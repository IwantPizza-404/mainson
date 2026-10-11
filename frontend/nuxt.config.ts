import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: ['@nuxtjs/i18n', '@pinia/nuxt', '@nuxt/image', '@nuxt/eslint'],

  css: ['~/assets/css/main.css'],

  vite: {
    plugins: [tailwindcss()],
  },

  runtimeConfig: {
    // Адрес API для серверного рендеринга (внутри сети) — NUXT_API_BASE
    apiBase: 'http://localhost:8000/api/v1',
    public: {
      // Адрес API для браузера — NUXT_PUBLIC_API_BASE
      apiBase: 'http://localhost:8000/api/v1',
      siteUrl: 'https://maison.uz',
    },
  },

  i18n: {
    baseUrl: 'https://maison.uz',
    defaultLocale: 'en',
    strategy: 'prefix_except_default',
    langDir: 'locales',
    locales: [
      { code: 'en', language: 'en-US', name: 'English', file: 'en.json' },
      { code: 'uz', language: 'uz-Latn-UZ', name: 'O‘zbekcha', file: 'uz.json' },
      { code: 'ru', language: 'ru-RU', name: 'Русский', file: 'ru.json' },
    ],
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'maison_locale',
      redirectOn: 'root',
    },
  },

  app: {
    head: {
      titleTemplate: '%s · Maison',
    },
  },

  typescript: {
    strict: true,
  },
})
