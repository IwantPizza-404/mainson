<script setup lang="ts">
const props = defineProps<{
  price: string
  compareAtPrice?: string | null
  size?: 'md' | 'lg'
}>()

const { format } = useMoney()
</script>

<template>
  <div class="flex items-baseline gap-2" :class="props.size === 'lg' ? 'text-2xl' : 'text-base'">
    <span class="font-medium" :class="{ 'text-gold-700': compareAtPrice }">{{ format(price) }}</span>
    <s v-if="compareAtPrice" class="text-sm text-muted">{{ format(compareAtPrice) }}</s>
  </div>
</template>
