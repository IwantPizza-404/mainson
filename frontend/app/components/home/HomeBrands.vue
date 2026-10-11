<script setup lang="ts">
import type { HomeSection } from '~/types/catalog'

defineProps<{ section: HomeSection }>()
const { t } = useI18n()
const localePath = useLocalePath()
</script>

<template>
  <section class="border-y border-default py-16">
    <UContainer>
      <HomeSectionTitle :title="section.title" :subtitle="section.subtitle" :to="localePath('/brands')" :link-label="t('brands.all')" />
      <div class="grid grid-cols-2 gap-px bg-[var(--ui-border)] sm:grid-cols-3 lg:grid-cols-6">
        <NuxtLink
          v-for="brand in section.brands"
          :key="brand.slug"
          :to="localePath(`/brands/${brand.slug}`)"
          class="flex h-28 items-center justify-center bg-default p-6 transition-colors hover:bg-elevated"
        >
          <img v-if="brand.logo" :src="brand.logo" :alt="brand.name" loading="lazy" class="max-h-12 max-w-full object-contain grayscale transition hover:grayscale-0">
          <span v-else class="font-serif text-xl tracking-[0.15em] uppercase">{{ brand.name }}</span>
        </NuxtLink>
      </div>
    </UContainer>
  </section>
</template>
