<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()
</script>

<template>
  <header class="border-b border-line">
    <div class="mx-auto flex max-w-7xl items-center justify-between gap-6 px-4 py-4">
      <NuxtLink :to="localePath('/')" class="font-serif text-2xl tracking-[0.2em]">
        MAISON
      </NuxtLink>

      <nav class="hidden gap-6 text-sm uppercase tracking-wider md:flex">
        <span>{{ t('nav.watches') }}</span>
        <span>{{ t('nav.brands') }}</span>
        <span>{{ t('nav.preowned') }}</span>
        <span>{{ t('nav.offers') }}</span>
      </nav>

      <div class="flex items-center gap-4">
        <CurrencySwitcher />
        <LanguageSwitcher />
      </div>
    </div>
  </header>
</template>
