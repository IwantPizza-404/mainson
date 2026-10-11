<script setup lang="ts">
import { useSiteStore } from '~/stores/site'

const { t } = useI18n()
const localePath = useLocalePath()
const site = useSiteStore()
const year = new Date().getFullYear()

const shopLinks = computed(() => [
  { label: t('nav.watches'), to: localePath('/watches') },
  { label: t('nav.brands'), to: localePath('/brands') },
  { label: t('menu.new'), to: localePath({ path: '/watches', query: { condition: 'new' } }) },
  { label: t('nav.preowned'), to: localePath({ path: '/watches', query: { condition: 'pre_owned' } }) },
])

const socials = computed(() => {
  const s = site.settings
  if (!s) return []
  return [
    { icon: 'i-simple-icons-instagram', label: 'Instagram', to: s.instagram_url },
    { icon: 'i-simple-icons-telegram', label: 'Telegram', to: s.telegram_channel_url },
    { icon: 'i-simple-icons-facebook', label: 'Facebook', to: s.facebook_url },
    { icon: 'i-simple-icons-youtube', label: 'YouTube', to: s.youtube_url },
  ].filter((item) => item.to)
})

// Страницы из админки по колонкам подвала + постоянные ссылки
const customerLinks = computed(() => [
  ...site.pages.filter((p) => p.footer_group === 'customers').map((p) => ({ label: p.title, to: localePath(`/${p.slug}`) })),
  { label: t('faq.title'), to: localePath('/faq') },
  { label: t('track.title'), to: localePath('/track') },
])
const aboutLinks = computed(() => [
  ...site.pages.filter((p) => p.footer_group === 'about').map((p) => ({ label: p.title, to: localePath(`/${p.slug}`) })),
  { label: t('contacts.title'), to: localePath('/contacts') },
])
const legalLinks = computed(() =>
  site.pages.filter((p) => p.footer_group === 'legal').map((p) => ({ label: p.title, to: localePath(`/${p.slug}`) })),
)

const telegram = computed(() => site.telegramLink())
const whatsapp = computed(() => site.whatsappLink())
</script>

<template>
  <footer class="mt-24 bg-ink text-white/70">
    <UContainer class="grid gap-10 py-16 sm:grid-cols-2 lg:grid-cols-5">
      <div>
        <NuxtLink :to="localePath('/')" class="font-serif text-2xl tracking-[0.3em] text-gold-500">MAISON</NuxtLink>
        <p class="mt-4 text-sm">{{ t('home.subtitle') }}</p>
        <div v-if="socials.length" class="mt-6 flex gap-2">
          <UButton
            v-for="item in socials"
            :key="item.label"
            :to="item.to"
            target="_blank"
            :icon="item.icon"
            :aria-label="item.label"
            variant="ghost"
            class="text-white/70 hover:bg-white/10 hover:text-gold-500"
          />
        </div>
      </div>

      <nav>
        <p class="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-white">{{ t('footer.shop') }}</p>
        <ul class="space-y-2 text-sm">
          <li v-for="link in shopLinks" :key="link.label">
            <NuxtLink :to="link.to" class="hover:text-gold-500">{{ link.label }}</NuxtLink>
          </li>
        </ul>
      </nav>

      <nav>
        <p class="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-white">{{ t('footer.customers') }}</p>
        <ul class="space-y-2 text-sm">
          <li v-for="link in customerLinks" :key="link.to">
            <NuxtLink :to="link.to" class="hover:text-gold-500">{{ link.label }}</NuxtLink>
          </li>
        </ul>
      </nav>

      <nav>
        <p class="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-white">{{ t('footer.about') }}</p>
        <ul class="space-y-2 text-sm">
          <li v-for="link in aboutLinks" :key="link.to">
            <NuxtLink :to="link.to" class="hover:text-gold-500">{{ link.label }}</NuxtLink>
          </li>
        </ul>
      </nav>

      <div>
        <p class="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-white">{{ t('footer.contacts') }}</p>
        <ul class="space-y-2 text-sm">
          <li v-if="site.settings?.phone">
            <a :href="`tel:${site.settings.phone.replace(/[^\d+]/g, '')}`" class="hover:text-gold-500">{{ site.settings.phone }}</a>
          </li>
          <li v-if="site.settings?.email">
            <a :href="`mailto:${site.settings.email}`" class="hover:text-gold-500">{{ site.settings.email }}</a>
          </li>
          <li v-if="telegram"><a :href="telegram" target="_blank" rel="noopener" class="hover:text-gold-500">Telegram</a></li>
          <li v-if="whatsapp"><a :href="whatsapp" target="_blank" rel="noopener" class="hover:text-gold-500">WhatsApp</a></li>
          <li v-if="site.settings?.address" class="pt-2">{{ site.settings.address }}</li>
          <li v-if="site.settings?.working_hours">{{ site.settings.working_hours }}</li>
        </ul>
      </div>

    </UContainer>
    <div class="border-t border-white/10">
      <UContainer class="flex flex-wrap items-center justify-between gap-4 py-6 text-xs">
        <span>© {{ year }} Maison. {{ t('footer.rights') }}</span>
        <nav v-if="legalLinks.length" class="flex flex-wrap gap-x-6 gap-y-2">
          <NuxtLink v-for="link in legalLinks" :key="link.to" :to="link.to" class="hover:text-gold-500">{{ link.label }}</NuxtLink>
        </nav>
      </UContainer>
    </div>
  </footer>
</template>
