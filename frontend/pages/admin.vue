<script setup lang="ts">
useHead({ title: 'Administration | Marasses' })

const config = useRuntimeConfig()
const token = ref('')
const password = ref('')
const activeTab = ref<'orders' | 'products'>('orders')
const orders = ref<any[]>([])
const products = ref<any[]>([])
const busy = ref(false)
const error = ref('')
const notice = ref('')

function api(path: string, options: Record<string, any> = {}) {
  return $fetch(`${config.public.apiBase}${path}`, {
    ...options,
    headers: { ...options.headers, Authorization: `Bearer ${token.value}` },
  })
}

async function loadDashboard() {
  error.value = ''
  busy.value = true
  try {
    const [orderRows, productRows] = await Promise.all([
      api('/admin/orders'),
      api('/admin/products'),
    ])
    orders.value = orderRows as any[]
    products.value = productRows as any[]
  } catch (cause: any) {
    if (cause?.status === 401) signOut()
    error.value = cause?.data?.detail || 'Impossible de charger les données. Vérifie la connexion puis réessaie.'
  } finally {
    busy.value = false
  }
}

async function signIn() {
  error.value = ''
  busy.value = true
  try {
    const result = await $fetch<{ token: string }>(`${config.public.apiBase}/admin/login`, {
      method: 'POST', body: { password: password.value },
    })
    token.value = result.token
    if (import.meta.client) sessionStorage.setItem('marasses-admin-token', result.token)
    password.value = ''
    await loadDashboard()
  } catch (cause: any) {
    error.value = cause?.data?.detail || 'Connexion impossible. Vérifie le mot de passe administrateur.'
  } finally {
    busy.value = false
  }
}

function signOut() {
  token.value = ''
  orders.value = []
  products.value = []
  if (import.meta.client) sessionStorage.removeItem('marasses-admin-token')
}

async function updateStatus(order: any) {
  error.value = ''
  notice.value = ''
  try {
    await api(`/admin/orders/${order.id}/status`, { method: 'PATCH', body: { order_status: order.order_status } })
    notice.value = `Commande ${order.order_number} mise à jour.`
  } catch (cause: any) {
    error.value = cause?.data?.detail || 'La commande n’a pas pu être modifiée.'
    await loadDashboard()
  }
}

async function updateVariant(variant: any) {
  error.value = ''
  notice.value = ''
  try {
    await api(`/admin/variants/${variant.variant_id}`, {
      method: 'PATCH', body: { price: Number(variant.price), stock_quantity: Number(variant.stock_quantity) },
    })
    notice.value = `Stock et prix enregistrés pour ${variant.name}.`
  } catch (cause: any) {
    error.value = cause?.data?.detail || 'Les changements n’ont pas pu être enregistrés.'
    await loadDashboard()
  }
}

onMounted(() => {
  const savedToken = sessionStorage.getItem('marasses-admin-token')
  if (savedToken) {
    token.value = savedToken
    void loadDashboard()
  }
})

const money = (value: number) => new Intl.NumberFormat('fr-FR').format(Number(value || 0))
const statuses: Record<string, string> = {
  processing: 'À traiter', preparing: 'En préparation', shipped: 'Expédiée', delivered: 'Livrée',
}
</script>

