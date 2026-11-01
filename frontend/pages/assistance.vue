<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const phone = ref('')
const orderNumber = ref('')
const topic = ref('Commande')
const message = ref('')
const consent = ref(false)
const website = ref('')
const busy = ref(false)
const error = ref('')
const confirmation = ref('')
const whatsappNumber = String(config.public.whatsappSupportNumber || '').replace(/\D/g, '')
const whatsappUrl = computed(() => {
  if (!whatsappNumber || !phone.value.trim() || !message.value.trim()) return ''
  const text = [
    'Bonjour Marasses, j’ai besoin d’aide.',
    orderNumber.value.trim() ? `Référence de commande : ${orderNumber.value.trim()}` : '',
    `Sujet : ${topic.value}`,
    `Mon téléphone : ${phone.value.trim()}`,
    message.value.trim(),
  ].filter(Boolean).join('\n')
  return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(text)}`
})

async function submitRequest() {
  error.value = ''
  confirmation.value = ''
  busy.value = true
  try {
    const result = await $fetch<{ reference: string }>(`${apiBase}/support-requests`, {
      method: 'POST',
      body: {
        order_number: orderNumber.value || null,
        customer_phone: phone.value,
        topic: topic.value,
        message: message.value,
        consent: consent.value,
        website: website.value,
      },
    })
    confirmation.value = result.reference
    orderNumber.value = ''
    phone.value = ''
    topic.value = 'Commande'
    message.value = ''
    consent.value = false
    website.value = ''
  } catch (cause: any) {
    error.value = cause?.data?.detail || 'Envoi impossible pour le moment. Réessayez plus tard.'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl">
    <NuxtLink to="/" class="text-sm text-rose-800">← Retour à la boutique</NuxtLink>
    <h1 class="my-5 text-3xl font-bold">Aide et réclamations</h1>
    <p class="mb-6 text-stone-600">Décrivez votre problème. Nous enregistrerons votre demande pour pouvoir la traiter. Vous pouvez aussi nous écrire sur WhatsApp si cette option est configurée.</p>

    <div v-if="confirmation" role="status" class="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-900">
      <p class="font-semibold">Votre demande a été envoyée.</p>
      <p class="mt-1 text-sm">Conservez cette référence : <strong>{{ confirmation }}</strong></p>
    </div>

    <form class="space-y-4 rounded-2xl border bg-white p-5" @submit.prevent="submitRequest">
      <label class="block text-sm font-medium">
        Sujet
        <select v-model="topic" class="mt-1 w-full rounded-xl border p-3">
          <option>Commande</option>
          <option>Livraison</option>
          <option>Paiement</option>
          <option>Produit</option>
          <option>Autre</option>
        </select>
      </label>
      <label class="block text-sm font-medium">
        Référence de commande <span class="font-normal text-stone-500">(facultatif)</span>
        <input v-model="orderNumber" maxlength="20" class="mt-1 w-full rounded-xl border p-3" placeholder="Ex. CMD-12345678">
      </label>
      <label class="block text-sm font-medium">
        Téléphone pour vous répondre
        <input v-model="phone" required type="tel" maxlength="20" autocomplete="tel" class="mt-1 w-full rounded-xl border p-3" placeholder="Votre numéro de téléphone">
      </label>
      <label class="block text-sm font-medium">
        Expliquez le problème
        <textarea v-model="message" required minlength="10" maxlength="2000" rows="5" class="mt-1 w-full rounded-xl border p-3" placeholder="Décrivez ce qui s’est passé…" />
      </label>
      <p class="text-xs text-stone-500">N’indiquez pas de mot de passe, de données bancaires ni d’informations médicales ou intimes.</p>

      <label class="flex items-start gap-2 text-sm">
        <input v-model="consent" required type="checkbox" class="mt-1">
        <span>J’accepte que Marasses utilise mon téléphone, ma référence de commande et mon message pour traiter cette demande.</span>
      </label>

      <input v-model="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="pointer-events-none absolute -left-[10000px] h-px w-px" aria-label="Ne pas remplir">
      <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>
      <button :disabled="busy" class="w-full rounded-xl bg-rose-800 p-3 font-semibold text-white disabled:opacity-50">
        {{ busy ? 'Envoi…' : 'Envoyer ma réclamation' }}
      </button>

      <a v-if="whatsappUrl" :href="whatsappUrl" target="_blank" rel="noopener noreferrer" class="block rounded-xl border border-emerald-700 p-3 text-center font-semibold text-emerald-800 hover:bg-emerald-50">
        Continuer sur WhatsApp
      </a>
    </form>
  </div>
</template>
