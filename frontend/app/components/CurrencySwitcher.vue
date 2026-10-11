<script setup lang="ts">
import { CURRENCIES, type Currency, useCurrencyStore } from '~/stores/currency'

const { t } = useI18n()
const currency = useCurrencyStore()
</script>

<template>
  <label class="flex items-center gap-1 text-sm">
    <span class="sr-only">{{ t('currency') }}</span>
    <select
      :value="currency.current"
      class="bg-transparent text-sm outline-none"
      @change="currency.set(($event.target as HTMLSelectElement).value as Currency)"
    >
      <option v-for="code in CURRENCIES" :key="code" :value="code">{{ code }}</option>
    </select>
  </label>
</template>
