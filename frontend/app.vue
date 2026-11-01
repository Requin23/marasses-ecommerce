<script setup lang="ts">
const route = useRoute()
const isDiscreet = computed(() => route.path === '/discret')
useHead(() => ({ title: isDiscreet.value ? 'Météo locale' : 'Marasses | Bien-être intime' }))
</script>

<template>
  <div>
    <Navbar v-if="!isDiscreet" />
    <main :class="isDiscreet ? 'min-h-screen px-4' : 'mx-auto min-h-screen max-w-6xl px-4 py-8'">
      <NuxtPage />
    </main>
    <footer v-if="!isDiscreet" class="border-t bg-white px-4 py-6 text-center text-sm text-stone-500">
      Bien-être intime, en toute discrétion.
    </footer>
  </div>
</template>
