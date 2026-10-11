<script setup lang="ts">
defineProps<{ brand?: string }>()
</script>

<!-- Заглушка для товара без фото -->
<template>
  <div class="flex h-full w-full flex-col items-center justify-center gap-3 bg-neutral-100 text-neutral-400">
    <svg viewBox="0 0 48 48" class="h-12 w-12" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">
      <rect x="17" y="3" width="14" height="8" rx="1.5" />
      <rect x="17" y="37" width="14" height="8" rx="1.5" />
      <circle cx="24" cy="24" r="13" />
      <path d="M24 16v8l5 3" stroke-linecap="round" />
    </svg>
    <span v-if="brand" class="font-serif text-sm tracking-[0.2em] uppercase">{{ brand }}</span>
  </div>
</template>
