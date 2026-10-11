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
      <UCarousel
        v-slot="{ item }"
        :items="section.products"
        arrows
        align="start"
        :prev="{ color: 'neutral', variant: 'outline' }"
        :next="{ color: 'neutral', variant: 'outline' }"
        :ui="{ item: 'basis-1/2 md:basis-1/3 lg:basis-1/4', container: '-ms-4', controls: 'hidden lg:block' }"
      >
        <div class="ps-4">
          <CatalogProductCard :product="item" />
        </div>
      </UCarousel>
    </UContainer>
  </section>
</template>
