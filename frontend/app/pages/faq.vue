<script setup lang="ts">
import type { FaqItem } from '~/types/catalog'

const { t, locale } = useI18n()
const api = useApi()

const { data: faq } = await useAsyncData('faq', () => api<FaqItem[]>('/content/faq'), {
  watch: [locale],
  default: () => [],
})
const items = computed(() => faq.value.map((item, index) => ({ label: item.question, value: String(index), answer: item.answer })))

// Разметка FAQPage — Google может показать вопросы прямо в выдаче
useHead({
  script: computed(() => [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: faq.value.map((item) => ({
          '@type': 'Question',
          name: item.question,
          acceptedAnswer: { '@type': 'Answer', text: item.answer },
        })),
      }),
    },
  ]),
})
useSeoMeta({ title: () => t('faq.title') })
</script>

<template>
  <UContainer class="max-w-3xl py-12">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ t('faq.title') }}</h1>
    <UAccordion v-if="items.length" :items="items" class="mt-6" :ui="{ trigger: 'text-base font-medium py-5', label: 'text-left' }">
      <template #body="{ item }">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="prose prose-stone max-w-none pb-4" v-html="item.answer" />
      </template>
    </UAccordion>
    <p v-else class="mt-8 text-muted">{{ t('faq.empty') }}</p>
  </UContainer>
</template>
