<script setup lang="ts">
useHead({ title: 'Administration | Marasses' })

const config = useRuntimeConfig()
const token = ref('')
const password = ref('')
const activeTab = ref<'orders' | 'products'>('orders')
const searchQuery = ref('')
const statusFilter = ref('all')
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
    const [orderRows, productRows] = await Promise.all([api('/admin/orders'), api('/admin/products')])
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
const statusLabel = (status: string) => statuses[status] || (status === 'awaiting_payment' ? 'Paiement attendu' : status)
const statusStyle = (status: string) => ({
  processing: 'bg-amber-50 text-amber-800 ring-amber-200',
  awaiting_payment: 'bg-orange-50 text-orange-800 ring-orange-200',
  preparing: 'bg-blue-50 text-blue-800 ring-blue-200',
  shipped: 'bg-violet-50 text-violet-800 ring-violet-200',
  delivered: 'bg-emerald-50 text-emerald-800 ring-emerald-200',
}[status] || 'bg-stone-100 text-stone-700 ring-stone-200')
const pendingOrders = computed(() => orders.value.filter(order => ['processing', 'awaiting_payment'].includes(order.order_status)).length)
const preparingOrders = computed(() => orders.value.filter(order => order.order_status === 'preparing').length)
const deliveredOrders = computed(() => orders.value.filter(order => order.order_status === 'delivered').length)
const lowStockCount = computed(() => products.value.filter(product => product.stock_quantity <= 5).length)
const filteredOrders = computed(() => {
  const query = searchQuery.value.trim().toLocaleLowerCase('fr')
  return orders.value.filter((order) => {
    const matchesQuery = !query || [order.order_number, order.customer_alias, order.customer_phone, order.delivery_address]
      .some(value => String(value || '').toLocaleLowerCase('fr').includes(query))
    return matchesQuery && (statusFilter.value === 'all' || order.order_status === statusFilter.value)
  })
})
const filteredProducts = computed(() => {
  const query = searchQuery.value.trim().toLocaleLowerCase('fr')
  return products.value.filter(product => !query || [product.name, product.category, product.variant_name]
    .some(value => String(value || '').toLocaleLowerCase('fr').includes(query)))
})
</script>

