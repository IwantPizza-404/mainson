<script setup lang="ts">
const { locale, locales, t } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>

<template>
  <nav :aria-label="t('language')" class="flex gap-2 text-sm">
    <NuxtLink
      v-for="item in locales"
      :key="item.code"
      :to="switchLocalePath(item.code)"
      :class="item.code === locale ? 'text-ink' : 'text-muted hover:text-ink'"
    >
      {{ item.code.toUpperCase() }}
    </NuxtLink>
  </nav>
</template>
