<script setup lang="ts">
import type { Brand } from '~/types/catalog'

const route = useRoute()
const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()

const slug = String(route.params.slug)
const { data: brand, error } = await useAsyncData(`brand:${slug}`, () => api<Brand>(`/catalog/brands/${slug}`), {
  watch: [locale],
})

if (error.value || !brand.value) {
  throw createError({ statusCode: 404, statusMessage: 'Brand not found', fatal: true })
}

useSeoMeta({
  title: () => t('brands.pageTitle', { name: brand.value?.name }),
  description: () => brand.value?.description.slice(0, 160) || t('brands.pageDescription', { name: brand.value?.name }),
})
</script>

<template>
  <div v-if="brand">
    <UContainer class="pt-10">
      <UBreadcrumb
        :items="[{ label: t('nav.brands'), to: localePath('/brands') }, { label: brand.name }]"
        :ui="{ link: 'text-xs uppercase tracking-wider' }"
      />
    </UContainer>
    <CatalogView :title="brand.name" :brand="brand.slug">
      <template #heading>
        <div class="flex items-center gap-6">
          <img v-if="brand.logo" :src="brand.logo" :alt="brand.name" class="max-h-16 max-w-40 object-contain">
          <div>
            <h1 class="font-serif text-4xl md:text-5xl">{{ brand.name }}</h1>
            <p v-if="brand.country" class="mt-1 text-sm uppercase tracking-wider text-muted">{{ brand.country }}</p>
          </div>
        </div>
        <p v-if="brand.description" class="mt-6 max-w-3xl whitespace-pre-line leading-relaxed text-toned">{{ brand.description }}</p>
      </template>
    </CatalogView>
  </div>
</template>
