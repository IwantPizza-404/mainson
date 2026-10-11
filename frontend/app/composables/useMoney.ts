import { useCurrencyStore } from '~/stores/currency'

const LOCALE_FORMATS: Record<string, string> = { en: 'en-US', ru: 'ru-RU', uz: 'uz-Latn-UZ' }

/** Форматирует цену из USD (строка из API) в выбранную валюту и язык. */
export function useMoney() {
  const currency = useCurrencyStore()
  const { locale } = useI18n()

  function format(amountUsd: string | number | null | undefined): string {
    if (amountUsd === null || amountUsd === undefined) return ''
    const value = currency.convert(Number(amountUsd))
    const code = currency.current
    return new Intl.NumberFormat(LOCALE_FORMATS[locale.value] ?? 'en-US', {
      style: 'currency',
      currency: code,
      // Цены часов показываем без копеек; сумы дополнительно округляем до тысяч
      maximumFractionDigits: 0,
    }).format(code === 'UZS' ? Math.round(value / 1000) * 1000 : value)
  }

  return { format }
}
