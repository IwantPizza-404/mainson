<script setup lang="ts">
import type { ResponsiveImage } from '~/types/catalog'

/** Баннер с WebP-вариантами; на телефонах — отдельное изображение, если оно загружено. */
withDefaults(
  defineProps<{
    image: ResponsiveImage
    mobile?: ResponsiveImage | null
    alt?: string
    sizes?: string
    loading?: 'lazy' | 'eager'
  }>(),
  { mobile: null, alt: '', sizes: '100vw', loading: 'lazy' },
)
</script>

<template>
  <picture>
    <source
      v-if="mobile"
      media="(max-width: 767px)"
      :srcset="mobile.srcset ?? mobile.url"
      :sizes="sizes"
    >
    <img
      :src="image.url"
      :srcset="image.srcset ?? undefined"
      :sizes="sizes"
      :width="image.width ?? undefined"
      :height="image.height ?? undefined"
      :alt="alt"
      :loading="loading"
      decoding="async"
      class="h-full w-full object-cover"
    >
  </picture>
</template>
