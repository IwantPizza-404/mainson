<script setup lang="ts">
defineProps<{ title?: string; subtitle?: string; to?: string; linkLabel?: string }>()
</script>

<template>
  <div v-if="title" class="mb-8 flex flex-wrap items-end justify-between gap-4">
    <div>
      <h2 class="font-serif text-3xl md:text-4xl">{{ title }}</h2>
      <p v-if="subtitle" class="mt-2 text-muted">{{ subtitle }}</p>
    </div>
    <UButton v-if="to && linkLabel" :to="to" :label="linkLabel" trailing-icon="i-lucide-arrow-right" variant="link" color="neutral" />
  </div>
</template>
