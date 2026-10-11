<script setup lang="ts">
import type { ProductDetail } from '~/types/catalog'

const route = useRoute()
const { t, locale } = useI18n()
const api = useApi()
const localePath = useLocalePath()
const config = useRuntimeConfig()

const slug = computed(() => String(route.params.slug))

const { data: product, error } = await useAsyncData(
  () => `product:${slug.value}`,
  () => api<ProductDetail>(`/catalog/products/${slug.value}`),
  { watch: [locale] },
)

if (error.value || !product.value) {
  throw createError({ statusCode: 404, statusMessage: 'Product not found', fatal: true })
}

const breadcrumbs = computed(() => [
  { label: t('nav.watches'), to: localePath('/watches') },
  { label: product.value?.brand.name, to: localePath({ path: '/watches', query: { brand: product.value?.brand.slug } }) },
  { label: product.value?.name },
])

const activeImage = ref(0)
const images = computed(() => product.value?.images ?? [])

/** Строки таблицы характеристик — только заполненные. */
const specs = computed(() => {
  const s = product.value?.watch_specs
  if (!s) return []
  const yesNo = (v: boolean) => (v ? t('common.yes') : t('common.no'))
  const rows: [string, string | number | null | undefined][] = [
    [t('specs.reference'), product.value?.reference],
    [t('specs.movement'), s.movement?.label],
    [t('specs.caliber'), s.caliber],
    [t('specs.powerReserve'), s.power_reserve_hours ? t('specs.hours', { n: s.power_reserve_hours }) : null],
    [t('specs.caseMaterial'), s.case_material?.name],
    [t('specs.diameter'), s.case_diameter_mm ? `${Number(s.case_diameter_mm)} mm` : null],
    [t('specs.thickness'), s.case_thickness_mm ? `${Number(s.case_thickness_mm)} mm` : null],
    [t('specs.glass'), s.glass?.name],
    [t('specs.waterResistance'), s.water_resistance_m ? `${s.water_resistance_m} m` : null],
    [t('specs.dialColor'), s.dial_color?.name],
    [t('specs.strap'), s.strap_material?.name],
    [t('specs.complications'), s.complications.map((c) => c.name).join(', ')],
    [t('specs.year'), s.year],
    [t('specs.box'), yesNo(s.has_box)],
    [t('specs.papers'), yesNo(s.has_papers)],
  ]
  return rows.filter(([, value]) => value !== null && value !== undefined && value !== '')
})

/** Заказ через мессенджер — пока нет корзины и онлайн-оплаты. */
const orderMessage = computed(() => {
  const p = product.value
  if (!p) return ''
  const url = `${config.public.siteUrl}${localePath(`/watches/${p.slug}`)}`
  return t('product.orderMessage', { name: `${p.brand.name} ${p.name}`, ref: p.reference, url })
})
const telegramLink = computed(() =>
  config.public.telegramUsername
    ? `https://t.me/${config.public.telegramUsername}?text=${encodeURIComponent(orderMessage.value)}`
    : null,
)
const whatsappLink = computed(() =>
  config.public.whatsappNumber
    ? `https://wa.me/${String(config.public.whatsappNumber)}?text=${encodeURIComponent(orderMessage.value)}`
    : null,
)

useSeoMeta({
  title: () => product.value?.seo_title || `${product.value?.brand.name} ${product.value?.name}`,
  description: () => product.value?.seo_description || product.value?.description.slice(0, 160),
  ogImage: () => images.value[0]?.url,
})
</script>

<template>
  <UContainer v-if="product" class="py-10">
    <UBreadcrumb :items="breadcrumbs" class="mb-8" :ui="{ link: 'text-xs uppercase tracking-wider' }" />

    <div class="grid gap-10 lg:grid-cols-2 lg:gap-16">
      <!-- Галерея -->
      <div>
        <div class="aspect-square overflow-hidden bg-neutral-100">
          <NuxtImg
            v-if="images.length"
            :src="images[activeImage]?.url"
            :alt="images[activeImage]?.alt || product.name"
            sizes="100vw lg:50vw"
            class="h-full w-full object-cover"
          />
          <CatalogWatchPlaceholder v-else :brand="product.brand.name" />
        </div>
        <div v-if="images.length > 1" class="mt-3 grid grid-cols-5 gap-2">
          <button
            v-for="(image, index) in images"
            :key="image.url"
            type="button"
            class="aspect-square overflow-hidden border"
            :class="index === activeImage ? 'border-inverted' : 'border-transparent'"
            @click="activeImage = index"
          >
            <NuxtImg :src="image.url" :alt="image.alt" sizes="100px" class="h-full w-full object-cover" />
          </button>
        </div>
      </div>

      <!-- Информация -->
      <div>
        <p class="text-sm uppercase tracking-[0.25em] text-muted">{{ product.brand.name }}</p>
        <h1 class="mt-2 font-serif text-4xl leading-tight md:text-5xl">{{ product.name }}</h1>
        <p v-if="product.reference" class="mt-2 text-sm text-muted">{{ t('product.ref') }} {{ product.reference }}</p>

        <div class="mt-6 flex flex-wrap items-center gap-3">
          <CatalogProductPrice :price="product.price" :compare-at-price="product.compare_at_price" size="lg" />
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <CatalogAvailabilityBadge :availability="product.availability" :lead-time-days="product.lead_time_days" />
          <UBadge :label="product.condition.label" color="neutral" variant="soft" size="sm" />
        </div>

        <div v-if="product.availability.value !== 'sold_out'" class="mt-8 flex flex-col gap-3 sm:flex-row">
          <UButton
            v-if="telegramLink"
            :to="telegramLink"
            target="_blank"
            :label="t('product.orderTelegram')"
            icon="i-lucide-send"
            color="neutral"
            size="xl"
            block
            class="flex-1 bg-ink text-gold-500 hover:bg-stone-800"
          />
          <UButton
            v-if="whatsappLink"
            :to="whatsappLink"
            target="_blank"
            :label="t('product.orderWhatsapp')"
            icon="i-lucide-message-circle"
            color="neutral"
            variant="outline"
            size="xl"
            block
            class="flex-1"
          />
        </div>
        <p v-else class="mt-8 text-sm text-muted">{{ t('product.soldOutHint') }}</p>

        <div v-if="product.description" class="mt-10 whitespace-pre-line leading-relaxed text-toned">
          {{ product.description }}
        </div>

        <section v-if="specs.length" class="mt-10">
          <h2 class="border-b border-default pb-3 text-sm font-medium uppercase tracking-wider">{{ t('specs.title') }}</h2>
          <dl class="divide-y divide-default">
            <div v-for="[label, value] in specs" :key="label" class="grid grid-cols-2 gap-4 py-3 text-sm">
              <dt class="text-muted">{{ label }}</dt>
              <dd>{{ value }}</dd>
            </div>
          </dl>
        </section>
      </div>
    </div>
  </UContainer>
</template>
