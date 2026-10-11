<script setup lang="ts">
import type { ProductListItem } from '~/types/catalog'

const route = useRoute()
const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()

const q = computed(() => String(route.query.q ?? '').trim())
const { data: results, status } = await useAsyncData(
  'search',
  () => (q.value.length >= 2 ? api<ProductListItem[]>('/catalog/search', { query: { q: q.value, limit: 48 } }) : Promise.resolve([])),
  { watch: [q, locale], default: () => [] },
)

useSeoMeta({ title: () => t('search.resultsFor', { q: q.value }), robots: 'noindex' })
</script>

<template>
  <UContainer class="py-10">
    <header class="border-b border-default pb-6">
      <h1 class="font-serif text-4xl md:text-5xl">{{ t('search.resultsFor', { q }) }}</h1>
      <p class="mt-2 text-sm text-muted">{{ t('catalog.found', { n: results.length }) }}</p>
    </header>

    <div v-if="results.length" class="mt-8 grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 lg:grid-cols-4">
      <CatalogProductCard v-for="product in results" :key="product.slug" :product="product" />
    </div>
    <UEmpty
      v-else-if="status !== 'pending'"
      icon="i-lucide-search-x"
      :title="t('search.nothing')"
      :actions="[{ label: t('menu.all'), to: localePath('/watches'), color: 'neutral', variant: 'outline' }]"
      class="py-24"
    />
  </UContainer>
</template>
