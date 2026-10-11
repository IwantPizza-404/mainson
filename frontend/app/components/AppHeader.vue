<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'
import { useCartStore } from '~/stores/cart'
import { useSiteStore } from '~/stores/site'

const { t } = useI18n()
const localePath = useLocalePath()
const cart = useCartStore()
const site = useSiteStore()

const watches = (query: Record<string, string> = {}) => localePath({ path: '/watches', query })

// Колонки мега-меню «Часы»
const menuColumns = computed(() => [
  {
    title: t('menu.forWhom'),
    links: [
      { label: t('menu.men'), to: watches({ gender: 'men' }) },
      { label: t('menu.women'), to: watches({ gender: 'women' }) },
      { label: t('menu.unisex'), to: watches({ gender: 'unisex' }) },
    ],
  },
  {
    title: t('menu.collections'),
    links: [
      { label: t('menu.all'), to: watches() },
      { label: t('menu.new'), to: watches({ condition: 'new' }) },
      { label: t('nav.preowned'), to: watches({ condition: 'pre_owned' }) },
      { label: t('menu.inStock'), to: watches({ availability: 'in_stock' }) },
      { label: t('menu.onOrder'), to: watches({ availability: 'on_order' }) },
    ],
  },
])

const topBrands = computed(() => site.brands.slice(0, 12))

const links = computed<NavigationMenuItem[]>(() => [
  { label: t('nav.watches'), to: watches(), slot: 'watches' as const },
  { label: t('nav.brands'), to: localePath('/brands') },
  { label: t('nav.preowned'), to: watches({ condition: 'pre_owned' }) },
])

// Мобильное меню — простой вертикальный список
const mobileLinks = computed<NavigationMenuItem[]>(() => [
  { label: t('nav.watches'), to: watches(), children: menuColumns.value.flatMap((c) => c.links) },
  {
    label: t('nav.brands'),
    to: localePath('/brands'),
    children: site.brands.map((b) => ({ label: b.name, to: localePath(`/brands/${b.slug}`) })),
  },
  { label: t('nav.preowned'), to: watches({ condition: 'pre_owned' }) },
])

const announcementLink = useSiteLink()
</script>

<template>
  <div>
    <!-- Строка объявления (настраивается в админке) -->
    <div v-if="site.settings?.announcement" class="bg-gold-500 px-4 py-2 text-center text-xs uppercase tracking-[0.18em] text-ink">
      <NuxtLink v-if="site.settings.announcement_link" :to="announcementLink(site.settings.announcement_link)" class="hover:underline">
        {{ site.settings.announcement }}
      </NuxtLink>
      <span v-else>{{ site.settings.announcement }}</span>
    </div>

    <UHeader
      :to="localePath('/')"
      :ui="{
        root: 'bg-ink border-none text-white',
        toggle: 'text-white',
        content: 'bg-ink',
      }"
    >
      <template #title>
        <span class="font-serif text-2xl tracking-[0.3em] text-gold-500">MAISON</span>
      </template>

      <UNavigationMenu
        :items="links"
        :ui="{
          link: 'text-xs uppercase tracking-[0.2em] text-white/80 hover:text-gold-500 data-active:text-gold-500',
          viewport: 'sm:w-(--reka-navigation-menu-viewport-width)',
          content: 'w-full sm:w-auto',
        }"
      >
        <template #watches-content>
          <div class="grid w-[min(90vw,52rem)] grid-cols-3 gap-8 p-8">
            <div class="col-span-1">
              <p class="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-muted">{{ t('nav.brands') }}</p>
              <ul class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                <li v-for="brand in topBrands" :key="brand.slug">
                  <NuxtLink :to="localePath(`/brands/${brand.slug}`)" class="hover:text-gold-700">{{ brand.name }}</NuxtLink>
                </li>
              </ul>
              <NuxtLink :to="localePath('/brands')" class="mt-4 inline-block text-xs uppercase tracking-wider underline">
                {{ t('brands.all') }}
              </NuxtLink>
            </div>
            <div v-for="column in menuColumns" :key="column.title">
              <p class="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-muted">{{ column.title }}</p>
              <ul class="space-y-2 text-sm">
                <li v-for="item in column.links" :key="item.label">
                  <NuxtLink :to="item.to" class="hover:text-gold-700">{{ item.label }}</NuxtLink>
                </li>
              </ul>
            </div>
          </div>
        </template>
      </UNavigationMenu>

      <template #right>
        <CurrencySwitcher />
        <LanguageSwitcher />
        <UChip :text="cart.count" :show="cart.count > 0" size="3xl" color="primary" inset>
          <UButton
            :to="localePath('/cart')"
            icon="i-lucide-shopping-bag"
            :aria-label="t('cart.title')"
            variant="ghost"
            class="text-white hover:bg-white/10"
          />
        </UChip>
      </template>

      <template #body>
        <UNavigationMenu :items="mobileLinks" orientation="vertical" class="-mx-2.5" />
      </template>
    </UHeader>
  </div>
</template>
