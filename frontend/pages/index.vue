<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = import.meta.server ? config.apiInternalBase : config.public.apiBase
const { data: products, error } = await useFetch<any[]>(`${apiBase}/products`, { key: 'catalog-products' })
const cart = useCartStore()
const selectedGroup = ref('all')

const groups = [
  {
    id: 'lui', title: 'Pour lui', subtitle: 'Protection et essentiels du quotidien.',
    slugs: ['preservatifs-classiques', 'preservatifs-ultra-fins'],
  },
  {
    id: 'elle', title: 'Pour elle', subtitle: 'Soins et traditions de bien-être féminin.',
    slugs: ['gowe-encens-superieur', 'gel-intime-tonifiant', 'kayanmata-miel-herbes', 'perles-taille-baya'],
  },
  {
    id: 'deux', title: 'À partager à deux', subtitle: 'Jeux, moments complices et coffrets pour le couple.',
    slugs: [
      'gel-lubrifiant-naturel', 'gel-lubrifiant-aromatise', 'huile-massage-gourmande',
      'jeu-cartes-defis-coquin', 'des-coquins-phosphorescents',
      'pack-decouverte-securite', 'pack-secrets-seduction', 'pack-soiree-couple', 'pack-soiree-pimentee',
    ],
  },
]

const visibleGroups = computed(() => groups
  .filter(group => selectedGroup.value === 'all' || selectedGroup.value === group.id)
  .map(group => ({ ...group, products: (products.value || []).filter(product => group.slugs.includes(product.slug)) }))
  .filter(group => group.products.length))
</script>

<template>
  <section class="mb-8 rounded-3xl bg-rose-900 px-6 py-10 text-white md:px-10">
    <p class="text-sm text-rose-100">MARASSES · BURKINA FASO</p>
    <h1 class="mt-3 max-w-xl text-3xl font-bold md:text-5xl">Prenez soin de vous, en toute confiance.</h1>
    <p class="mt-4 max-w-xl text-rose-100">Des essentiels de santé intime livrés avec discrétion.</p>
  </section>
  <div class="mb-5 flex items-center justify-between gap-3">
    <h2 class="text-2xl font-bold">Nos essentiels</h2>
    <NuxtLink to="/checkout" class="rounded-xl bg-stone-900 px-4 py-2 text-white">Panier ({{ cart.count }})</NuxtLink>
  </div>
  <p v-if="error" class="rounded-xl bg-amber-50 p-4">Catalogue indisponible pour le moment. Réessayez dans quelques instants.</p>
  <template v-else-if="products?.length">
    <nav class="mb-8 flex gap-2 overflow-x-auto pb-2" aria-label="Filtrer les produits par collection">
      <button
        class="shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition"
        :class="selectedGroup === 'all' ? 'border-rose-900 bg-rose-900 text-white' : 'border-stone-300 bg-white hover:border-rose-500'"
        :aria-pressed="selectedGroup === 'all'"
        @click="selectedGroup = 'all'"
      >Tout voir</button>
      <button
        v-for="group in groups"
        :key="group.id"
        class="shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition"
        :class="selectedGroup === group.id ? 'border-rose-900 bg-rose-900 text-white' : 'border-stone-300 bg-white hover:border-rose-500'"
        :aria-pressed="selectedGroup === group.id"
        @click="selectedGroup = group.id"
      >{{ group.title }}</button>
    </nav>

    <section v-for="group in visibleGroups" :key="group.id" class="mb-10 scroll-mt-6">
      <header class="mb-4 border-b border-stone-200 pb-3">
        <h3 class="text-xl font-bold sm:text-2xl">{{ group.title }}</h3>
        <p class="mt-1 text-sm text-stone-600">{{ group.subtitle }}</p>
      </header>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <ProductCard v-for="product in group.products" :key="product.id" :product="product" />
      </div>
    </section>
  </template>
  <p v-else class="rounded-xl bg-white p-4 text-stone-600">Le catalogue sera bientôt disponible.</p>
</template>
