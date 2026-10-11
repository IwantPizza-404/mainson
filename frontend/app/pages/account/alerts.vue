<script setup lang="ts">
import type { StockAlert } from '~/types/catalog'

const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()

const { data: alerts, refresh } = await useAsyncData('account-alerts', () => api<StockAlert[]>('/account/alerts'), {
  default: () => [],
})

async function remove(id: number) {
  await api(`/account/alerts/${id}`, { method: 'DELETE' })
  await refresh()
}

const link = (alert: StockAlert) => localePath(alert.kind === 'product' ? `/watches/${alert.product_slug}` : `/brands/${alert.brand_slug}`)
const date = (value: string) => new Date(value).toLocaleDateString(locale.value, { day: 'numeric', month: 'long' })
useSeoMeta({ title: () => t('account.nav.alerts') })
</script>

<template>
  <div>
    <h2 class="font-serif text-2xl">{{ t('account.nav.alerts') }}</h2>
    <p class="mt-2 text-sm text-muted">{{ t('account.alerts.hint') }}</p>

    <ul v-if="alerts.length" class="mt-6 divide-y divide-default">
      <li v-for="alert in alerts" :key="alert.id" class="flex items-center justify-between gap-4 py-4">
        <div>
          <NuxtLink :to="link(alert)" class="font-medium hover:underline">{{ alert.title }}</NuxtLink>
          <p class="text-sm text-muted">
            {{ alert.kind === 'product' ? t('account.alerts.product') : t('account.alerts.brand') }} · {{ date(alert.created_at) }}
          </p>
        </div>
        <UButton :label="t('account.alerts.unsubscribe')" variant="link" color="neutral" @click="remove(alert.id)" />
      </li>
    </ul>
    <UEmpty v-else icon="i-lucide-bell" :title="t('account.alerts.empty')" :description="t('account.alerts.emptyHint')" class="py-16" />
  </div>
</template>