<template>
  <section class="mx-auto max-w-6xl py-8">
    <div class="mb-8 flex items-center justify-between gap-4">
      <div>
        <p class="text-sm font-medium uppercase tracking-widest text-rose-700">Marasses</p>
        <h1 class="mt-1 text-3xl font-bold">Administration</h1>
      </div>
      <button v-if="token" class="rounded-lg border px-4 py-2 text-sm hover:bg-stone-100" @click="signOut">Se déconnecter</button>
    </div>

    <div v-if="error" role="alert" class="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{{ error }}</div>
    <div v-if="notice" role="status" class="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{{ notice }}</div>

    <form v-if="!token" class="mx-auto max-w-md rounded-2xl border bg-white p-6 shadow-sm" @submit.prevent="signIn">
      <h2 class="text-xl font-semibold">Connexion réservée</h2>
      <p class="mt-2 text-sm text-stone-600">Entre le mot de passe administrateur configuré dans Render. Il ne sera pas conservé dans le navigateur.</p>
      <label class="mt-5 block text-sm font-medium" for="admin-password">Mot de passe administrateur</label>
      <input id="admin-password" v-model="password" type="password" autocomplete="current-password" required class="mt-2 w-full rounded-lg border border-stone-300 px-3 py-3" />
      <button :disabled="busy" class="mt-4 w-full rounded-xl bg-rose-800 px-4 py-3 font-semibold text-white disabled:opacity-50">{{ busy ? 'Connexion…' : 'Se connecter' }}</button>
    </form>

    <template v-else>
      <div class="mb-6 flex gap-2 border-b">
        <button class="border-b-2 px-4 py-3 font-medium" :class="activeTab === 'orders' ? 'border-rose-800 text-rose-900' : 'border-transparent text-stone-500'" @click="activeTab = 'orders'">Commandes ({{ orders.length }})</button>
        <button class="border-b-2 px-4 py-3 font-medium" :class="activeTab === 'products' ? 'border-rose-800 text-rose-900' : 'border-transparent text-stone-500'" @click="activeTab = 'products'">Produits ({{ products.length }})</button>
        <button class="ml-auto px-3 py-3 text-sm text-stone-600 hover:text-rose-800" :disabled="busy" @click="loadDashboard">Actualiser</button>
      </div>

      <div v-if="busy" class="rounded-xl border bg-white p-8 text-center text-stone-600">Chargement…</div>
      <div v-else-if="activeTab === 'orders'" class="space-y-4">
        <p v-if="!orders.length" class="rounded-xl border bg-white p-8 text-center text-stone-600">Aucune commande pour le moment.</p>
        <article v-for="order in orders" :key="order.id" class="rounded-2xl border bg-white p-5 shadow-sm">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h2 class="text-lg font-semibold">{{ order.order_number }}</h2>
              <p class="mt-1 text-sm text-stone-600">{{ new Date(order.created_at).toLocaleString('fr-FR') }} · {{ order.zone || 'Zone inconnue' }}</p>
            </div>
            <strong class="text-lg">{{ money(order.total_amount) }} FCFA</strong>
          </div>
          <div class="mt-4 grid gap-4 border-t pt-4 sm:grid-cols-2">
            <div class="space-y-1 text-sm">
              <p><strong>Client :</strong> {{ order.customer_alias || 'Client' }} · <a class="text-rose-800 underline" :href="`tel:${order.customer_phone}`">{{ order.customer_phone }}</a></p>
              <p><strong>Adresse :</strong> {{ order.delivery_address }}</p>
              <p><strong>Paiement :</strong> {{ order.payment_method }} · {{ order.payment_status }}</p>
              <a v-if="order.delivery_latitude && order.delivery_longitude" class="inline-block text-rose-800 underline" :href="`https://www.openstreetmap.org/?mlat=${order.delivery_latitude}&mlon=${order.delivery_longitude}#map=17/${order.delivery_latitude}/${order.delivery_longitude}`" target="_blank" rel="noopener noreferrer">Voir la position sur la carte</a>
            </div>
            <div>
              <p class="mb-2 text-sm font-semibold">Articles</p>
              <ul class="space-y-1 text-sm text-stone-700"><li v-for="(item, index) in order.items" :key="index">{{ item.product }} · {{ item.variant }} × {{ item.quantity }} — {{ money(item.unit_price * item.quantity) }} F</li></ul>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap items-center justify-between gap-3 border-t pt-4">
            <p class="text-sm text-stone-600">Sous-total {{ money(order.subtotal_amount) }} F · livraison {{ money(order.delivery_fee) }} F</p>
            <label class="flex items-center gap-2 text-sm">État
              <select v-model="order.order_status" class="rounded-lg border p-2" @change="updateStatus(order)">
                <option v-for="(label, value) in statuses" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>
          </div>
        </article>
      </div>

      <div v-else class="overflow-hidden rounded-2xl border bg-white shadow-sm">
        <p v-if="!products.length" class="p-8 text-center text-stone-600">Aucun produit trouvé.</p>
        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[680px] text-left text-sm">
            <thead class="bg-stone-100 text-stone-600"><tr><th class="p-3">Produit</th><th class="p-3">Format</th><th class="p-3">Prix (FCFA)</th><th class="p-3">Stock</th><th class="p-3"></th></tr></thead>
            <tbody><tr v-for="product in products" :key="product.variant_id" class="border-t">
              <td class="p-3"><strong>{{ product.name }}</strong><span class="block text-xs text-stone-500">{{ product.category }}<span v-if="!product.is_active"> · masqué</span></span></td>
              <td class="p-3">{{ product.variant_name || 'Format standard' }}</td>
              <td class="p-3"><input v-model.number="product.price" type="number" min="0" step="50" class="w-32 rounded-lg border p-2" :aria-label="`Prix de ${product.name}`" /></td>
              <td class="p-3"><input v-model.number="product.stock_quantity" type="number" min="0" step="1" class="w-24 rounded-lg border p-2" :aria-label="`Stock de ${product.name}`" /></td>
              <td class="p-3"><button class="rounded-lg border border-rose-200 px-3 py-2 text-rose-900 hover:bg-rose-50" @click="updateVariant(product)">Enregistrer</button></td>
            </tr></tbody>
          </table>
        </div>
      </div>
    </template>
  </section>
</template>
