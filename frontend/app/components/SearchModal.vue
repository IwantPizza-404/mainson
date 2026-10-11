<script setup lang="ts">
import type { ProductListItem } from '~/types/catalog'

const { t } = useI18n()
const api = useApi()
const localePath = useLocalePath()
const { format } = useMoney()

const open = ref(false)
const query = ref('')
const results = ref<ProductListItem[]>([])
const loading = ref(false)

// Подсказки с задержкой 250 мс — не дёргаем API на каждую букву
let timer: ReturnType<typeof setTimeout> | undefined
let requestId = 0
watch(query, (value) => {
  clearTimeout(timer)
  const q = value.trim()
  if (q.length < 2) {
    results.value = []
    return
  }
  timer = setTimeout(async () => {
    const id = ++requestId
    loading.value = true
    try {
      const data = await api<ProductListItem[]>('/catalog/search', { query: { q, limit: 6 } })
      if (id === requestId) results.value = data // игнорируем устаревшие ответы
    } finally {
      if (id === requestId) loading.value = false
    }
  }, 250)
})

async function showAll() {
  const q = query.value.trim()
  if (q.length < 2) return
  open.value = false
  await navigateTo(localePath({ path: '/search', query: { q } }))
}

const route = useRoute()
watch(() => route.fullPath, () => (open.value = false))
defineShortcuts({ meta_k: () => (open.value = true), '/': () => (open.value = true) })
</script>

<template>
  <UModal v-model:open="open" :title="t('search.title')" :ui="{ content: 'sm:max-w-2xl' }">
    <UButton icon="i-lucide-search" :aria-label="t('search.title')" variant="ghost" class="text-white hover:bg-white/10" />

    <template #content>
      <div class="p-4">
        <form @submit.prevent="showAll">
          <UInput
            v-model="query"
            :placeholder="t('search.placeholder')"
            icon="i-lucide-search"
            :loading="loading"
            size="xl"
            autofocus
            class="w-full"
          />
        </form>

        <ul v-if="results.length" class="mt-4 divide-y divide-default">
          <li v-for="product in results" :key="product.slug">
            <NuxtLink :to="localePath(`/watches/${product.slug}`)" class="flex items-center gap-4 py-3 hover:bg-elevated">
              <div class="size-14 shrink-0 bg-elevated">
                <ProductPicture v-if="product.image" :image="product.image" :alt="product.name" sizes="56px" class="h-full w-full object-cover" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs uppercase tracking-wider text-muted">{{ product.brand.name }}</p>
                <p class="truncate">{{ product.name }}</p>
              </div>
              <span class="shrink-0 text-sm">{{ format(product.price) }}</span>
            </NuxtLink>
          </li>
        </ul>
        <p v-else-if="query.trim().length >= 2 && !loading" class="mt-6 text-center text-sm text-muted">
          {{ t('search.nothing') }}
        </p>

        <UButton
          v-if="results.length"
          :label="t('search.showAll')"
          trailing-icon="i-lucide-arrow-right"
          variant="link"
          color="neutral"
          class="mt-2"
          @click="showAll"
        />
      </div>
    </template>
  </UModal>
</template>
