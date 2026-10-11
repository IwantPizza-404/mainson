<script setup lang="ts">
const { t } = useI18n()

useSeoMeta({
  title: () => t('home.title'),
  description: () => t('home.subtitle'),
})
</script>

<template>
  <section class="mx-auto max-w-7xl px-4 py-32 text-center">
    <h1 class="font-serif text-5xl md:text-7xl">{{ t('home.title') }}</h1>
    <p class="mt-6 text-lg text-muted">{{ t('home.subtitle') }}</p>
  </section>
</template>
