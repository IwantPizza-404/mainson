<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { z } from 'zod'
import { useCartStore } from '~/stores/cart'
import { useCurrencyStore } from '~/stores/currency'
import type { CheckoutOptions, Order, OrderPayload } from '~/types/catalog'

const { t, locale } = useI18n()
const localePath = useLocalePath()
const api = useApi()
const cart = useCartStore()
const currency = useCurrencyStore()
const { format } = useMoney()

if (!cart.items.length) await navigateTo(localePath('/cart'))

const [{ data: options }, { data: quote }] = await Promise.all([
  useAsyncData('checkout-options', () => api<CheckoutOptions>('/checkout/options'), { watch: [locale] }),
  useCartQuote(),
])

const schema = computed(() =>
  z.object({
    customer_name: z.string().trim().min(2, t('checkout.errors.name')),
    phone: z.string().trim().regex(/^\+?[0-9 ()-]{7,20}$/, t('checkout.errors.phone')),
    email: z.union([z.literal(''), z.email(t('checkout.errors.email'))]),
    contact_method: z.enum(['telegram', 'whatsapp', 'phone']),
    country: z.string().length(2, t('checkout.errors.required')),
    city: z.string().trim().min(2, t('checkout.errors.required')),
    address: z.string().max(255),
    delivery_method: z.string().min(1, t('checkout.errors.delivery')),
    comment: z.string().max(2000),
  }),
)
type FormState = z.output<typeof schema.value>

const state = reactive<FormState>({
  customer_name: '',
  phone: '',
  email: '',
  contact_method: 'telegram',
  country: options.value?.home_country ?? 'UZ',
  city: '',
  address: '',
  delivery_method: '',
  comment: '',
})
// Ловушка для ботов: поле скрыто, человек его не заполнит
const website = ref('')

const isHome = computed(() => state.country === options.value?.home_country)
const deliveryMethods = computed(() =>
  (options.value?.delivery_methods ?? []).filter((m) => (m.scope === 'international') !== isHome.value),
)
// Смена страны может сделать выбранный способ недоступным
watch(deliveryMethods, (methods) => {
  if (!methods.some((m) => m.code === state.delivery_method)) state.delivery_method = methods[0]?.code ?? ''
}, { immediate: true })

const selectedDelivery = computed(() => deliveryMethods.value.find((m) => m.code === state.delivery_method))
const deliveryItems = computed(() =>
  deliveryMethods.value.map((m) => ({
    value: m.code,
    label: m.name,
    description: m.price !== null && Number(m.price) > 0 ? `${m.description} · ${format(m.price)}` : m.description,
  })),
)
const contactItems = computed(() => [
  { value: 'telegram', label: 'Telegram' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'phone', label: t('checkout.call') },
])
const countryItems = computed(() => (options.value?.countries ?? []).map((c) => ({ value: c.code, label: c.name })))

const total = computed(() => Number(quote.value?.subtotal ?? 0) + Number(selectedDelivery.value?.price ?? 0))

const submitting = ref(false)
const error = ref<string | null>(null)

async function onSubmit(event: FormSubmitEvent<FormState>) {
  submitting.value = true
  error.value = null
  const payload: OrderPayload = {
    ...event.data,
    email: event.data.email || null,
    items: cart.items,
    currency: currency.current,
    website: website.value,
  }
  try {
    const order = await api<Order>('/orders', { method: 'POST', body: payload })
    cart.clear()
    await navigateTo(localePath(`/order/${order.token}`))
  } catch (e: unknown) {
    const response = (e as { response?: { status?: number; _data?: { detail?: unknown } } }).response
    const detail = response?._data?.detail
    error.value =
      response?.status === 429
        ? t('checkout.errors.tooMany')
        : typeof detail === 'string'
          ? detail
          : t('checkout.errors.generic')
  } finally {
    submitting.value = false
  }
}

useSeoMeta({ title: () => t('checkout.title'), robots: 'noindex' })
</script>

