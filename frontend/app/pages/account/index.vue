<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useWishlistStore } from '~/stores/wishlist'
import type { OrderSummary } from '~/types/catalog'

const { t } = useI18n()
const api = useApi()
const localePath = useLocalePath()
const auth = useAuthStore()
const wishlist = useWishlistStore()

const { data: orders } = await useAsyncData('account-orders', () => api<OrderSummary[]>('/account/orders'), { default: () => [] })

const cards = computed(() => [
  { icon: 'i-lucide-heart', title: t('account.nav.wishlist'), text: t('account.overview.wishlist', { n: wishlist.count }), to: '/wishlist' },
  { icon: 'i-lucide-watch', title: t('account.nav.collection'), text: t('account.overview.collection'), to: '/account/collection' },
  { icon: 'i-lucide-bell', title: t('account.nav.alerts'), text: t('account.overview.alerts'), to: '/account/alerts' },
  { icon: 'i-lucide-search', title: t('account.nav.requests'), text: t('account.overview.requests'), to: '/account/requests' },
])
</script>

<template>
  <div class="space-y-10">
    <UAlert
      v-if="auth.customer && !auth.customer.has_telegram"
      :title="t('account.overview.telegramHint')"
      icon="i-simple-icons-telegram"
      color="neutral"
      variant="soft"
    />

    <section>
      <div class="mb-2 flex items-end justify-between">
        <h2 class="font-serif text-2xl">{{ t('account.overview.lastOrders') }}</h2>
        <UButton v-if="orders.length > 3" :to="localePath('/account/orders')" :label="t('home.viewAll')" variant="link" color="neutral" />
      </div>
      <div v-if="orders.length" class="divide-y divide-default">
        <AccountOrderRow v-for="order in orders.slice(0, 3)" :key="order.number" :order="order" />
      </div>
      <p v-else class="py-6 text-muted">{{ t('account.orders.empty') }}</p>
    </section>

    <section class="grid gap-4 sm:grid-cols-2">
      <NuxtLink
        v-for="card in cards"
        :key="card.to"
        :to="localePath(card.to)"
        class="flex gap-4 border border-default p-6 transition-colors hover:border-gold-500"
      >
        <UIcon :name="card.icon" class="size-6 shrink-0 text-gold-600" />
        <div>
          <p class="font-medium">{{ card.title }}</p>
          <p class="mt-1 text-sm text-muted">{{ card.text }}</p>
        </div>
      </NuxtLink>
    </section>
  </div>
</template>
