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
const locationConsent = ref(false)
const location = ref<{ latitude: number; longitude: number; accuracy: number } | null>(null)
const locating = ref(false)
const locationError = ref('')
const result = ref<any>(null)
const error = ref('')
const busy = ref(false)
const confirmedLines = ref<any[]>([])
const selectedZone = computed(() => zones.value?.find(item => item.id === zone.value) || null)
const delivery = computed(() => cart.lines.length ? (selectedZone.value?.fee || 0) : 0)
const total = computed(() => cart.subtotal + Number(delivery.value))
const money = (amount: number) => new Intl.NumberFormat('fr-FR').format(Number(amount || 0))
const locationMapUrl = computed(() => {
  if (!location.value) return ''
  const { latitude, longitude } = location.value
  const delta = Math.max(0.003, (location.value.accuracy / 111_000) * 2)
  const params = new URLSearchParams({
    bbox: `${longitude - delta},${latitude - delta},${longitude + delta},${latitude + delta}`,
    layer: 'mapnik',
    marker: `${latitude},${longitude}`,
  })
  return `https://www.openstreetmap.org/export/embed.html?${params.toString()}`
})

function clearLocation() {
  location.value = null
  locationError.value = ''
}

function requestLocation() {
  locationError.value = ''
  if (!locationConsent.value) return
  if (!navigator.geolocation) {
    locationError.value = 'La localisation n’est pas disponible dans ce navigateur.'
    return
  }

  locating.value = true
  navigator.geolocation.getCurrentPosition(
    (position) => {
      location.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
      }
      locating.value = false
    },
    (cause) => {
      locationError.value = cause.code === cause.PERMISSION_DENIED
        ? 'Autorisation refusée. Vous pouvez l’autoriser dans les paramètres du navigateur ou continuer sans partager votre position.'
        : cause.code === cause.TIMEOUT
          ? 'La localisation prend trop de temps. Réessayez ou continuez sans partager votre position.'
          : 'Position indisponible. Vérifiez que la localisation est activée ou continuez sans partager votre position.'
      locating.value = false
    },
    { enableHighAccuracy: true, timeout: 20_000, maximumAge: 0 },
  )
}

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
        delivery_latitude: location.value?.latitude ?? null,
        delivery_longitude: location.value?.longitude ?? null,
        delivery_location_accuracy_m: location.value?.accuracy ?? null,
        delivery_location_consent: Boolean(locationConsent.value && location.value),
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
  <div class="mx-auto max-w-5xl">
    <NuxtLink to="/#catalogue" class="inline-flex min-h-10 items-center text-sm font-medium text-rose-800 hover:underline">← Retour aux produits</NuxtLink>
    <div class="mb-6 mt-3">
      <p class="text-xs font-semibold uppercase tracking-wider text-rose-800">Étape finale</p>
      <h1 class="mt-1 text-3xl font-bold">Finaliser ma commande</h1>
      <p class="mt-2 text-sm text-stone-600">Renseignez la livraison, choisissez votre paiement et vérifiez le total avant de confirmer.</p>
    </div>

    <div class="grid gap-6 md:grid-cols-[1.1fr_.9fr] md:gap-8">
      <section class="order-2 md:order-1">
        <div v-if="result" role="status" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-950 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-100">
          <p class="text-sm font-semibold uppercase tracking-wide text-emerald-800 dark:text-emerald-300">Commande confirmée</p>
          <h2 class="mt-2 text-2xl font-bold">Merci pour votre commande</h2>
          <p class="mt-3">Votre référence est <strong>{{ result.order_number }}</strong>.</p>
          <p class="mt-1">Montant total : <strong>{{ money(result.total) }} FCFA</strong></p>
          <p class="mt-3 text-sm">Gardez cette référence pour toute question au sujet de votre commande.</p>
          <NuxtLink to="/" class="mt-5 inline-flex min-h-11 items-center rounded-xl bg-emerald-800 px-4 py-2.5 font-semibold text-white hover:bg-emerald-900">Retourner à la boutique</NuxtLink>
        </div>

        <div v-else-if="!cart.lines.length" class="rounded-2xl border bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 class="font-semibold">Votre panier est vide</h2>
          <p class="mt-1 text-sm text-stone-600">Ajoutez un produit avant de passer commande.</p>
          <NuxtLink to="/#catalogue" class="mt-4 inline-flex min-h-11 items-center rounded-xl bg-rose-800 px-4 py-2.5 font-semibold text-white">Découvrir les produits</NuxtLink>
        </div>

        <form v-else class="space-y-6" @submit.prevent="submit">
          <div v-if="zonesError" role="alert" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">Impossible de charger les frais de livraison. Actualisez la page ou réessayez plus tard.</div>
          <div v-if="error" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-900">{{ error }}</div>

          <section class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6" aria-labelledby="contact-heading">
            <div class="mb-4 flex items-center gap-3">
              <span class="flex h-8 w-8 items-center justify-center rounded-full bg-rose-100 text-sm font-bold text-rose-900">1</span>
              <div><h2 id="contact-heading" class="font-bold">Vos coordonnées</h2><p class="text-xs text-stone-500">Pour que le livreur puisse vous joindre.</p></div>
            </div>
            <div class="space-y-4">
              <label class="block text-sm font-medium" for="customer-alias">Nom ou pseudonyme <span class="font-normal text-stone-500">(facultatif)</span>
                <input id="customer-alias" v-model="alias" maxlength="100" autocomplete="nickname" class="mt-1.5 min-h-12 w-full rounded-xl border border-stone-300 px-3 py-3" placeholder="Le nom à communiquer au livreur">
              </label>
              <label class="block text-sm font-medium" for="customer-phone">Téléphone <span class="text-rose-700">*</span>
                <input id="customer-phone" v-model="phone" required type="tel" maxlength="20" autocomplete="tel" class="mt-1.5 min-h-12 w-full rounded-xl border border-stone-300 px-3 py-3" placeholder="Ex. 70 00 00 00">
              </label>
              <label class="block text-sm font-medium" for="delivery-address">Adresse ou point de repère <span class="text-rose-700">*</span>
                <textarea id="delivery-address" v-model="address" required minlength="3" maxlength="500" autocomplete="street-address" class="mt-1.5 w-full rounded-xl border border-stone-300 px-3 py-3" placeholder="Quartier, rue et repère proche" rows="3" />
              </label>
            </div>
          </section>

          <section class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6" aria-labelledby="delivery-heading">
            <div class="mb-4 flex items-center gap-3">
              <span class="flex h-8 w-8 items-center justify-center rounded-full bg-rose-100 text-sm font-bold text-rose-900">2</span>
              <div><h2 id="delivery-heading" class="font-bold">Zone de livraison</h2><p class="text-xs text-stone-500">Le prix et le délai s’affichent pour chaque zone.</p></div>
            </div>
            <p v-if="!zones && !zonesError" role="status" class="mb-3 text-sm text-stone-500">Chargement des zones et des frais…</p>
            <fieldset :disabled="!!zonesError || !zones?.length" class="space-y-2">
              <legend class="sr-only">Choisissez votre zone de livraison</legend>
              <label v-for="item in zones || []" :key="item.id" class="flex cursor-pointer items-start gap-3 rounded-xl border p-3.5 transition hover:border-rose-400" :class="zone === item.id ? 'border-rose-700 bg-rose-50 ring-1 ring-rose-700 dark:bg-rose-950/30' : 'border-stone-200 dark:border-slate-700'">
                <input v-model="zone" type="radio" name="delivery-zone" :value="item.id" required class="mt-1 accent-rose-800">
                <span class="min-w-0 flex-1">
                  <span class="flex flex-wrap items-start justify-between gap-2">
                    <span class="font-semibold">{{ item.name }}</span>
                    <span class="shrink-0 text-sm font-bold">{{ money(item.fee) }} FCFA</span>
                  </span>
                  <span v-if="item.neighborhoods" class="mt-1 block text-xs leading-5 text-stone-600">{{ item.neighborhoods }}</span>
                  <span v-if="item.estimated_delay" class="mt-1 block text-xs font-medium text-rose-800">Délai indicatif : {{ item.estimated_delay }}</span>
                </span>
              </label>
            </fieldset>

            <details class="mt-4 rounded-xl border border-stone-200 p-4 dark:border-slate-700">
              <summary class="cursor-pointer font-semibold">Partager ma position GPS <span class="font-normal text-stone-500">(facultatif)</span></summary>
              <div class="mt-3 space-y-3">
                <p class="text-sm leading-6 text-stone-600">Cela peut aider le livreur à vous trouver. Le navigateur demandera votre autorisation. Si vous affichez la carte, OpenStreetMap reçoit vos coordonnées. Vous pouvez passer commande sans partager votre position.</p>
                <label class="flex items-start gap-2 text-sm">
                  <input v-model="locationConsent" type="checkbox" class="mt-1 accent-rose-800" @change="!locationConsent && clearLocation()">
                  <span>J’accepte de joindre ma position à cette commande et de l’afficher sur OpenStreetMap.</span>
                </label>
                <div class="flex flex-wrap gap-2">
                  <button type="button" :disabled="!locationConsent || locating" class="min-h-10 rounded-lg border px-3 py-2 text-sm font-medium disabled:opacity-50" @click="requestLocation">
                    {{ locating ? 'Recherche en cours…' : location ? 'Actualiser ma position' : 'Me localiser' }}
                  </button>
                  <button v-if="location" type="button" class="min-h-10 rounded-lg px-3 py-2 text-sm text-rose-800 underline" @click="clearLocation">Retirer ma position</button>
                </div>
                <p v-if="locationError" role="status" class="text-sm text-amber-800">{{ locationError }}</p>
                <div v-if="location && locationConsent" class="space-y-2">
                  <p class="text-sm text-emerald-800">Position obtenue (précision estimée : ±{{ Math.round(location.accuracy) }} m). Elle sera jointe à la commande.</p>
                  <iframe :src="locationMapUrl" title="Carte de votre position pour la livraison" class="h-56 w-full rounded-lg border" loading="lazy" referrerpolicy="no-referrer" />
                  <a :href="`https://www.openstreetmap.org/?mlat=${location.latitude}&mlon=${location.longitude}#map=18/${location.latitude}/${location.longitude}`" target="_blank" rel="noreferrer" class="text-sm font-medium text-rose-800 underline">Ouvrir la carte en grand</a>
                </div>
              </div>
            </details>
          </section>

          <section class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6" aria-labelledby="payment-heading">
            <div class="mb-4 flex items-center gap-3">
              <span class="flex h-8 w-8 items-center justify-center rounded-full bg-rose-100 text-sm font-bold text-rose-900">3</span>
              <div><h2 id="payment-heading" class="font-bold">Mode de paiement</h2><p class="text-xs text-stone-500">Choisissez comment régler la commande.</p></div>
            </div>
            <fieldset class="space-y-2">
              <legend class="sr-only">Sélectionnez le mode de paiement</legend>
              <label class="flex cursor-pointer items-start gap-3 rounded-xl border p-3.5" :class="paymentMethod === 'Paiement à la livraison' ? 'border-rose-700 bg-rose-50 ring-1 ring-rose-700 dark:bg-rose-950/30' : 'border-stone-200 dark:border-slate-700'">
                <input v-model="paymentMethod" type="radio" name="payment-method" value="Paiement à la livraison" class="mt-1 accent-rose-800">
                <span><span class="block font-semibold">Paiement à la livraison</span><span class="mt-1 block text-xs text-stone-600">Réglez votre commande au moment de la remise.</span></span>
              </label>
              <label class="flex cursor-pointer items-start gap-3 rounded-xl border p-3.5" :class="paymentMethod === 'GeniusPay' ? 'border-rose-700 bg-rose-50 ring-1 ring-rose-700 dark:bg-rose-950/30' : 'border-stone-200 dark:border-slate-700'">
                <input v-model="paymentMethod" type="radio" name="payment-method" value="GeniusPay" class="mt-1 accent-rose-800">
                <span><span class="block font-semibold">GeniusPay</span><span class="mt-1 block text-xs text-stone-600">Paiement {{ geniusPayEnvironment === 'sandbox' ? 'de test' : 'sécurisé' }} sur la page GeniusPay.</span></span>
              </label>
            </fieldset>
            <p v-if="paymentMethod === 'GeniusPay' && geniusPayEnvironment === 'sandbox'" class="mt-3 rounded-xl bg-amber-50 p-3 text-sm text-amber-950">Le paiement est en mode test. N’effectuez pas de paiement réel par cette option.</p>
          </section>

          <button :disabled="busy || !cart.lines.length || !zone || !!zonesError" class="min-h-12 w-full rounded-xl bg-rose-800 px-5 py-3 font-semibold text-white shadow-sm hover:bg-rose-900 disabled:cursor-not-allowed disabled:opacity-50">
            {{ busy ? 'Envoi de la commande…' : paymentMethod === 'GeniusPay' ? 'Continuer vers GeniusPay' : 'Confirmer la commande' }}
          </button>
          <p class="text-center text-xs leading-5 text-stone-500">En confirmant, vous acceptez que vos coordonnées servent à traiter et livrer cette commande.</p>
        </form>
      </section>

      <aside v-if="result || cart.lines.length" class="order-1 h-fit rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 md:sticky md:top-4 md:order-2 md:p-6">
        <div class="flex items-start justify-between gap-3">
          <div><h2 class="text-xl font-bold">Votre panier</h2><p class="mt-1 text-sm text-stone-500">{{ result ? 'Commande confirmée' : `${cart.count} article${cart.count > 1 ? 's' : ''}` }}</p></div>
          <NuxtLink v-if="!result && cart.lines.length" to="/#catalogue" class="text-sm font-medium text-rose-800 underline">Modifier</NuxtLink>
        </div>
        <div v-for="line in (result ? confirmedLines : cart.lines)" :key="line.variant.id" class="flex items-start justify-between gap-3 border-b border-stone-200 py-3 text-sm dark:border-slate-700">
          <div class="min-w-0 flex-1">
            <p class="font-semibold">{{ line.productName }}</p>
            <p v-if="line.variant.name" class="mt-1 text-xs text-stone-500">{{ line.variant.name }}</p>
            <div v-if="!result" class="mt-2 flex flex-wrap items-center gap-2">
              <div class="inline-flex min-h-9 items-center rounded-lg border border-stone-300 dark:border-slate-600">
                <button type="button" :disabled="line.quantity <= 1" :aria-label="`Diminuer la quantité de ${line.productName}`" class="px-3 py-1.5 disabled:opacity-40" @click="cart.decrement(line.variant.id)">−</button>
                <span class="min-w-8 text-center" aria-live="polite">{{ line.quantity }}</span>
                <button type="button" :disabled="line.quantity >= line.variant.stock" :aria-label="`Augmenter la quantité de ${line.productName}`" class="px-3 py-1.5 disabled:opacity-40" @click="cart.increment(line.variant.id)">+</button>
              </div>
              <button type="button" class="min-h-9 px-2 text-xs font-medium text-rose-800 underline" :aria-label="`Retirer ${line.productName} du panier`" @click="cart.remove(line.variant.id)">Retirer</button>
            </div>
            <p v-else class="mt-1 text-xs text-stone-500">Quantité : {{ line.quantity }}</p>
          </div>
          <span class="shrink-0 font-semibold">{{ money(line.variant.price * line.quantity) }} F</span>
        </div>
        <p v-if="!result && !cart.lines.length" class="py-5 text-sm text-stone-600">Votre panier est vide.</p>
        <div class="space-y-2 pt-4 text-sm">
          <p class="flex justify-between gap-4"><span>Sous-total</span><span>{{ money(result ? result.subtotal : cart.subtotal) }} F</span></p>
          <p class="flex justify-between gap-4"><span>Livraison <span v-if="selectedZone" class="text-xs text-stone-500">· {{ selectedZone.name }}</span></span><span v-if="result">{{ money(result.delivery_fee) }} F</span><span v-else-if="zone">{{ money(delivery) }} F</span><span v-else class="text-right text-xs text-stone-500">Choisir une zone</span></p>
          <p class="flex justify-between gap-4 border-t border-stone-200 pt-3 text-lg font-bold dark:border-slate-700"><span>Total</span><span>{{ money(result ? result.total : total) }} FCFA</span></p>
        </div>
        <div class="mt-4 rounded-xl bg-rose-50 p-3 text-sm leading-5 text-rose-950 dark:bg-rose-950/40 dark:text-rose-100">
          <p class="font-semibold">Livraison discrète</p>
          <p class="mt-1 text-xs">Emballage neutre et scellé.</p>
        </div>
      </aside>
    </div>
  </div>
</template>
