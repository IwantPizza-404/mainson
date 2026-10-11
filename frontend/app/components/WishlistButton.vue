<script setup lang="ts">
import { useWishlistStore } from '~/stores/wishlist'

const props = withDefaults(defineProps<{ slug: string; variant?: 'icon' | 'button' }>(), { variant: 'icon' })

const { t } = useI18n()
const wishlist = useWishlistStore()
const active = computed(() => wishlist.has(props.slug))

function toggle(event: Event) {
  // Кнопка лежит внутри ссылки-карточки — не переходим на страницу товара
  event.preventDefault()
  event.stopPropagation()
  wishlist.toggle(props.slug)
}
</script>

<template>
  <UButton
    v-if="variant === 'icon'"
    :aria-label="active ? t('wishlist.remove') : t('wishlist.add')"
    :aria-pressed="active"
    variant="ghost"
    color="neutral"
    :class="active ? 'text-gold-600' : 'text-ink/60 hover:text-ink'"
    class="rounded-full bg-white/80 backdrop-blur hover:bg-white"
    @click="toggle"
  >
    <template #leading>
      <UIcon name="i-lucide-heart" class="size-5" :class="{ 'fill-current': active }" />
    </template>
  </UButton>
  <UButton
    v-else
    :label="active ? t('wishlist.inList') : t('wishlist.add')"
    variant="outline"
    color="neutral"
    size="xl"
    block
    @click="toggle"
  >
    <template #leading>
      <UIcon name="i-lucide-heart" class="size-5" :class="{ 'fill-current text-gold-600': active }" />
    </template>
  </UButton>
</template>
