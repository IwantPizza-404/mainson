// robots.txt: на продакшене — индексация каталога, на тестовом сервере — запрет всего
const PRIVATE = ['/cart', '/checkout', '/order/', '/track', '/search']

export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')

  if (!config.indexable) return 'User-agent: *\nDisallow: /\n'

  const disallow = ['', '/uz', '/ru'].flatMap((prefix) => PRIVATE.map((path) => `Disallow: ${prefix}${path}`))
  return ['User-agent: *', 'Allow: /', ...disallow, '', `Sitemap: ${config.public.siteUrl}/sitemap.xml`, ''].join('\n')
})
