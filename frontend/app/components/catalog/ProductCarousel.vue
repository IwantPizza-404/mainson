<script setup lang="ts">
import type { ProductListItem } from '~/types/catalog'

defineProps<{ products: ProductListItem[] }>()
</script>

<template>
  <UCarousel
    v-slot="{ item }"
    :items="products"
    arrows
    align="start"
    :prev="{ color: 'neutral', variant: 'outline' }"
    :next="{ color: 'neutral', variant: 'outline' }"
    :ui="{ item: 'basis-1/2 md:basis-1/3 lg:basis-1/4', container: '-ms-4', controls: 'hidden lg:block' }"
  >
    <div class="ps-4">
      <CatalogProductCard :product="item" />
    </div>
  </UCarousel>
</template>
