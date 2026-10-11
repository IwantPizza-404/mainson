<script setup lang="ts">
import type { HomeSection } from '~/types/catalog'

const props = defineProps<{ section: HomeSection }>()
const link = useSiteLink()
const slides = computed(() => props.section.items)
</script>

<template>
  <section class="relative bg-ink text-white">
    <UCarousel
      v-slot="{ item, index }"
      :items="slides"
      :dots="slides.length > 1"
      :autoplay="slides.length > 1 ? { delay: 6000 } : false"
      loop
      :ui="{ dots: 'absolute bottom-6 inset-x-0 justify-center', dot: 'bg-white/40 data-[state=active]:bg-gold-500' }"
    >
      <div class="relative flex min-h-[70vh] items-center md:min-h-[80vh]">
        <ResponsivePicture
          v-if="item.image"
          :image="item.image"
          :mobile="item.image_mobile"
          :alt="item.title"
          :loading="index === 0 ? 'eager' : 'lazy'"
          class="absolute inset-0"
        />
        <!-- Затемнение, чтобы текст читался на любом фото -->
        <div v-if="item.image" class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
        <UContainer class="relative py-24 text-center">
          <h1 v-if="item.title" class="font-serif text-5xl md:text-7xl">{{ item.title }}</h1>
          <p v-if="item.text" class="mx-auto mt-6 max-w-2xl text-lg text-white/80">{{ item.text }}</p>
          <UButton
            v-if="item.button_label && item.link"
            :to="link(item.link)"
            :label="item.button_label"
            variant="outline"
            size="xl"
            class="mt-10 px-10 text-gold-500 ring-gold-500 hover:bg-gold-500 hover:text-ink"
          />
        </UContainer>
      </div>
    </UCarousel>
  </section>
</template>
