<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { z } from 'zod'
import type { WatchRequest } from '~/types/catalog'

const emit = defineEmits<{ created: [request: WatchRequest] }>()
const props = defineProps<{ initialBrand?: string; initialQuery?: string }>()

const { t } = useI18n()
const api = useApi()

const schema = computed(() =>
  z.object({
    brand: z.string().trim().min(2, t('checkout.errors.required')),
    model: z.string().max(150),
    reference: z.string().max(80),
    condition: z.enum(['any', 'new', 'pre_owned']),
    budget: z.number().positive().optional(),
    comment: z.string().max(2000),
  }),
)
type FormState = z.output<typeof schema.value>
const state = reactive<FormState>({
  brand: props.initialBrand ?? '',
  model: props.initialQuery ?? '',
  reference: '',
  condition: 'any',
  budget: undefined,
  comment: '',
})
const loading = ref(false)

const conditionItems = computed(() => [
  { value: 'any', label: t('requests.condition.any') },
  { value: 'new', label: t('menu.new') },
  { value: 'pre_owned', label: t('nav.preowned') },
])

async function onSubmit(event: FormSubmitEvent<FormState>) {
  loading.value = true
  try {
    const created = await api<WatchRequest>('/account/requests', { method: 'POST', body: event.data })
    emit('created', created)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UForm :schema="schema" :state="state" class="grid gap-4 sm:grid-cols-2" @submit="onSubmit">
    <UFormField :label="t('requests.brand')" name="brand" required>
      <UInput v-model="state.brand" placeholder="Patek Philippe" class="w-full" />
    </UFormField>
    <UFormField :label="t('requests.model')" name="model">
      <UInput v-model="state.model" placeholder="Nautilus" class="w-full" />
    </UFormField>
    <UFormField :label="t('specs.reference')" name="reference" :hint="t('checkout.optional')">
      <UInput v-model="state.reference" placeholder="5711/1A" class="w-full" />
    </UFormField>
    <UFormField :label="t('requests.budget')" name="budget" :hint="t('checkout.optional')">
      <UInputNumber v-model="state.budget" :min="0" :step="500" class="w-full" />
    </UFormField>
    <UFormField :label="t('filters.condition')" name="condition" class="sm:col-span-2">
      <URadioGroup v-model="state.condition" :items="conditionItems" orientation="horizontal" color="neutral" />
    </UFormField>
    <UFormField :label="t('checkout.comment')" name="comment" class="sm:col-span-2">
      <UTextarea v-model="state.comment" :rows="3" :placeholder="t('requests.commentHint')" class="w-full" />
    </UFormField>
    <div class="sm:col-span-2">
      <UButton type="submit" :label="t('requests.submit')" :loading="loading" color="neutral" class="bg-ink text-gold-500 hover:bg-stone-800" />
    </div>
  </UForm>
</template>
