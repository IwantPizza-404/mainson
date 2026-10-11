<script setup lang="ts">
import type { HomeSection } from '~/types/catalog'

defineProps<{ section: HomeSection }>()
const link = useSiteLink()
</script>

<template>
  <section class="py-8">
    <UContainer>
      <HomeSectionTitle :title="section.title" :subtitle="section.subtitle" />
      <div class="grid gap-4" :class="section.items.length > 2 ? 'md:grid-cols-3' : 'md:grid-cols-2'">
        <NuxtLink
          v-for="item in section.items"
          :key="item.title"
          :to="link(item.link)"
          class="group relative flex aspect-[4/3] items-end overflow-hidden bg-ink text-white"
        >
          <ResponsivePicture
            v-if="item.image"
            :image="item.image"
            :mobile="item.image_mobile"
            :alt="item.title"
            sizes="(min-width: 768px) 50vw, 100vw"
            class="absolute inset-0 transition-transform duration-700 group-hover:scale-105"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div class="relative p-8">
            <p class="font-serif text-4xl">{{ item.title }}</p>
            <p v-if="item.text" class="mt-2 text-white/80">{{ item.text }}</p>
            <span v-if="item.button_label" class="mt-4 inline-block border-b border-gold-500 pb-1 text-xs uppercase tracking-[0.2em] text-gold-500">
              {{ item.button_label }}
            </span>
          </div>
        </NuxtLink>
      </div>
    </UContainer>
  </section>
</template>
