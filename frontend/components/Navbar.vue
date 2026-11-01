<script setup lang="ts">
const router = useRouter()
function activateDiscreetMode() {
  void router.replace('/discret')
}
</script>

<template>
  <header class="border-b bg-white">
    <nav class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
      <NuxtLink to="/" class="text-2xl font-bold tracking-tight text-rose-800">Marasses</NuxtLink>
      <div class="flex items-center gap-2 sm:gap-4">
        <NuxtLink to="/assistance" class="text-sm text-rose-800 hover:underline">Aide / Réclamation</NuxtLink>
        <button class="rounded-full border border-stone-300 px-4 py-2 text-sm hover:bg-stone-100" @click="activateDiscreetMode">
          Mode discret
        </button>
      </div>
    </nav>
  </header>
</template>