<template>
  <UContainer class="py-10">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ t('checkout.title') }}</h1>

    <UForm :schema="schema" :state="state" class="mt-8 grid gap-10 lg:grid-cols-[1fr_380px]" @submit="onSubmit">
      <div class="space-y-10">
        <fieldset class="space-y-4">
          <legend class="mb-4 text-sm font-medium uppercase tracking-wider">{{ t('checkout.contacts') }}</legend>
          <div class="grid gap-4 sm:grid-cols-2">
            <UFormField :label="t('checkout.name')" name="customer_name" required>
              <UInput v-model="state.customer_name" autocomplete="name" class="w-full" />
            </UFormField>
            <UFormField :label="t('checkout.phone')" name="phone" required>
              <UInput v-model="state.phone" type="tel" autocomplete="tel" placeholder="+998 90 123 45 67" class="w-full" />
            </UFormField>
            <UFormField :label="t('checkout.email')" name="email" :hint="t('checkout.optional')">
              <UInput v-model="state.email" type="email" autocomplete="email" class="w-full" />
            </UFormField>
          </div>
          <UFormField :label="t('checkout.contactMethod')" name="contact_method">
            <URadioGroup v-model="state.contact_method" :items="contactItems" orientation="horizontal" color="neutral" />
          </UFormField>
        </fieldset>

        <fieldset class="space-y-4">
          <legend class="mb-4 text-sm font-medium uppercase tracking-wider">{{ t('checkout.delivery') }}</legend>
          <div class="grid gap-4 sm:grid-cols-2">
            <UFormField :label="t('checkout.country')" name="country" required>
              <USelectMenu v-model="state.country" :items="countryItems" value-key="value" class="w-full" />
            </UFormField>
            <UFormField :label="t('checkout.city')" name="city" required>
              <UInput v-model="state.city" autocomplete="address-level2" class="w-full" />
            </UFormField>
          </div>
          <UFormField :label="t('checkout.address')" name="address" :hint="t('checkout.optional')">
            <UInput v-model="state.address" autocomplete="street-address" class="w-full" />
          </UFormField>
          <UFormField :label="t('checkout.deliveryMethod')" name="delivery_method" required>
            <URadioGroup v-model="state.delivery_method" :items="deliveryItems" variant="card" color="neutral" />
          </UFormField>
          <UFormField :label="t('checkout.comment')" name="comment" :hint="t('checkout.optional')">
            <UTextarea v-model="state.comment" :rows="3" class="w-full" />
          </UFormField>
        </fieldset>

        <input v-model="website" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="hidden">
      </div>

      <aside class="h-fit space-y-4 bg-elevated p-6">
        <h2 class="text-sm font-medium uppercase tracking-wider">{{ t('checkout.summary') }}</h2>
        <ul class="space-y-2 text-sm">
          <li v-for="line in quote?.lines ?? []" :key="line.slug" class="flex justify-between gap-4">
            <span>{{ line.brand }} {{ line.name }}<template v-if="line.quantity > 1"> × {{ line.quantity }}</template></span>
            <span class="shrink-0">{{ format(line.line_total) }}</span>
          </li>
        </ul>
        <USeparator />
        <div class="flex justify-between text-sm">
          <span>{{ t('checkout.delivery') }}</span>
          <span>{{ selectedDelivery?.price !== null && selectedDelivery?.price !== undefined ? format(selectedDelivery.price) : t('checkout.byManager') }}</span>
        </div>
        <div class="flex justify-between text-lg">
          <span>{{ t('checkout.total') }}</span>
          <span class="font-medium">{{ format(total) }}</span>
        </div>
        <p class="text-sm text-muted">{{ t('checkout.paymentNote') }}</p>
        <UAlert v-if="error" :title="error" color="error" variant="soft" icon="i-lucide-circle-alert" />
        <UButton
          type="submit"
          :label="t('checkout.submit')"
          :loading="submitting"
          :disabled="!quote?.is_valid"
          color="neutral"
          size="xl"
          block
          class="bg-ink text-gold-500 hover:bg-stone-800"
        />
        <UButton :to="localePath('/cart')" :label="t('checkout.backToCart')" variant="link" color="neutral" block />
      </aside>
    </UForm>
  </UContainer>
</template>
