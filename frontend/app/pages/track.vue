<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { z } from 'zod'

const { t } = useI18n()
const api = useApi()
const localePath = useLocalePath()

const schema = computed(() =>
  z.object({
    number: z.string().trim().min(4, t('checkout.errors.required')),
    phone: z.string().trim().min(7, t('checkout.errors.phone')),
  }),
)
type FormState = z.output<typeof schema.value>
const state = reactive<FormState>({ number: '', phone: '' })
const error = ref<string | null>(null)
const loading = ref(false)

async function onSubmit(event: FormSubmitEvent<FormState>) {
  loading.value = true
  error.value = null
  try {
    const { token } = await api<{ token: string }>('/orders/lookup', { method: 'POST', body: event.data })
    await navigateTo(localePath(`/order/${token}`))
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } }).response?.status
    error.value = status === 429 ? t('checkout.errors.tooMany') : t('track.notFound')
  } finally {
    loading.value = false
  }
}

useSeoMeta({ title: () => t('track.title'), robots: 'noindex' })
</script>

<template>
  <UContainer class="max-w-md py-16">
    <h1 class="font-serif text-4xl">{{ t('track.title') }}</h1>
    <p class="mt-3 text-muted">{{ t('track.hint') }}</p>
    <UForm :schema="schema" :state="state" class="mt-8 space-y-4" @submit="onSubmit">
      <UFormField :label="t('track.number')" name="number" required>
        <UInput v-model="state.number" placeholder="MS-123456" class="w-full" />
      </UFormField>
      <UFormField :label="t('checkout.phone')" name="phone" required>
        <UInput v-model="state.phone" type="tel" placeholder="+998 90 123 45 67" class="w-full" />
      </UFormField>
      <UAlert v-if="error" :title="error" color="error" variant="soft" icon="i-lucide-circle-alert" />
      <UButton type="submit" :label="t('track.submit')" :loading="loading" color="neutral" size="xl" block class="bg-ink text-gold-500 hover:bg-stone-800" />
    </UForm>
  </UContainer>
</template>
