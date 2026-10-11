<script setup lang="ts">
import { useSiteStore } from '~/stores/site'

const { t } = useI18n()
const site = useSiteStore()
const s = computed(() => site.settings)
const telegram = computed(() => site.telegramLink())
const whatsapp = computed(() => site.whatsappLink())

useSeoMeta({ title: () => t('contacts.title') })
</script>

<template>
  <UContainer class="max-w-3xl py-12">
    <h1 class="border-b border-default pb-6 font-serif text-4xl md:text-5xl">{{ t('contacts.title') }}</h1>
    <dl class="mt-8 divide-y divide-default">
      <div v-if="s?.phone" class="grid gap-1 py-4 sm:grid-cols-3">
        <dt class="text-muted">{{ t('checkout.phone') }}</dt>
        <dd class="sm:col-span-2"><a :href="`tel:${s.phone.replace(/[^\d+]/g, '')}`" class="hover:underline">{{ s.phone }}</a></dd>
      </div>
      <div v-if="s?.email" class="grid gap-1 py-4 sm:grid-cols-3">
        <dt class="text-muted">Email</dt>
        <dd class="sm:col-span-2"><a :href="`mailto:${s.email}`" class="hover:underline">{{ s.email }}</a></dd>
      </div>
      <div v-if="s?.address" class="grid gap-1 py-4 sm:grid-cols-3">
        <dt class="text-muted">{{ t('checkout.address') }}</dt>
        <dd class="sm:col-span-2">{{ s.address }}</dd>
      </div>
      <div v-if="s?.working_hours" class="grid gap-1 py-4 sm:grid-cols-3">
        <dt class="text-muted">{{ t('contacts.hours') }}</dt>
        <dd class="sm:col-span-2">{{ s.working_hours }}</dd>
      </div>
    </dl>
    <div v-if="telegram || whatsapp" class="mt-8 flex flex-col gap-3 sm:flex-row">
      <UButton v-if="telegram" :to="telegram" target="_blank" label="Telegram" icon="i-simple-icons-telegram" color="neutral" size="xl" block class="flex-1 bg-ink text-gold-500 hover:bg-stone-800" />
      <UButton v-if="whatsapp" :to="whatsapp" target="_blank" label="WhatsApp" icon="i-simple-icons-whatsapp" color="neutral" variant="outline" size="xl" block class="flex-1" />
    </div>
  </UContainer>
</template>
