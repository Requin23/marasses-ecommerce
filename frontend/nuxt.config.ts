export default defineNuxtConfig({
  modules: ['@pinia/nuxt', '@nuxtjs/tailwindcss'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    apiInternalBase: process.env.NUXT_API_INTERNAL_BASE || 'http://api:8000/api',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api',
      geniusPayEnvironment: process.env.NUXT_PUBLIC_GENIUSPAY_ENVIRONMENT || 'sandbox',
      whatsappSupportNumber: process.env.NUXT_PUBLIC_WHATSAPP_NUMBER || '',
    },
  },
  app: {
    head: {
      title: 'Marasses | Bien-être intime',
      meta: [{ name: 'description', content: 'Bien-être intime, en toute discrétion.' }],
    },
  },
})
