<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

import { useCartStore } from '~/stores/cart'

const { t } = useI18n()
const localePath = useLocalePath()
const cart = useCartStore()

const links = computed<NavigationMenuItem[]>(() => [
  { label: t('nav.watches'), to: localePath('/watches') },
  { label: t('nav.preowned'), to: localePath({ path: '/watches', query: { condition: 'pre_owned' } }) },
])
</script>

<template>
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
      :ui="{ link: 'text-xs uppercase tracking-[0.2em] text-white/80 hover:text-gold-500 data-active:text-gold-500' }"
    />

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
      <UNavigationMenu :items="links" orientation="vertical" class="-mx-2.5" />
    </template>
  </UHeader>
</template>
