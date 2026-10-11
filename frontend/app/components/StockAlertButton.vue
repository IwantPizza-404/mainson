<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { StockAlert } from '~/types/catalog'

/** «Сообщить о поступлении»: подписка на модель (product) или на новинки бренда (brand). */
const props = defineProps<{ product?: string; brand?: string; label: string }>()

const { t } = useI18n()
const api = useApi()
const route = useRoute()
const toast = useToast()
const localePath = useLocalePath()
const auth = useAuthStore()

const subscribed = ref(false)
const loading = ref(false)

// Вошедшему покупателю показываем, подписан ли он уже
onMounted(async () => {
  if (!auth.isLoggedIn) return
  const alerts = await api<StockAlert[]>('/account/alerts').catch(() => [])
  subscribed.value = alerts.some((a) => (props.product ? a.product_slug === props.product : a.brand_slug === props.brand))
})

async function subscribe() {
  if (!auth.isLoggedIn) {
    return navigateTo(localePath({ path: '/login', query: { redirect: route.fullPath } }))
  }
  loading.value = true
  try {
    await api('/account/alerts', { method: 'POST', body: props.product ? { product: props.product } : { brand: props.brand } })
    subscribed.value = true
    toast.add({
      title: t('alerts.subscribed'),
      description: auth.customer?.has_telegram ? t('alerts.viaTelegram') : t('alerts.connectTelegram'),
      icon: 'i-lucide-bell',
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UButton
    :label="subscribed ? t('alerts.active') : label"
    :icon="subscribed ? 'i-lucide-bell-ring' : 'i-lucide-bell'"
    :loading="loading"
    :disabled="subscribed"
    variant="outline"
    color="neutral"
    size="xl"
    block
    @click="subscribe"
  />
</template>
