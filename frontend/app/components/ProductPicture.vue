<script setup lang="ts">
import type { ProductImage } from '~/types/catalog'

/**
 * Фото товара с адаптивными WebP-вариантами от бэкенда (400/800/1600 px):
 * браузер сам выбирает размер под экран, телефон не качает оригинал.
 */
const props = withDefaults(
  defineProps<{
    image: ProductImage
    alt: string
    sizes?: string
    loading?: 'lazy' | 'eager'
  }>(),
  { sizes: '100vw', loading: 'lazy' },
)

const srcset = computed(() => {
  const { thumb, medium, large } = props.image
  // Пока варианты не построены, бэкенд отдаёт оригинал во всех полях
  if (thumb === large) return undefined
  return `${thumb} 400w, ${medium} 800w, ${large} 1600w`
})
</script>

<template>
  <img
    :src="image.medium"
    :srcset="srcset"
    :sizes="sizes"
    :alt="image.alt || alt"
    :width="image.width ?? undefined"
    :height="image.height ?? undefined"
    :loading="loading"
    decoding="async"
  >
</template>
