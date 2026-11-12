<script setup lang="ts">
const props = defineProps<{ product: any }>()
const cart = useCartStore()
const variant = ref(props.product.variants?.find((item: any) => item.stock > 0) || props.product.variants?.[0])
const inCart = computed(() => cart.lines.find(line => line.variant.id === variant.value?.id)?.quantity || 0)
const canAdd = computed(() => !!variant.value && variant.value.stock > inCart.value)

function addToCart() {
  if (!variant.value || !canAdd.value) return
  cart.add(props.product.name, variant.value)
}
</script>

<template>
  <article class="flex h-full flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
    <ProductArtwork :slug="product.slug" :name="product.name" />
    <div class="flex flex-1 flex-col p-5">
      <p class="text-xs uppercase tracking-wider text-rose-700">{{ product.category || 'Bien-être' }}</p>
      <h2 class="mt-2 text-lg font-semibold leading-snug">{{ product.name }}</h2>
      <p class="mt-2 flex-1 text-sm leading-6 text-stone-600">{{ product.description }}</p>
      <label class="mt-4 block text-xs font-medium text-stone-600" :for="`variant-${product.id}`">Choisir le format</label>
      <div class="mt-1 flex flex-wrap items-center justify-between gap-3">
      <select :id="`variant-${product.id}`" v-model="variant" class="min-w-0 flex-1 rounded-lg border p-2.5 text-sm">
        <option v-for="item in product.variants" :key="item.id" :value="item" :disabled="item.stock < 1">
          {{ item.name || 'Format standard' }} · {{ new Intl.NumberFormat('fr-FR').format(item.price) }} FCFA{{ item.stock < 1 ? ' · Épuisé' : '' }}
        </option>
      </select>
      <button :disabled="!canAdd" class="shrink-0 rounded-xl bg-rose-800 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-900 disabled:cursor-not-allowed disabled:opacity-50" @click="addToCart">
        {{ canAdd ? (inCart ? 'Ajouter encore' : 'Ajouter au panier') : (variant?.stock ? 'Limite atteinte' : 'Indisponible') }}
      </button>
      </div>
      <p v-if="inCart" aria-live="polite" class="mt-2 text-xs font-medium text-emerald-700">{{ inCart }} dans votre panier</p>
    </div>
  </article>
</template>
