<script setup lang="ts">
const route = useRoute()
const isDiscreet = computed(() => route.path === '/discret')
useHead(() => ({ title: isDiscreet.value ? 'Météo locale' : 'Marasses | Bien-être intime' }))
</script>

<template>
  <div>
    <a v-if="!isDiscreet" href="#main-content" class="sr-only z-50 rounded-lg bg-white px-4 py-3 text-rose-900 focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:shadow-lg">Aller au contenu</a>
    <Navbar v-if="!isDiscreet" />
    <main id="main-content" :class="isDiscreet ? 'min-h-screen px-4' : 'mx-auto min-h-screen max-w-6xl px-4 pt-6 pb-28 sm:pt-8'">
      <NuxtPage />
    </main>
    <CartBar v-if="!isDiscreet" />
    <footer v-if="!isDiscreet" class="border-t bg-white px-4 py-6 text-sm text-stone-600">
      <div class="mx-auto flex max-w-6xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p>Marasses · Bien-être intime, en toute discrétion.</p>
        <nav aria-label="Liens utiles" class="flex flex-wrap gap-x-5 gap-y-2">
          <NuxtLink to="/assistance" class="font-medium text-rose-800 underline underline-offset-2">Aide et réclamations</NuxtLink>
          <NuxtLink to="/discret" class="font-medium text-rose-800 underline underline-offset-2">Mode discret</NuxtLink>
        </nav>
      </div>
    </footer>
  </div>
</template>
