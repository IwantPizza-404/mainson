<script setup lang="ts">
import type { BadgeProps } from '@nuxt/ui'
import type { WatchRequest } from '~/types/catalog'

const { t, locale } = useI18n()
const api = useApi()
const route = useRoute()
const toast = useToast()

const { data: requests, refresh } = await useAsyncData('account-requests', () => api<WatchRequest[]>('/account/requests'), {
  default: () => [],
})
// Форма открыта сразу, если пришли из поиска («Не нашли? Найдём для вас»)
const formOpen = ref(!!route.query.q || !requests.value.length)

async function onCreated() {
  formOpen.value = false
  toast.add({ title: t('requests.sent'), description: t('requests.sentHint'), icon: 'i-lucide-check' })
  await refresh()
}

const statusColor: Record<string, BadgeProps['color']> = { new: 'info', searching: 'warning', offered: 'success', closed: 'neutral' }
const date = (value: string) => new Date(value).toLocaleDateString(locale.value, { day: 'numeric', month: 'long' })
const { format } = useMoney()
useSeoMeta({ title: () => t('account.nav.requests') })
</script>

<template>
  <div class="space-y-8">
    <div>
      <div class="flex items-end justify-between gap-4">
        <h2 class="font-serif text-2xl">{{ t('account.nav.requests') }}</h2>
        <UButton v-if="!formOpen" :label="t('requests.new')" icon="i-lucide-plus" variant="link" color="neutral" @click="formOpen = true" />
      </div>
      <p class="mt-2 text-sm text-muted">{{ t('requests.hint') }}</p>
    </div>

    <div v-if="formOpen" class="border border-default p-6">
      <AccountWatchRequestForm :initial-query="typeof route.query.q === 'string' ? route.query.q : undefined" @created="onCreated" />
    </div>

    <ul v-if="requests.length" class="divide-y divide-default">
      <li v-for="item in requests" :key="item.id" class="py-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <p class="font-medium">{{ [item.brand, item.model, item.reference].filter(Boolean).join(' ') }}</p>
          <UBadge :label="item.status_label" :color="statusColor[item.status]" variant="soft" />
        </div>
        <p class="mt-1 text-sm text-muted">
          {{ date(item.created_at) }}<template v-if="item.budget"> · {{ t('requests.budget') }}: {{ format(item.budget) }}</template>
        </p>
        <div v-if="item.reply" class="mt-3 border-l-2 border-gold-500 bg-elevated px-4 py-3 text-sm whitespace-pre-line">
          {{ item.reply }}
        </div>
      </li>
    </ul>
  </div>
</template>
