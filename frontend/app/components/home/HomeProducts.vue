<script setup lang="ts">
import type { HomeSection } from '~/types/catalog'

const props = defineProps<{ section: HomeSection }>()
const { t } = useI18n()
const localePath = useLocalePath()
const link = useSiteLink()

// «Смотреть все» ведёт в каталог с тем же отбором, если он выражается фильтром
const allLink = computed(() => link(props.section.link) ?? localePath('/watches'))
</script>

<template>
  <section class="py-16">
    <UContainer>
      <HomeSectionTitle :title="section.title" :subtitle="section.subtitle" :to="allLink" :link-label="t('home.viewAll')" />
      <CatalogProductCarousel :products="section.products" />
    </UContainer>
  </section>
</template>
