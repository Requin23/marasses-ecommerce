<script setup lang="ts">
const cart = useCartStore()
const route = useRoute()
const isOpen = ref(false)

const visible = computed(() => cart.count > 0 && !['/discret', '/checkout', '/admin'].includes(route.path))
const money = (amount: number) => new Intl.NumberFormat('fr-FR').format(amount)

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') isOpen.value = false
}

watch(isOpen, (open) => {
  if (import.meta.client) {
    document.body.style.overflow = open ? 'hidden' : ''
    if (open) window.addEventListener('keydown', onKeydown)
    else window.removeEventListener('keydown', onKeydown)
  }
})

onBeforeUnmount(() => {
  if (import.meta.client) {
    document.body.style.overflow = ''
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-x-0 bottom-0 z-40 border-t border-stone-200 bg-white/95 p-3 shadow-[0_-8px_30px_rgba(28,25,23,0.12)] backdrop-blur dark:border-slate-700 dark:bg-slate-900/95 sm:px-6 sm:py-4">
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-3">
        <button class="min-w-0 text-left" :aria-expanded="isOpen" @click="isOpen = true">
          <span class="block truncate text-sm font-semibold sm:text-base">Voir mon panier · {{ cart.count }} article{{ cart.count > 1 ? 's' : '' }}</span>
          <span class="mt-0.5 block text-xs text-stone-600">Sous-total : {{ money(cart.subtotal) }} FCFA</span>
        </button>
        <button class="shrink-0 rounded-xl bg-rose-900 px-4 py-3 text-sm font-semibold text-white hover:bg-rose-800 sm:px-6" @click="navigateTo('/checkout')">
          Commander / payer
        </button>
      </div>
    </div>

    <div v-if="visible && isOpen" class="fixed inset-0 z-50 flex items-end bg-black/45 sm:items-center sm:justify-center sm:p-4" @click.self="isOpen = false">
      <section role="dialog" aria-modal="true" aria-labelledby="cart-title" class="max-h-[85vh] w-full overflow-y-auto rounded-t-3xl bg-white p-5 shadow-2xl dark:bg-slate-900 sm:max-w-xl sm:rounded-3xl sm:p-6">
        <header class="flex items-start justify-between gap-4 border-b border-stone-200 pb-4 dark:border-slate-700">
          <div>
            <h2 id="cart-title" class="text-xl font-bold">Mon panier</h2>
            <p class="mt-1 text-sm text-stone-600">{{ cart.count }} article{{ cart.count > 1 ? 's' : '' }} sélectionné{{ cart.count > 1 ? 's' : '' }}</p>
          </div>
          <button class="rounded-full border border-stone-300 px-3 py-1.5 text-sm hover:bg-stone-100" aria-label="Fermer le panier" @click="isOpen = false">Fermer</button>
        </header>

        <ul class="divide-y divide-stone-200 dark:divide-slate-700">
          <li v-for="line in cart.lines" :key="line.variant.id" class="flex items-start justify-between gap-3 py-4">
            <div class="min-w-0 flex-1">
              <p class="font-semibold">{{ line.productName }}</p>
              <p v-if="line.variant.name" class="mt-0.5 text-xs text-stone-500">{{ line.variant.name }}</p>
              <div class="mt-2 flex flex-wrap items-center gap-3">
                <div class="inline-flex items-center rounded-lg border border-stone-300">
                  <button type="button" class="px-3 py-1.5 disabled:opacity-40" :disabled="line.quantity <= 1" :aria-label="`Diminuer ${line.productName}`" @click="cart.decrement(line.variant.id)">−</button>
                  <span class="min-w-8 text-center text-sm">{{ line.quantity }}</span>
                  <button type="button" class="px-3 py-1.5 disabled:opacity-40" :disabled="line.quantity >= line.variant.stock" :aria-label="`Augmenter ${line.productName}`" @click="cart.increment(line.variant.id)">+</button>
                </div>
                <button type="button" class="text-sm text-rose-800 underline" :aria-label="`Retirer ${line.productName} du panier`" @click="cart.remove(line.variant.id)">Retirer</button>
              </div>
            </div>
            <span class="shrink-0 text-right text-sm font-semibold">{{ money(line.variant.price * line.quantity) }} F</span>
          </li>
        </ul>

        <div v-if="cart.lines.length" class="border-t border-stone-200 pt-4 dark:border-slate-700">
          <p class="flex justify-between text-base font-bold"><span>Sous-total</span><span>{{ money(cart.subtotal) }} FCFA</span></p>
          <p class="mt-1 text-xs text-stone-500">Les frais de livraison seront calculés à l’étape suivante.</p>
          <button class="mt-4 w-full rounded-xl bg-rose-900 px-5 py-3 font-semibold text-white hover:bg-rose-800" @click="isOpen = false; navigateTo('/checkout')">Commander / payer</button>
        </div>
        <div v-else class="pt-5 text-center">
          <p class="text-sm text-stone-600">Ton panier est vide.</p>
          <button class="mt-3 text-sm font-semibold text-rose-800 underline" @click="isOpen = false">Continuer mes achats</button>
        </div>
      </section>
    </div>
  </Teleport>
</template>
