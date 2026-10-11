<script setup lang="ts">
const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="mt-24 border-t border-line">
    <div class="mx-auto max-w-7xl px-4 py-8 text-sm text-muted">
      © {{ year }} Maison. {{ t('footer.rights') }}
    </div>
  </footer>
</template>
