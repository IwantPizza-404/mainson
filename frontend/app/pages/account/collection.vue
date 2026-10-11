<script setup lang="ts">
import type { CollectionItem } from '~/types/catalog'

const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()

const { data: items } = await useAsyncData('account-collection', () => api<CollectionItem[]>('/account/collection'), {
  default: () => [],
})

const date = (value: string) => new Date(value).toLocaleDateString(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })
const warrantyActive = (value: string | null) => !!value && new Date(value) >= new Date()
useSeoMeta({ title: () => t('account.nav.collection') })
</script>

<template>
  <div>
    <h2 class="font-serif text-2xl">{{ t('account.nav.collection') }}</h2>
    <p class="mt-2 text-sm text-muted">{{ t('account.collection.hint') }}</p>

    <div v-if="items.length" class="mt-6 grid gap-6 sm:grid-cols-2">
      <article v-for="item in items" :key="`${item.order_number}-${item.reference}-${item.serial_number}`" class="flex gap-4 border border-default p-4">
        <NuxtLink :to="item.product_slug ? localePath(`/watches/${item.product_slug}`) : undefined" class="aspect-square w-28 shrink-0 bg-elevated">
          <ProductPicture v-if="item.image" :image="item.image" :alt="item.name" sizes="112px" class="h-full w-full object-cover" />
          <CatalogWatchPlaceholder v-else :brand="item.brand" />
        </NuxtLink>
        <dl class="min-w-0 flex-1 space-y-1 text-sm">
          <p class="text-xs uppercase tracking-wider text-muted">{{ item.brand }}</p>
          <p class="font-serif text-lg leading-snug">{{ item.name }}</p>
          <p v-if="item.reference" class="text-muted">{{ t('product.ref') }} {{ item.reference }}</p>
          <p v-if="item.serial_number" class="text-muted">{{ t('account.collection.serial') }}: {{ item.serial_number }}</p>
          <p class="text-muted">{{ t('account.collection.purchased') }}: {{ date(item.purchased_at) }}</p>
          <UBadge
            v-if="item.warranty_until"
            :label="t(warrantyActive(item.warranty_until) ? 'account.collection.warranty' : 'account.collection.warrantyExpired', { date: date(item.warranty_until) })"
            :color="warrantyActive(item.warranty_until) ? 'success' : 'neutral'"
            variant="soft"
            size="sm"
          />
        </dl>
      </article>
    </div>
    <UEmpty v-else icon="i-lucide-watch" :title="t('account.collection.empty')" class="py-16" />
  </div>
</template>
