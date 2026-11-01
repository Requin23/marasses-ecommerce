<script setup lang="ts">
const discreet=ref(false); const priorTitle=ref(''); const router=useRouter();
function toggleDiscreet(){discreet.value=!discreet.value;if(discreet.value){priorTitle.value=document.title;document.title='Météo locale';router.push('/discret')}else{document.title=priorTitle.value||'Marasses | Bien-être intime';router.push('/')}}
</script>
<template><header class="border-b bg-white"><nav class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4"><NuxtLink to="/" class="text-2xl font-bold tracking-tight text-rose-800">Marasses</NuxtLink><button class="rounded-full border border-stone-300 px-4 py-2 text-sm hover:bg-stone-100" @click="toggleDiscreet">{{ discreet?'Revenir':'Mode discret' }}</button></nav></header></template>
