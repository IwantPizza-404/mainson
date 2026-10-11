<script setup lang="ts">
import type { HomeSection } from '~/types/catalog'

defineProps<{ section: HomeSection }>()
const link = useSiteLink()
</script>

<template>
  <section v-if="section.image" class="py-8">
    <UContainer>
      <component
        :is="section.link ? resolveComponent('NuxtLink') : 'div'"
        :to="link(section.link)"
        class="group relative flex min-h-[50vh] items-center overflow-hidden bg-ink text-white"
      >
        <ResponsivePicture :image="section.image" :mobile="section.image_mobile" :alt="section.title" class="absolute inset-0" />
        <div class="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent" />
        <div class="relative max-w-xl p-10 md:p-16">
          <h2 v-if="section.title" class="font-serif text-4xl md:text-5xl">{{ section.title }}</h2>
          <p v-if="section.subtitle" class="mt-4 text-white/80">{{ section.subtitle }}</p>
          <span v-if="section.button_label" class="mt-8 inline-block border-b border-gold-500 pb-1 text-xs uppercase tracking-[0.2em] text-gold-500">
            {{ section.button_label }}
          </span>
        </div>
      </component>
    </UContainer>
  </section>
</template>
