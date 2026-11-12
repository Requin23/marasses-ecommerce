<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = import.meta.server ? config.apiInternalBase : config.public.apiBase
const { data: products, error } = await useFetch<any[]>(`${apiBase}/products`, { key: 'catalog-products' })
const cart = useCartStore()
const selectedGroup = ref('all')
const searchQuery = ref('')

const groups = [
  {
    id: 'lui', title: 'Pour lui', subtitle: 'Protection et essentiels du quotidien.',
    slugs: ['preservatifs-classiques', 'preservatifs-ultra-fins', 'spray-retardateur-homme', 'oeuf-intime', 'koundjajo'],
  },
  {
    id: 'elle', title: 'Pour elle', subtitle: 'Soins et traditions de bien-être féminin.',
    slugs: ['gowe-encens-superieur', 'gel-intime-tonifiant', 'kayanmata-miel-herbes', 'perles-taille-baya', 'gel-mami-lot-3', 'vibro-rouge-a-levres', 'jouet-langue', 'jouet-intime-kiki', 'kit-secret-perles-cadenas'],
  },
  {
    id: 'deux', title: 'À partager à deux', subtitle: 'Jeux, moments complices et coffrets pour le couple.',
    slugs: [
      'gel-lubrifiant-naturel', 'gel-lubrifiant-aromatise', 'huile-massage-gourmande',
      'vibrant-kiss-menthe', 'mousse-massage-vibrant-kiss', 'smart-scalp-massager', 'appareil-massage',
      'manar-fraise', 'manar-menthe', 'manar-chocolat', 'parfum-intimite', 'parfum-argent-lot-3', 'kit-torture',
      'jeu-cartes-defis-coquin', 'des-coquins-phosphorescents',
      'pack-decouverte-securite', 'pack-secrets-seduction', 'pack-soiree-couple', 'pack-soiree-pimentee',
    ],
  },
]

const visibleGroups = computed(() => groups
  .filter(group => selectedGroup.value === 'all' || selectedGroup.value === group.id)
  .map(group => ({
    ...group,
    products: (products.value || []).filter((product) => {
      if (!group.slugs.includes(product.slug)) return false
      const query = searchQuery.value.trim().toLocaleLowerCase('fr')
      return !query || [product.name, product.description, product.category]
        .some(value => String(value || '').toLocaleLowerCase('fr').includes(query))
    }),
  }))
  .filter(group => group.products.length))
const visibleProductCount = computed(() => visibleGroups.value.reduce((sum, group) => sum + group.products.length, 0))
</script>

