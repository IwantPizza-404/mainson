<script setup lang="ts">
import type { HomeSection } from '~/types/catalog'

defineProps<{ section: HomeSection }>()
</script>

<template>
  <section class="border-b border-default">
    <UContainer class="grid grid-cols-2 gap-8 py-10 lg:grid-cols-4">
      <div v-for="item in section.items" :key="item.title" class="flex items-start gap-3">
        <UIcon v-if="item.icon" :name="`i-lucide-${item.icon}`" class="mt-0.5 size-6 shrink-0 text-gold-600" />
        <div>
          <p class="text-sm font-medium uppercase tracking-wider">{{ item.title }}</p>
          <p v-if="item.text" class="mt-1 text-sm text-muted">{{ item.text }}</p>
        </div>
      </div>
    </UContainer>
  </section>
</template>
