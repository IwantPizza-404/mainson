<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useWishlistStore } from '~/stores/wishlist'
import type { ProductListItem, ProductPage } from '~/types/catalog'

const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()
const auth = useAuthStore()
const wishlist = useWishlistStore()

// Вошедшему — из аккаунта; гостю — товары по сохранённым в браузере slug
const { data: products } = await useAsyncData(
  'wishlist',
  async () => {
    if (auth.isLoggedIn) return wishlist.applyServer(await api<ProductListItem[]>('/account/wishlist'))
    if (!wishlist.slugs.length) return []
    const page = await api<ProductPage>('/catalog/products', { query: { slug: wishlist.slugs, page_size: 96 } })
    return page.items
  },
  { watch: [locale], default: () => [] },
)
// Убранные с этой страницы товары исчезают сразу
const visible = computed(() => products.value.filter((p) => wishlist.has(p.slug)))

useSeoMeta({ title: () => t('wishlist.title'), robots: 'noindex' })
</script>

<template>
  <UContainer class="py-10">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ t('wishlist.title') }}</h1>

    <UAlert
      v-if="!auth.isLoggedIn && visible.length"
      :title="t('wishlist.guestHint')"
      :actions="[{ label: t('login.title'), to: localePath({ path: '/login', query: { redirect: '/wishlist' } }), color: 'neutral', variant: 'outline' }]"
      icon="i-lucide-info"
      color="neutral"
      variant="soft"
      class="mt-6"
    />

    <div v-if="visible.length" class="mt-8 grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 lg:grid-cols-4">
      <CatalogProductCard v-for="product in visible" :key="product.slug" :product="product" />
    </div>
    <UEmpty
      v-else
      icon="i-lucide-heart"
      :title="t('wishlist.empty')"
      :description="t('wishlist.emptyHint')"
      :actions="[{ label: t('menu.all'), to: localePath('/watches'), color: 'neutral', variant: 'outline' }]"
      class="py-24"
    />
  </UContainer>
</template>
