<script setup lang="ts">
import type { BadgeProps } from '@nuxt/ui'
import type { Availability, Choice } from '~/types/catalog'

const props = defineProps<{
  availability: Choice
  leadTimeDays?: number | null
}>()

const { t } = useI18n()

const color: Record<Availability, BadgeProps['color']> = {
  in_stock: 'success',
  on_order: 'warning',
  sold_out: 'neutral',
}

const label = computed(() =>
  props.availability.value === 'on_order' && props.leadTimeDays
    ? `${props.availability.label} · ${t('product.leadTime', { days: props.leadTimeDays })}`
    : props.availability.label,
)
</script>

<template>
  <UBadge :label="label" :color="color[availability.value as Availability]" variant="soft" size="sm" />
</template>
