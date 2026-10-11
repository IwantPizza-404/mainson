<script setup lang="ts">
import type { OrderSummary } from '~/types/catalog'

const { t } = useI18n()
const api = useApi()
const localePath = useLocalePath()

const { data: orders } = await useAsyncData('account-orders', () => api<OrderSummary[]>('/account/orders'), { default: () => [] })
useSeoMeta({ title: () => t('account.nav.orders') })
</script>

<template>
  <div>
    <h2 class="font-serif text-2xl">{{ t('account.nav.orders') }}</h2>
    <div v-if="orders.length" class="mt-4 divide-y divide-default">
      <AccountOrderRow v-for="order in orders" :key="order.number" :order="order" />
    </div>
    <UEmpty
      v-else
      icon="i-lucide-package"
      :title="t('account.orders.empty')"
      :actions="[{ label: t('menu.all'), to: localePath('/watches'), color: 'neutral', variant: 'outline' }]"
      class="py-16"
    />
  </div>
</template>