<template>
  <section class="mx-auto max-w-7xl py-6 sm:py-10">
    <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-900 text-lg font-bold text-white">M</div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-rose-700">Marasses · Boutique</p>
          <h1 class="text-2xl font-bold sm:text-3xl">Tableau de bord</h1>
        </div>
      </div>
      <button v-if="token" class="rounded-xl border border-stone-300 bg-white px-4 py-2.5 text-sm font-medium hover:bg-stone-100" @click="signOut">Se déconnecter</button>
    </div>

    <div v-if="error" role="alert" class="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{{ error }}</div>
    <div v-if="notice" role="status" class="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{{ notice }}</div>

    <form v-if="!token" class="mx-auto max-w-md rounded-2xl border bg-white p-6 shadow-sm sm:p-8" @submit.prevent="signIn">
      <h2 class="text-xl font-semibold">Connexion réservée</h2>
      <p class="mt-2 text-sm text-stone-600">Entre le mot de passe administrateur configuré dans Render. Il ne sera pas conservé dans le navigateur.</p>
      <label class="mt-5 block text-sm font-medium" for="admin-password">Mot de passe administrateur</label>
      <input id="admin-password" v-model="password" type="password" autocomplete="current-password" required class="mt-2 w-full rounded-lg border border-stone-300 px-3 py-3" />
      <button :disabled="busy" class="mt-4 w-full rounded-xl bg-rose-800 px-4 py-3 font-semibold text-white disabled:opacity-50">{{ busy ? 'Connexion…' : 'Se connecter' }}</button>
    </form>

    <template v-else>
      <div class="mb-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <article class="rounded-2xl border border-amber-100 bg-white p-4 shadow-sm"><p class="text-sm text-stone-500">À traiter</p><p class="mt-2 text-3xl font-bold text-amber-700">{{ pendingOrders }}</p><p class="mt-1 text-xs text-stone-500">commandes en attente</p></article>
        <article class="rounded-2xl border border-blue-100 bg-white p-4 shadow-sm"><p class="text-sm text-stone-500">En préparation</p><p class="mt-2 text-3xl font-bold text-blue-700">{{ preparingOrders }}</p><p class="mt-1 text-xs text-stone-500">commandes à emballer</p></article>
        <article class="rounded-2xl border border-emerald-100 bg-white p-4 shadow-sm"><p class="text-sm text-stone-500">Livrées</p><p class="mt-2 text-3xl font-bold text-emerald-700">{{ deliveredOrders }}</p><p class="mt-1 text-xs text-stone-500">sur les 100 dernières</p></article>
        <article class="rounded-2xl border border-rose-100 bg-white p-4 shadow-sm"><p class="text-sm text-stone-500">Stocks faibles</p><p class="mt-2 text-3xl font-bold text-rose-800">{{ lowStockCount }}</p><p class="mt-1 text-xs text-stone-500">formats à 5 unités ou moins</p></article>
      </div>

      <div class="mb-5 flex flex-col gap-3 rounded-2xl border bg-white p-3 shadow-sm sm:flex-row sm:items-center">
        <div class="flex rounded-xl bg-stone-100 p-1">
          <button class="rounded-lg px-4 py-2 text-sm font-semibold" :class="activeTab === 'orders' ? 'bg-white text-rose-900 shadow-sm' : 'text-stone-600'" @click="activeTab = 'orders'; searchQuery = ''">Commandes <span class="ml-1 text-xs">{{ orders.length }}</span></button>
          <button class="rounded-lg px-4 py-2 text-sm font-semibold" :class="activeTab === 'products' ? 'bg-white text-rose-900 shadow-sm' : 'text-stone-600'" @click="activeTab = 'products'; searchQuery = ''">Produits <span class="ml-1 text-xs">{{ products.length }}</span></button>
        </div>
        <label class="relative flex-1">
          <span class="sr-only">Rechercher {{ activeTab === 'orders' ? 'une commande' : 'un produit' }}</span>
          <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-stone-400">⌕</span>
          <input v-model="searchQuery" class="w-full rounded-xl border border-stone-200 py-2.5 pl-9 pr-3 text-sm outline-none focus:border-rose-400 focus:ring-2 focus:ring-rose-100" :placeholder="activeTab === 'orders' ? 'Référence, client, téléphone…' : 'Nom du produit, catégorie…'" />
        </label>
        <select v-if="activeTab === 'orders'" v-model="statusFilter" class="rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm">
          <option value="all">Tous les états</option><option v-for="(label, value) in statuses" :key="value" :value="value">{{ label }}</option><option value="awaiting_payment">Paiement attendu</option>
        </select>
        <button class="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-50" :disabled="busy" @click="loadDashboard">{{ busy ? 'Actualisation…' : 'Actualiser' }}</button>
      </div>

      <div v-if="busy && !orders.length && !products.length" class="rounded-2xl border bg-white p-10 text-center text-stone-600">Chargement du tableau de bord…</div>
      <div v-else-if="activeTab === 'orders'" class="space-y-3">
        <p v-if="!filteredOrders.length" class="rounded-2xl border bg-white p-10 text-center text-stone-600">Aucune commande ne correspond à cette recherche.</p>
        <article v-for="order in filteredOrders" :key="order.id" class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
          <div class="flex flex-wrap items-center justify-between gap-3 bg-stone-50/80 px-4 py-4 sm:px-6">
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="font-bold">{{ order.order_number }}</h2>
              <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset" :class="statusStyle(order.order_status)">{{ statusLabel(order.order_status) }}</span>
            </div>
            <div class="text-right"><strong class="block text-lg">{{ money(order.total_amount) }} F</strong><span class="text-xs text-stone-500">{{ new Date(order.created_at).toLocaleString('fr-FR') }}</span></div>
          </div>
          <div class="grid gap-5 p-4 sm:grid-cols-2 sm:p-6">
            <div>
              <h3 class="mb-2 text-xs font-bold uppercase tracking-wider text-stone-500">Client et livraison</h3>
              <p class="font-medium">{{ order.customer_alias || 'Client' }} · <a class="text-rose-800 hover:underline" :href="`tel:${order.customer_phone}`">{{ order.customer_phone }}</a></p>
              <p class="mt-1 text-sm text-stone-600">{{ order.delivery_address }} <span v-if="order.zone">· {{ order.zone }}</span></p>
              <a v-if="order.delivery_latitude && order.delivery_longitude" class="mt-2 inline-flex text-sm font-medium text-rose-800 hover:underline" :href="`https://www.openstreetmap.org/?mlat=${order.delivery_latitude}&mlon=${order.delivery_longitude}#map=17/${order.delivery_latitude}/${order.delivery_longitude}`" target="_blank" rel="noopener noreferrer">⌖ Ouvrir la position sur la carte</a>
            </div>
            <div>
              <h3 class="mb-2 text-xs font-bold uppercase tracking-wider text-stone-500">Articles commandés</h3>
              <ul class="space-y-2 text-sm"><li v-for="(item, index) in order.items" :key="index" class="flex justify-between gap-3"><span>{{ item.product }} · {{ item.variant }} <span class="text-stone-500">× {{ item.quantity }}</span></span><span class="shrink-0 font-medium">{{ money(item.unit_price * item.quantity) }} F</span></li></ul>
              <p class="mt-3 border-t pt-2 text-xs text-stone-500">{{ order.payment_method }} · Paiement {{ order.payment_status }}</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center justify-between gap-3 border-t px-4 py-3 sm:px-6">
            <p class="text-xs text-stone-500">Articles {{ money(order.subtotal_amount) }} F <span class="px-1">+</span> livraison {{ money(order.delivery_fee) }} F</p>
            <label class="flex items-center gap-2 text-sm font-medium">Mettre à jour
              <select v-model="order.order_status" :disabled="['awaiting_payment', 'failed', 'cancelled', 'expired'].includes(order.order_status)" class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm disabled:bg-stone-100" @change="updateStatus(order)">
                <option v-for="(label, value) in statuses" :key="value" :value="value">{{ label }}</option>
              </select>
            </label>
          </div>
        </article>
      </div>

      <div v-else class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
        <p v-if="!filteredProducts.length" class="p-10 text-center text-stone-600">Aucun produit ne correspond à cette recherche.</p>
        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[720px] text-left text-sm">
            <thead class="bg-stone-50 text-xs uppercase tracking-wider text-stone-500"><tr><th class="px-5 py-4">Produit</th><th class="px-4 py-4">Format</th><th class="px-4 py-4">Prix</th><th class="px-4 py-4">Stock</th><th class="px-5 py-4"></th></tr></thead>
            <tbody><tr v-for="product in filteredProducts" :key="product.variant_id" class="border-t border-stone-100 hover:bg-stone-50/70">
              <td class="px-5 py-4"><strong>{{ product.name }}</strong><span class="mt-1 block text-xs text-stone-500">{{ product.category }}<span v-if="!product.is_active"> · Masqué du catalogue</span></span></td>
              <td class="px-4 py-4 text-stone-600">{{ product.variant_name || 'Format standard' }}</td>
              <td class="px-4 py-4"><div class="flex items-center gap-2"><input v-model.number="product.price" type="number" min="0" step="50" class="w-28 rounded-lg border border-stone-300 p-2" :aria-label="`Prix de ${product.name}`" /><span class="text-xs text-stone-500">FCFA</span></div></td>
              <td class="px-4 py-4"><div class="flex items-center gap-2"><input v-model.number="product.stock_quantity" type="number" min="0" step="1" class="w-20 rounded-lg border border-stone-300 p-2" :aria-label="`Stock de ${product.name}`" /><span class="rounded-full px-2 py-1 text-xs font-semibold" :class="product.stock_quantity <= 5 ? 'bg-rose-50 text-rose-800' : 'bg-emerald-50 text-emerald-800'">{{ product.stock_quantity <= 5 ? 'Faible' : 'Disponible' }}</span></div></td>
              <td class="px-5 py-4 text-right"><button class="rounded-lg bg-rose-900 px-3 py-2 font-semibold text-white hover:bg-rose-800" @click="updateVariant(product)">Enregistrer</button></td>
            </tr></tbody>
          </table>
        </div>
      </div>
    </template>
  </section>
</template>
