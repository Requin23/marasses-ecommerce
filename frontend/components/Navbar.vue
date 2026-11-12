<script setup lang="ts">
const router = useRouter()
const route = useRoute()
const isMenuOpen = ref(false)

function activateDiscreetMode() {
  isMenuOpen.value = false
  void router.replace('/discret')
}

watch(() => route.fullPath, () => { isMenuOpen.value = false })
</script>

<template>
  <header class="border-b bg-white">
    <nav class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:py-4" aria-label="Navigation principale">
      <NuxtLink to="/" class="text-2xl font-bold tracking-tight text-rose-800">Marasses</NuxtLink>
      <div class="hidden items-center gap-3 sm:flex sm:gap-4">
        <NuxtLink to="/assistance" class="text-sm text-rose-800 hover:underline">Aide / Réclamation</NuxtLink>
        <button class="rounded-full border border-stone-300 px-4 py-2 text-sm hover:bg-stone-100" @click="activateDiscreetMode">
          Mode discret
        </button>
      </div>
      <button
        type="button"
        class="rounded-xl border border-stone-300 px-3 py-2 text-sm font-medium hover:bg-stone-100 sm:hidden"
        :aria-expanded="isMenuOpen"
        aria-controls="mobile-navigation"
        @click="isMenuOpen = !isMenuOpen"
      >{{ isMenuOpen ? 'Fermer' : 'Menu' }}</button>
    </nav>
    <div v-if="isMenuOpen" id="mobile-navigation" class="space-y-1 border-t px-4 py-3 sm:hidden">
      <NuxtLink to="/assistance" class="block rounded-lg px-3 py-3 text-sm font-medium text-rose-800 hover:bg-stone-100">Aide et réclamations</NuxtLink>
      <button type="button" class="w-full rounded-lg px-3 py-3 text-left text-sm font-medium hover:bg-stone-100" @click="activateDiscreetMode">Activer le mode discret</button>
    </div>
  </header>
</template>
