// Типы витрины — алиасы над сгенерированными из OpenAPI (make api-types).
import type { components } from './api'

type Schemas = components['schemas']

export type ProductListItem = Schemas['ProductListOut']
export type ProductDetail = Schemas['ProductDetailOut']
export type ProductPage = Schemas['PagedProductListOut']
export type CatalogFilters = Schemas['FiltersOut']
export type Choice = Schemas['ChoiceOut']
export type SpecOption = Schemas['SpecOptionOut']
export type ProductImage = Schemas['ImageOut']

export type Availability = 'in_stock' | 'on_order' | 'sold_out'
export type SortOption = 'newest' | 'price_asc' | 'price_desc'

// Корзина и заказы
export type CartQuote = Schemas['QuoteOut']
export type CartLine = Schemas['CartLineOut']
export type CheckoutOptions = Schemas['CheckoutOptionsOut']
export type DeliveryMethod = Schemas['DeliveryMethodOut']
export type OrderPayload = Schemas['OrderIn']
export type Order = Schemas['OrderOut']
