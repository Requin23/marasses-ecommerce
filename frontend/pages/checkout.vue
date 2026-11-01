<script setup lang="ts">
const config = useRuntimeConfig()
const cart = useCartStore()
const geniusPayEnvironment = config.public.geniusPayEnvironment
const apiBase = import.meta.server ? config.apiInternalBase : config.public.apiBase
const { data: zones, error: zonesError } = await useFetch<any[]>(`${apiBase}/delivery-zones`, { key: 'delivery-zones' })
const zone = ref('')
const alias = ref('')
const phone = ref('')
const address = ref('')
const paymentMethod = ref('Paiement à la livraison')
const result = ref<any>(null)
const error = ref('')
const busy = ref(false)
const confirmedLines = ref<any[]>([])
const delivery = computed(() => cart.lines.length ? (zones.value?.find(item => item.id === zone.value)?.fee || 0) : 0)
const total = computed(() => cart.subtotal + Number(delivery.value))

async function submit() {
  error.value = ''
  busy.value = true
  try {
    const submittedLines = cart.lines.map(line => ({
      productName: line.productName,
      quantity: line.quantity,
      variant: { ...line.variant },
    }))
    result.value = await $fetch(`${config.public.apiBase}/orders`, {
      method: 'POST',
      body: {
        delivery_zone_id: zone.value,
        customer_alias: alias.value || null,
        customer_phone: phone.value,
        delivery_address: address.value,
        payment_method: paymentMethod.value,
        items: cart.lines.map(line => ({ variant_id: line.variant.id, quantity: line.quantity })),
      },
    })
    if (result.value.payment_url) {
      cart.clear()
      window.location.assign(result.value.payment_url)
      return
    }
    confirmedLines.value = submittedLines
    cart.clear()
  } catch (cause: any) {
    error.value = cause?.data?.detail || 'Commande non envoyée. Vérifiez les informations et réessayez.'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="mx-auto grid max-w-4xl gap-8 md:grid-cols-2">
    <section>
      <NuxtLink to="/" class="text-sm text-rose-800">← Continuer mes achats</NuxtLink>
      <h1 class="my-5 text-3xl font-bold">Commande discrète</h1>

      <div v-if="result" class="rounded-2xl bg-emerald-50 p-6">
        <h2 class="text-xl font-semibold">Merci pour votre commande</h2>
        <p class="mt-2">Référence : <strong>{{ result.order_number }}</strong></p>
        <p class="mt-2">Total : {{ result.total }} FCFA</p>
      </div>
      <div v-else-if="!cart.lines.length" class="rounded-2xl border bg-white p-6">
        <p class="font-medium">Votre panier est vide.</p>
        <NuxtLink to="/" class="mt-3 inline-block text-sm text-rose-800 underline">Découvrir le catalogue</NuxtLink>
      </div>
      <form v-else class="space-y-4" @submit.prevent="submit">
        <p v-if="zonesError" class="rounded-xl bg-amber-50 p-3 text-sm text-amber-900">Impossible de charger les zones. Actualisez la page ou réessayez plus tard.</p>
        <input v-model="alias" maxlength="100" autocomplete="nickname" class="w-full rounded-xl border p-3" placeholder="Pseudonyme (facultatif)">
        <input v-model="phone" required type="tel" maxlength="20" autocomplete="tel" class="w-full rounded-xl border p-3" placeholder="Téléphone">
        <select v-model="zone" required :disabled="!!zonesError || !zones?.length" class="w-full rounded-xl border p-3 disabled:bg-stone-100">
          <option value="" disabled>Zone de livraison</option>
          <option v-for="item in zones || []" :key="item.id" :value="item.id">{{ item.name }} · {{ item.fee }} FCFA</option>
        </select>
        <textarea v-model="address" required maxlength="500" autocomplete="street-address" class="w-full rounded-xl border p-3" placeholder="Point de repère / adresse" rows="3" />
        <select v-model="paymentMethod" class="w-full rounded-xl border p-3">
          <option>Paiement à la livraison</option>
          <option>GeniusPay</option>
        </select>
        <p v-if="paymentMethod === 'GeniusPay'" class="rounded-xl bg-stone-100 p-3 text-sm text-stone-700">
          Paiement {{ geniusPayEnvironment === 'sandbox' ? 'de test' : 'réel' }} par GeniusPay. Les moyens disponibles s’afficheront sur leur page.
        </p>
        <p v-if="error" class="text-sm text-red-700">{{ error }}</p>
        <button :disabled="busy || !cart.lines.length || !zone || !!zonesError" class="w-full rounded-xl bg-rose-800 p-3 font-semibold text-white disabled:opacity-50">
          {{ busy ? 'Envoi…' : 'Confirmer la commande' }}
        </button>
      </form>
    </section>

    <aside class="h-fit rounded-2xl border bg-white p-5">
      <h2 class="text-xl font-semibold">Récapitulatif</h2>
      <div v-for="line in (result ? confirmedLines : cart.lines)" :key="line.variant.id" class="flex items-start justify-between gap-3 border-b py-3 text-sm">
        <div class="min-w-0 flex-1">
          <p class="font-medium">{{ line.productName }}</p>
          <p v-if="line.variant.name" class="mt-1 text-xs text-stone-500">{{ line.variant.name }}</p>
          <div v-if="!result" class="mt-2 flex flex-wrap items-center gap-2">
            <div class="inline-flex items-center rounded-lg border">
              <button type="button" :disabled="line.quantity <= 1" :aria-label="`Diminuer la quantité de ${line.productName}`" class="px-3 py-1.5 disabled:opacity-40" @click="cart.decrement(line.variant.id)">−</button>
              <span class="min-w-8 text-center">{{ line.quantity }}</span>
              <button type="button" :disabled="line.quantity >= line.variant.stock" :aria-label="`Augmenter la quantité de ${line.productName}`" class="px-3 py-1.5 disabled:opacity-40" @click="cart.increment(line.variant.id)">+</button>
            </div>
            <button type="button" class="text-xs text-rose-800 underline" :aria-label="`Retirer ${line.productName} du panier`" @click="cart.remove(line.variant.id)">Retirer</button>
          </div>
          <p v-else class="mt-1 text-xs text-stone-500">Quantité : {{ line.quantity }}</p>
        </div>
        <span class="shrink-0 font-medium">{{ line.variant.price * line.quantity }} F</span>
      </div>
      <p class="mt-4 flex justify-between">Sous-total <span>{{ result ? result.subtotal : cart.subtotal }} F</span></p>
      <p class="mt-2 flex justify-between">Livraison <span>{{ result ? result.delivery_fee : delivery }} F</span></p>
      <p class="mt-3 flex justify-between border-t pt-3 text-lg font-bold">Total <span>{{ result ? result.total : total }} FCFA</span></p>
      <p class="mt-5 rounded-xl bg-rose-50 p-3 text-sm text-rose-900">Livraison sous packaging 100% neutre et scellé.</p>
    </aside>
  </div>
</template>
