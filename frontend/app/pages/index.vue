<script setup lang="ts">
import type { Component } from 'vue'
import type { HomeSection } from '~/types/catalog'

const { t, locale } = useI18n()
const api = useApi()

const { data: sections } = await useAsyncData('home', () => api<HomeSection[]>('/content/home'), {
  watch: [locale],
  default: () => [],
})

// Секции главной собираются в админке; порядок — как там
const components: Record<string, Component> = {
  hero: resolveComponent('HomeHero') as Component,
  trust: resolveComponent('HomeTrust') as Component,
  products: resolveComponent('HomeProducts') as Component,
  tiles: resolveComponent('HomeTiles') as Component,
  brands: resolveComponent('HomeBrands') as Component,
  banner: resolveComponent('HomeBanner') as Component,
}

useSeoMeta({
  title: () => t('home.title'),
  description: () => t('home.subtitle'),
})
</script>

<template>
  <div>
    <template v-for="section in sections" :key="section.id">
      <component :is="components[section.kind]" v-if="components[section.kind]" :section="section" />
    </template>
  </div>
</template>
