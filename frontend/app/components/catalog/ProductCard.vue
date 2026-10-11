<script setup lang="ts">
import type { ProductListItem } from '~/types/catalog'

const props = defineProps<{ product: ProductListItem }>()

const { t } = useI18n()
const localePath = useLocalePath()
const isSoldOut = computed(() => props.product.availability.value === 'sold_out')
</script>

<template>
  <NuxtLink
    :to="localePath(`/watches/${product.slug}`)"
    class="group flex flex-col"
    :class="{ 'opacity-60': isSoldOut }"
  >
    <div class="relative aspect-square overflow-hidden bg-neutral-100">
      <ProductPicture
        v-if="product.image"
        :image="product.image"
        :alt="product.name"
        sizes="(min-width: 1024px) 25vw, (min-width: 768px) 33vw, 50vw"
        class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
      />
      <CatalogWatchPlaceholder v-else :brand="product.brand.name" />

      <UBadge
        v-if="product.condition.value === 'pre_owned'"
        :label="product.condition.label"
        color="neutral"
        size="sm"
        class="absolute left-3 top-3 bg-ink text-gold-500"
      />
      <UBadge
        v-else-if="product.compare_at_price"
        :label="t('product.sale')"
        size="sm"
        class="absolute left-3 top-3"
      />
    </div>

    <div class="mt-4 flex flex-1 flex-col gap-1">
      <span class="text-xs uppercase tracking-[0.2em] text-muted">{{ product.brand.name }}</span>
      <h3 class="font-serif text-lg leading-snug group-hover:underline">{{ product.name }}</h3>
      <span v-if="product.reference" class="text-xs text-muted">{{ t('product.ref') }} {{ product.reference }}</span>
      <div class="mt-auto flex flex-wrap items-center justify-between gap-2 pt-3">
        <CatalogProductPrice :price="product.price" :compare-at-price="product.compare_at_price" />
        <CatalogAvailabilityBadge
          v-if="product.availability.value !== 'in_stock'"
          :availability="product.availability"
          :lead-time-days="product.lead_time_days"
        />
      </div>
    </div>
  </NuxtLink>
</template>
