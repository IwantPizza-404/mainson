// sitemap.xml: все языковые версии страниц с перекрёстными hreflang-ссылками
interface Entry {
  slug: string
  updated_at?: string | null
}
interface SitemapData {
  products: Entry[]
  brands: Entry[]
  pages: Entry[]
}

// Совпадает с i18n: английский без префикса
const LOCALES = [
  { code: 'en', prefix: '', hreflang: 'en' },
  { code: 'uz', prefix: '/uz', hreflang: 'uz' },
  { code: 'ru', prefix: '/ru', hreflang: 'ru' },
]

const escape = (value: string) => value.replace(/&/g, '&amp;').replace(/</g, '&lt;')

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const site = config.public.siteUrl
  const data = await $fetch<SitemapData>(`${config.apiBase}/content/sitemap`)

  const paths: Entry[] = [
    { slug: '' },
    { slug: '/watches' },
    { slug: '/brands' },
    { slug: '/faq' },
    { slug: '/contacts' },
    ...data.products.map((p) => ({ slug: `/watches/${p.slug}`, updated_at: p.updated_at })),
    ...data.brands.map((b) => ({ slug: `/brands/${b.slug}` })),
    ...data.pages.map((p) => ({ slug: `/${p.slug}`, updated_at: p.updated_at })),
  ]

  const urls = paths.flatMap(({ slug, updated_at }) => {
    const alternates = LOCALES.map(
      (l) => `<xhtml:link rel="alternate" hreflang="${l.hreflang}" href="${escape(site + l.prefix + slug)}"/>`,
    ).join('')
    const xDefault = `<xhtml:link rel="alternate" hreflang="x-default" href="${escape(site + slug)}"/>`
    const lastmod = updated_at ? `<lastmod>${updated_at.slice(0, 10)}</lastmod>` : ''
    return LOCALES.map(
      (l) => `<url><loc>${escape(site + l.prefix + slug || site + '/')}</loc>${lastmod}${alternates}${xDefault}</url>`,
    )
  })

  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  setHeader(event, 'cache-control', 'public, max-age=3600')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls.join('\n')}
</urlset>`
})
