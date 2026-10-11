<script setup lang="ts">
import type { BadgeProps } from '@nuxt/ui'
import { useSiteStore } from '~/stores/site'
import type { Order } from '~/types/catalog'

const route = useRoute()
const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()
const site = useSiteStore()
const { formatIn } = useMoney()

const token = String(route.params.token)
const { data: order, error } = await useAsyncData(`order:${token}`, () => api<Order>(`/orders/${token}`), {
  watch: [locale],
})

if (error.value || !order.value) {
  throw createError({ statusCode: 404, statusMessage: 'Order not found', fatal: true })
}

const statusColor: Record<string, BadgeProps['color']> = {
  new: 'info',
  confirmed: 'primary',
  paid: 'success',
  shipped: 'warning',
  completed: 'success',
  cancelled: 'error',
}

/** Сумма в валюте покупателя по курсу, зафиксированному в момент заказа. */
function money(amountUsd: string | null | undefined) {
  if (amountUsd === null || amountUsd === undefined || !order.value) return ''
  return formatIn(Number(amountUsd) * Number(order.value.exchange_rate), order.value.currency)
}

const message = computed(() => t('order.contactMessage', { number: order.value?.number }))
const telegramLink = computed(() => site.telegramLink(message.value))
const whatsappLink = computed(() => site.whatsappLink(message.value))

useSeoMeta({ title: () => t('order.title', { number: order.value?.number }), robots: 'noindex' })
</script>

<template>
  <UContainer v-if="order" class="max-w-3xl py-16">
    <div class="text-center">
      <UIcon name="i-lucide-circle-check" class="size-12 text-gold-500" />
      <h1 class="mt-4 font-serif text-4xl md:text-5xl">{{ t('order.thanks') }}</h1>
      <p class="mt-3 text-muted">{{ t('order.managerWillContact') }}</p>
      <div class="mt-6 flex items-center justify-center gap-3">
        <span class="text-lg">{{ t('order.number') }} <strong>{{ order.number }}</strong></span>
        <UBadge :label="order.status_label" :color="statusColor[order.status]" variant="soft" />
      </div>
    </div>

    <section class="mt-12 bg-elevated p-6">
      <ul class="divide-y divide-default">
        <li v-for="item in order.items" :key="item.name + item.reference" class="flex justify-between gap-4 py-3">
          <div>
            <p>{{ item.brand }} {{ item.name }}<template v-if="item.quantity > 1"> × {{ item.quantity }}</template></p>
            <p v-if="item.reference" class="text-xs text-muted">{{ t('product.ref') }} {{ item.reference }}</p>
            <p v-if="item.on_order" class="text-xs text-muted">{{ t('cart.onOrder', { days: item.lead_time_days }) }}</p>
          </div>
          <span class="shrink-0">{{ money(String(Number(item.price) * item.quantity)) }}</span>
        </li>
      </ul>
      <USeparator class="my-4" />
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span>{{ order.delivery_method }}</span>
          <span>{{ order.delivery_price !== null ? money(order.delivery_price) : t('checkout.byManager') }}</span>
        </div>
        <div class="flex justify-between text-lg">
          <span>{{ t('checkout.total') }}</span>
          <span class="font-medium">{{ money(order.total) }}</span>
        </div>
      </div>
    </section>

    <div v-if="telegramLink || whatsappLink" class="mt-8 flex flex-col gap-3 sm:flex-row">
      <UButton v-if="telegramLink" :to="telegramLink" target="_blank" :label="t('order.writeTelegram')" icon="i-lucide-send" color="neutral" size="xl" block class="flex-1 bg-ink text-gold-500 hover:bg-stone-800" />
      <UButton v-if="whatsappLink" :to="whatsappLink" target="_blank" :label="t('order.writeWhatsapp')" icon="i-lucide-message-circle" color="neutral" variant="outline" size="xl" block class="flex-1" />
    </div>
    <p class="mt-6 text-center text-sm text-muted">{{ t('order.bookmark') }}</p>
    <div class="mt-8 text-center">
      <UButton :to="localePath('/watches')" :label="t('order.continue')" variant="link" color="neutral" />
    </div>
  </UContainer>
</template>
