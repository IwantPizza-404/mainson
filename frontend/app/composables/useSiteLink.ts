/** Ссылка из админки: путь на сайте (/watches?…) — с префиксом языка, внешний адрес — как есть. */
export function useSiteLink() {
  const localePath = useLocalePath()
  return (link: string | null | undefined) => {
    if (!link) return undefined
    return link.startsWith('/') ? localePath(link) : link
  }
}
