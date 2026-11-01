<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = import.meta.server ? config.apiInternalBase : config.public.apiBase
const { data: products, error } = await useFetch<any[]>(`${apiBase}/products`, { key: 'catalog-products' })
const cart = useCartStore()
</script>

<template>
  <section class="mb-8 rounded-3xl bg-rose-900 px-6 py-10 text-white md:px-10">
    <p class="text-sm text-rose-100">MARASSES · BURKINA FASO</p>
    <h1 class="mt-3 max-w-xl text-3xl font-bold md:text-5xl">Prenez soin de vous, en toute confiance.</h1>
    <p class="mt-4 max-w-xl text-rose-100">Des essentiels de santé intime livrés avec discrétion.</p>
  </section>
  <div class="mb-5 flex items-center justify-between">
    <h2 class="text-2xl font-bold">Nos essentiels</h2>
    <NuxtLink to="/checkout" class="rounded-xl bg-stone-900 px-4 py-2 text-white">Panier ({{ cart.count }})</NuxtLink>
  </div>
  <p v-if="error" class="rounded-xl bg-amber-50 p-4">Catalogue indisponible pour le moment. Réessayez dans quelques instants.</p>
  <div v-else-if="products?.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
    <ProductCard v-for="product in products" :key="product.id" :product="product" />
  </div>
  <p v-else class="rounded-xl bg-white p-4 text-stone-600">Le catalogue sera bientôt disponible.</p>
</template>
