<script setup lang="ts">
import type { Page } from '~/types/catalog'

const route = useRoute()
const { locale } = useI18n()
const api = useApi()

const slug = String(route.params.slug)
const { data: page, error } = await useAsyncData(`page:${slug}`, () => api<Page>(`/content/pages/${slug}`), {
  watch: [locale],
})

if (error.value || !page.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}

useSeoMeta({
  title: () => page.value?.title,
  description: () => page.value?.seo_description || undefined,
})
</script>

<template>
  <UContainer v-if="page" class="max-w-3xl py-12">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ page.title }}</h1>
    <!-- HTML очищен на бэкенде (nh3): только безопасная разметка -->
    <!-- eslint-disable-next-line vue/no-v-html -->
    <article class="prose prose-stone mt-8 max-w-none prose-headings:font-serif prose-a:text-gold-700" v-html="page.content" />
  </UContainer>
</template>
