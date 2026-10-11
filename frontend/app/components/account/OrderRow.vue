<script setup lang="ts">
import type { BadgeProps } from '@nuxt/ui'
import type { OrderSummary } from '~/types/catalog'

defineProps<{ order: OrderSummary }>()

const { t, locale } = useI18n()
const localePath = useLocalePath()
const { formatIn } = useMoney()

const statusColor: Record<string, BadgeProps['color']> = {
  new: 'info',
  confirmed: 'primary',
  paid: 'success',
  shipped: 'warning',
  completed: 'success',
  cancelled: 'error',
}
const date = (value: string) =>
  new Date(value).toLocaleDateString(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })
</script>

<template>
  <NuxtLink :to="localePath(`/order/${order.token}`)" class="flex flex-wrap items-center justify-between gap-4 py-4 hover:bg-elevated">
    <div>
      <p class="font-medium">{{ order.number }}</p>
      <p class="text-sm text-muted">{{ date(order.created_at) }} · {{ t('account.items', { n: order.items_count }) }}</p>
    </div>
    <div class="flex items-center gap-4">
      <span>{{ formatIn(Number(order.total) * Number(order.exchange_rate), order.currency) }}</span>
      <UBadge :label="order.status_label" :color="statusColor[order.status]" variant="soft" />
    </div>
  </NuxtLink>
</template>
