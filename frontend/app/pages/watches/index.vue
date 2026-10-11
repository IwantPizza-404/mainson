<script setup lang="ts">
const { t } = useI18n()

useSeoMeta({
  title: () => t('catalog.title'),
  description: () => t('catalog.description'),
})
</script>

<template>
  <CatalogView :title="t('catalog.title')" />
</template>
