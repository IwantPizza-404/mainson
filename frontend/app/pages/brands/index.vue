<script setup lang="ts">
import { useSiteStore } from '~/stores/site'

const { t } = useI18n()
const localePath = useLocalePath()
const site = useSiteStore()

// Алфавитный указатель
const groups = computed(() => {
  const result: Record<string, typeof site.brands> = {}
  for (const brand of [...site.brands].sort((a, b) => a.name.localeCompare(b.name))) {
    const letter = brand.name[0]?.toUpperCase() ?? '#'
    ;(result[letter] ??= []).push(brand)
  }
  return result
})

useSeoMeta({ title: () => t('brands.title'), description: () => t('brands.description') })
</script>

<template>
  <UContainer class="py-10">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ t('brands.title') }}</h1>

    <div class="mt-10 grid grid-cols-2 gap-px bg-[var(--ui-border)] sm:grid-cols-3 lg:grid-cols-4">
      <NuxtLink
        v-for="brand in site.brands"
        :key="brand.slug"
        :to="localePath(`/brands/${brand.slug}`)"
        class="flex h-40 flex-col items-center justify-center gap-3 bg-default p-6 transition-colors hover:bg-elevated"
      >
        <img v-if="brand.logo" :src="brand.logo" :alt="brand.name" loading="lazy" class="max-h-14 max-w-full object-contain">
        <span v-else class="font-serif text-2xl tracking-[0.15em] uppercase">{{ brand.name }}</span>
        <span class="text-xs text-muted">{{ t('brands.count', { n: brand.product_count }) }}</span>
      </NuxtLink>
    </div>

    <section class="mt-16 columns-2 gap-10 sm:columns-3 lg:columns-4">
      <div v-for="(brands, letter) in groups" :key="letter" class="mb-6 break-inside-avoid">
        <p class="font-serif text-2xl text-gold-700">{{ letter }}</p>
        <ul class="mt-2 space-y-1 text-sm">
          <li v-for="brand in brands" :key="brand.slug">
            <NuxtLink :to="localePath(`/brands/${brand.slug}`)" class="hover:underline">{{ brand.name }}</NuxtLink>
          </li>
        </ul>
      </div>
    </section>
  </UContainer>
</template>
