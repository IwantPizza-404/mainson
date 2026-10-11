<script setup lang="ts">
import { useCartStore } from '~/stores/cart'

const { t } = useI18n()
const localePath = useLocalePath()
const cart = useCartStore()
const { format } = useMoney()

const { data: quote, status } = await useCartQuote()

useSeoMeta({ title: () => t('cart.title'), robots: 'noindex' })
</script>

<template>
  <UContainer class="py-10">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ t('cart.title') }}</h1>

    <UEmpty
      v-if="!cart.items.length"
      icon="i-lucide-shopping-bag"
      :title="t('cart.empty')"
      :actions="[{ label: t('home.cta'), to: localePath('/watches'), color: 'neutral' }]"
      class="py-24"
    />

    <div v-else class="mt-8 grid gap-10 lg:grid-cols-[1fr_360px]">
      <ul class="divide-y divide-default" :class="{ 'opacity-50': status === 'pending' }">
        <li v-for="line in quote?.lines ?? []" :key="line.slug" class="flex gap-4 py-6">
          <NuxtLink :to="localePath(`/watches/${line.slug}`)" class="aspect-square w-24 shrink-0 bg-elevated sm:w-32">
            <ProductPicture v-if="line.image" :image="line.image" :alt="line.name ?? ''" sizes="128px" class="h-full w-full object-cover" />
            <CatalogWatchPlaceholder v-else :brand="line.brand ?? ''" />
          </NuxtLink>

          <div class="flex flex-1 flex-col gap-1">
            <span class="text-xs uppercase tracking-[0.2em] text-muted">{{ line.brand }}</span>
            <NuxtLink :to="localePath(`/watches/${line.slug}`)" class="font-serif text-xl hover:underline">
              {{ line.name ?? line.slug }}
            </NuxtLink>
            <span v-if="line.availability === 'on_order'" class="text-xs text-muted">
              {{ t('cart.onOrder', { days: line.lead_time_days }) }}
            </span>

            <UAlert v-if="line.error" :title="line.error" color="error" variant="soft" icon="i-lucide-circle-alert" class="mt-2" />

            <div class="mt-auto flex flex-wrap items-center justify-between gap-3 pt-3">
              <UInputNumber
                v-if="line.max_quantity > 1"
                :model-value="line.quantity"
                :min="1"
                :max="line.max_quantity"
                size="sm"
                class="w-28"
                @update:model-value="(value) => value && cart.setQuantity(line.slug, value)"
              />
              <span v-else />
              <div class="flex items-center gap-3">
                <span class="font-medium">{{ format(line.line_total !== '0' ? line.line_total : line.price) }}</span>
                <UButton
                  icon="i-lucide-x"
                  :aria-label="t('cart.remove')"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  @click="cart.remove(line.slug)"
                />
              </div>
            </div>
          </div>
        </li>
      </ul>

      <aside class="h-fit space-y-4 bg-elevated p-6">
        <div class="flex justify-between text-lg">
          <span>{{ t('cart.subtotal') }}</span>
          <span class="font-medium">{{ format(quote?.subtotal) }}</span>
        </div>
        <p class="text-sm text-muted">{{ t('cart.deliveryNote') }}</p>
        <UButton
          :to="localePath('/checkout')"
          :label="t('cart.checkout')"
          :disabled="!quote?.is_valid"
          color="neutral"
          size="xl"
          block
          class="bg-ink text-gold-500 hover:bg-stone-800"
        />
        <p v-if="quote && !quote.is_valid" class="text-sm text-error">{{ t('cart.fixErrors') }}</p>
      </aside>
    </div>
  </UContainer>
</template>
