<script setup lang="ts">
const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="mt-24 bg-ink text-white/60">
    <UContainer class="py-10 text-sm">
      <span class="font-serif tracking-[0.3em] text-gold-500">MAISON</span>
      <span class="ml-4">© {{ year }}. {{ t('footer.rights') }}</span>
    </UContainer>
  </footer>
</template>
