<script setup lang="ts">
const props = defineProps<{ product: any }>()
const cart = useCartStore()
const variant = ref(props.product.variants?.[0])
const inCart = computed(() => cart.lines.find(line => line.variant.id === variant.value?.id)?.quantity || 0)
const canAdd = computed(() => !!variant.value && variant.value.stock > inCart.value)
</script>

<template>
  <article class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
    <p class="text-xs uppercase tracking-wider text-rose-700">{{ product.category || 'Bien-être' }}</p>
    <h2 class="mt-2 text-lg font-semibold">{{ product.name }}</h2>
    <p class="mt-2 min-h-12 text-sm text-stone-600">{{ product.description }}</p>
    <div class="mt-4 flex items-center justify-between gap-3">
      <select v-model="variant" class="max-w-40 rounded-lg border p-2 text-sm" :aria-label="`Format de ${product.name}`">
        <option v-for="item in product.variants" :key="item.id" :value="item" :disabled="item.stock < 1">
          {{ item.name || 'Format standard' }} · {{ item.price }} FCFA
        </option>
      </select>
      <button :disabled="!canAdd" class="rounded-xl bg-rose-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-40" @click="cart.add(product.name, variant)">
        {{ canAdd ? 'Ajouter' : 'Stock épuisé' }}
      </button>
    </div>
  </article>
</template>
