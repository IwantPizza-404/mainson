<script setup lang="ts">
import { CURRENCIES, type Currency, useCurrencyStore } from '~/stores/currency'

const { t } = useI18n()
const currency = useCurrencyStore()

const model = computed({
  get: () => currency.current,
  set: (value: Currency) => currency.set(value),
})
</script>

<template>
  <USelect
    v-model="model"
    :items="[...CURRENCIES]"
    :aria-label="t('currency')"
    variant="none"
    size="sm"
    class="w-20 text-white/80"
  />
</template>
