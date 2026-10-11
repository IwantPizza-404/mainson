<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

useSeoMeta({
  title: () => t('home.title'),
  description: () => t('home.subtitle'),
})
</script>

<template>
  <section class="bg-ink text-white">
    <UContainer class="py-32 text-center md:py-44">
      <h1 class="font-serif text-5xl md:text-7xl">{{ t('home.title') }}</h1>
      <p class="mt-6 text-lg text-white/70">{{ t('home.subtitle') }}</p>
      <UButton
        :to="localePath('/watches')"
        :label="t('home.cta')"
        variant="outline"
        size="xl"
        class="mt-10 px-10 ring-gold-500 text-gold-500 hover:bg-gold-500 hover:text-ink"
      />
    </UContainer>
  </section>
</template>
