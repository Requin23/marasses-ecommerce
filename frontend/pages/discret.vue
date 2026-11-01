<script setup lang="ts">
const router = useRouter()
const today = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long', day: 'numeric', month: 'long',
}).format(new Date())

function leaveDiscreetMode() {
  void router.push('/')
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') leaveDiscreetMode()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <section class="min-h-screen bg-slate-100 px-4 py-8 text-slate-800 sm:py-14">
    <div class="mx-auto max-w-2xl">
      <header class="flex items-center justify-between border-b border-slate-200 pb-5">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Météo locale</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight">Prévisions</h1>
        </div>
        <span class="rounded-full bg-white px-3 py-1.5 text-xs text-slate-500 shadow-sm">{{ today }}</span>
      </header>

      <main class="mt-8 space-y-5">
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm text-slate-500">Votre région</p>
              <h2 class="mt-1 text-xl font-semibold">Ouagadougou</h2>
            </div>
            <span aria-hidden="true" class="text-4xl">☁</span>
          </div>
          <p class="mt-8 text-sm leading-6 text-slate-600">Consultez les prévisions météorologiques de votre région et préparez vos déplacements.</p>
          <div class="mt-6 grid grid-cols-3 gap-3 border-t border-slate-100 pt-5 text-center text-xs text-slate-500">
            <div><span class="block text-lg">☀</span>Matin</div>
            <div><span class="block text-lg">☁</span>Après-midi</div>
            <div><span class="block text-lg">☾</span>Soir</div>
          </div>
        </article>

        <button class="rounded-xl px-3 py-2 text-sm text-slate-500 hover:bg-white hover:text-slate-800" @click="leaveDiscreetMode">Retour</button>
      </main>
    </div>
  </section>
</template>
