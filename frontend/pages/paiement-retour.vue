<script setup lang="ts">
const config = useRuntimeConfig()
const route = useRoute()
const orderNumber = computed(() => typeof route.query.commande === 'string' ? route.query.commande : '')
const token = computed(() => typeof route.query.jeton === 'string' ? route.query.jeton : '')
const status = ref('checking')
const error = ref('')

async function checkPayment() {
  if (!orderNumber.value || !token.value) {
    status.value = 'unknown'
    return
  }
  error.value = ''
  status.value = 'checking'
  try {
    const result = await $fetch<{ status: string }>(`${config.public.apiBase}/orders/${encodeURIComponent(orderNumber.value)}/payment-status`, {
      query: { token: token.value },
    })
    status.value = result.status
  } catch {
    status.value = 'unknown'
    error.value = 'La vérification est momentanément indisponible. Réessaie dans quelques instants.'
  }
}

onMounted(checkPayment)
const title = computed(() => {
  if (status.value === 'completed') return 'Paiement confirmé'
  if (status.value === 'failed' || status.value === 'cancelled' || status.value === 'expired') return 'Paiement non confirmé'
  return 'Paiement en cours de confirmation'
})
</script>

<template>
  <section class="mx-auto max-w-xl rounded-2xl border bg-white p-6 md:p-8">
    <p class="text-sm font-medium text-rose-800">MARASSES · PAIEMENT</p>
    <h1 class="mt-3 text-2xl font-bold">{{ title }}</h1>
    <p v-if="orderNumber" class="mt-3 text-stone-700">Référence de commande : <strong>{{ orderNumber }}</strong></p>
    <p class="mt-3 text-sm text-stone-600">
      <template v-if="status === 'completed'">Le paiement a été confirmé par GeniusPay.</template>
      <template v-else-if="status === 'failed' || status === 'cancelled' || status === 'expired'">GeniusPay n’a pas confirmé le paiement. Le stock réservé a été libéré.</template>
      <template v-else>Nous attendons la confirmation sécurisée de GeniusPay. Le retour du navigateur ne suffit pas à confirmer le paiement.</template>
    </p>
    <p v-if="error" class="mt-3 text-sm text-amber-800">{{ error }}</p>
    <button v-if="status !== 'completed' && status !== 'failed' && status !== 'cancelled' && status !== 'expired'" class="mt-5 rounded-xl border px-4 py-3 text-sm" @click="checkPayment">Vérifier à nouveau</button>
    <NuxtLink to="/" class="mt-5 inline-block rounded-xl bg-rose-800 px-4 py-3 text-white">Retour à la boutique</NuxtLink>
  </section>
</template>