<template>
  <section class="mb-8 overflow-hidden rounded-3xl bg-rose-900 px-6 py-8 text-white shadow-sm md:px-10 md:py-10">
    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-rose-100">MARASSES · BURKINA FASO</p>
    <h1 class="mt-3 max-w-2xl text-3xl font-bold leading-tight md:text-5xl">Le bien-être intime, en toute confiance.</h1>
    <p class="mt-4 max-w-2xl leading-7 text-rose-100">Choisissez vos essentiels facilement. Votre commande est livrée dans un emballage neutre et scellé.</p>
    <a href="#catalogue" class="mt-6 inline-flex min-h-11 items-center justify-center rounded-xl bg-white px-5 py-3 text-sm font-semibold text-rose-900 hover:bg-rose-50">Découvrir les produits</a>
    <div class="mt-7 flex flex-wrap gap-x-5 gap-y-2 border-t border-white/20 pt-4 text-sm text-rose-100">
      <span>✓ Emballage discret</span>
      <span>✓ Paiement à la livraison</span>
      <span>✓ Aide disponible</span>
    </div>
  </section>
  <div id="catalogue" class="mb-5 scroll-mt-5">
    <h2 class="text-2xl font-bold">Nos essentiels</h2>
    <p class="mt-1 text-sm text-stone-600">Parcourez les produits par besoin ou recherchez un article précis.</p>
  </div>
  <p v-if="error" class="rounded-xl bg-amber-50 p-4">Catalogue indisponible pour le moment. Réessayez dans quelques instants.</p>
  <template v-else-if="products?.length">
    <label class="mb-4 block">
      <span class="sr-only">Rechercher un produit</span>
      <span class="relative block">
        <span aria-hidden="true" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-lg text-stone-500">⌕</span>
        <input v-model="searchQuery" type="search" autocomplete="off" class="min-h-12 w-full rounded-xl border border-stone-300 bg-white py-3 pl-10 pr-4 text-sm shadow-sm focus:border-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-200" placeholder="Rechercher un produit…">
      </span>
    </label>
    <nav class="mb-5 flex gap-2 overflow-x-auto pb-2" aria-label="Filtrer les produits par collection">
      <button
        type="button"
        class="shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition"
        :class="selectedGroup === 'all' ? 'border-rose-900 bg-rose-900 text-white' : 'border-stone-300 bg-white hover:border-rose-500'"
        :aria-pressed="selectedGroup === 'all'"
        @click="selectedGroup = 'all'"
      >Tout voir</button>
      <button
        v-for="group in groups"
        :key="group.id"
        type="button"
        class="shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition"
        :class="selectedGroup === group.id ? 'border-rose-900 bg-rose-900 text-white' : 'border-stone-300 bg-white hover:border-rose-500'"
        :aria-pressed="selectedGroup === group.id"
        @click="selectedGroup = group.id"
      >{{ group.title }}</button>
    </nav>

    <p class="mb-5 text-sm text-stone-500" aria-live="polite">{{ visibleProductCount }} produit{{ visibleProductCount > 1 ? 's' : '' }} affiché{{ visibleProductCount > 1 ? 's' : '' }}</p>

    <section v-for="group in visibleGroups" :key="group.id" class="mb-10 scroll-mt-6">
      <header class="mb-4 border-b border-stone-200 pb-3">
        <h3 class="text-xl font-bold sm:text-2xl">{{ group.title }}</h3>
        <p class="mt-1 text-sm text-stone-600">{{ group.subtitle }}</p>
      </header>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <ProductCard v-for="product in group.products" :key="product.id" :product="product" />
      </div>
    </section>
    <div v-if="!visibleProductCount" class="mb-8 rounded-2xl border border-stone-200 bg-white p-6 text-center">
      <h3 class="font-semibold">Aucun produit trouvé</h3>
      <p class="mt-1 text-sm text-stone-600">Essaie un autre mot ou affiche toute la collection.</p>
      <button type="button" class="mt-4 rounded-xl border border-stone-300 px-4 py-2 text-sm font-semibold hover:bg-stone-50" @click="searchQuery = ''; selectedGroup = 'all'">Effacer les filtres</button>
    </div>
  </template>
  <p v-else class="rounded-xl bg-white p-4 text-stone-600">Le catalogue sera bientôt disponible.</p>

  <section aria-labelledby="emergency-contraception-title" class="mb-10 rounded-3xl border border-rose-200 bg-rose-50 p-6 dark:border-slate-700 dark:bg-slate-900 md:p-8">
    <p class="text-xs font-semibold uppercase tracking-wider text-rose-800 dark:text-rose-300">Rubrique en préparation</p>
    <h2 id="emergency-contraception-title" class="mt-2 text-xl font-bold text-stone-900 dark:text-slate-100 sm:text-2xl">Contraception d’urgence</h2>
    <p class="mt-2 max-w-2xl text-sm leading-6 text-stone-700 dark:text-slate-300">
      Les produits, prix et disponibilités seront ajoutés après confirmation des informations auprès du fournisseur.
    </p>
    <p class="mt-3 max-w-2xl text-xs leading-5 text-stone-600 dark:text-slate-400">
      Pour un besoin immédiat, adressez-vous directement à une pharmacie ou à un professionnel de santé.
    </p>
  </section>
</template>
