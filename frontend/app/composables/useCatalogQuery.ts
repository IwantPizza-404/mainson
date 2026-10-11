import type { LocationQuery, LocationQueryValue } from 'vue-router'
import type { SortOption } from '~/types/catalog'

export const PAGE_SIZE = 24

const LIST_KEYS = [
  'brand',
  'condition',
  'availability',
  'gender',
  'movement',
  'case_material',
  'dial_color',
  'strap_material',
] as const

export type ListFilterKey = (typeof LIST_KEYS)[number]

const SORT_OPTIONS: SortOption[] = ['newest', 'price_asc', 'price_desc']

function asArray(value: LocationQueryValue | LocationQueryValue[] | undefined): string[] {
  if (value === undefined || value === null) return []
  return (Array.isArray(value) ? value : [value]).filter((v): v is string => !!v)
}

function asString(value: LocationQueryValue | LocationQueryValue[] | undefined): string | undefined {
  const [first] = asArray(value)
  return first || undefined
}

/**
 * Состояние каталога (фильтры, сортировка, страница) живёт в URL:
 * ссылкой на подборку можно поделиться, а поисковики видят отфильтрованные страницы.
 */
export function useCatalogQuery(fixed: { brand?: string } = {}) {
  const route = useRoute()
  const router = useRouter()

  const lists = computed(() =>
    Object.fromEntries(LIST_KEYS.map((key) => [key, asArray(route.query[key])])) as Record<
      ListFilterKey,
      string[]
    >,
  )

  const sort = computed<SortOption>(() => {
    const value = asString(route.query.sort) as SortOption | undefined
    return value && SORT_OPTIONS.includes(value) ? value : 'newest'
  })

  const page = computed(() => Math.max(1, Number(asString(route.query.page)) || 1))
  const priceMin = computed(() => asString(route.query.price_min))
  const priceMax = computed(() => asString(route.query.price_max))

  /** Параметры запроса к API каталога. */
  const apiQuery = computed(() => ({
    ...lists.value,
    ...(fixed.brand ? { brand: [fixed.brand] } : {}),
    price_min: priceMin.value,
    price_max: priceMax.value,
    sort: sort.value,
    page: page.value,
    page_size: PAGE_SIZE,
  }))

  const activeCount = computed(
    () =>
      Object.values(lists.value).reduce((sum, values) => sum + values.length, 0) +
      (priceMin.value ? 1 : 0) +
      (priceMax.value ? 1 : 0),
  )

  function navigate(patch: LocationQuery, { keepPage = false } = {}) {
    const merged: LocationQuery = { ...route.query, ...patch }
    if (!keepPage) merged.page = null
    // Пустые параметры убираем из URL
    const query = Object.fromEntries(
      Object.entries(merged).filter(
        ([, value]) => value !== undefined && value !== null && value !== '' && !(Array.isArray(value) && !value.length),
      ),
    )
    return router.push({ query })
  }

  function toggle(key: ListFilterKey, value: string) {
    const current = lists.value[key]
    const next = current.includes(value) ? current.filter((v) => v !== value) : [...current, value]
    return navigate({ [key]: next })
  }

  function setPrice(min?: string, max?: string) {
    return navigate({ price_min: min || null, price_max: max || null })
  }

  function setSort(value: SortOption) {
    return navigate({ sort: value === 'newest' ? null : value })
  }

  function setPage(value: number) {
    return navigate({ page: value > 1 ? String(value) : null }, { keepPage: true })
  }

  function reset() {
    return router.push({ query: route.query.sort ? { sort: route.query.sort } : {} })
  }

  return { lists, sort, page, priceMin, priceMax, apiQuery, activeCount, toggle, setPrice, setSort, setPage, reset }
}
