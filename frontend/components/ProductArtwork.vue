<script setup lang="ts">
const props = defineProps<{ slug: string; name: string }>()

const palettes: Record<string, { bg: string; ink: string; accent: string }> = {
  protection: { bg: '#f4e9e7', ink: '#8f173d', accent: '#d9a8a0' },
  soin: { bg: '#e8eee6', ink: '#45634e', accent: '#b4c7a9' },
  nature: { bg: '#f3ecdf', ink: '#876333', accent: '#d9bf8d' },
  jeu: { bg: '#ece8f3', ink: '#574575', accent: '#b6a7d2' },
  pack: { bg: '#f1e6e8', ink: '#8f173d', accent: '#d5a1ad' },
}
const themes: Record<string, string> = {
  'preservatifs-classiques': 'protection', 'preservatifs-ultra-fins': 'protection',
  'gel-lubrifiant-naturel': 'soin', 'gel-lubrifiant-aromatise': 'soin',
  'gowe-encens-superieur': 'nature', 'gel-intime-tonifiant': 'soin',
  'kayanmata-miel-herbes': 'nature', 'huile-massage-gourmande': 'soin',
  'jeu-cartes-defis-coquin': 'jeu', 'des-coquins-phosphorescents': 'jeu',
  'perles-taille-baya': 'nature', 'pack-decouverte-securite': 'pack',
  'pack-secrets-seduction': 'pack', 'pack-soiree-couple': 'pack', 'pack-soiree-pimentee': 'pack',
}
const theme = computed(() => themes[props.slug] || 'soin')
const colors = computed(() => palettes[theme.value]!)
const isPack = computed(() => theme.value === 'pack')
const isJar = computed(() => ['gowe-encens-superieur', 'kayanmata-miel-herbes'].includes(props.slug))
const isCards = computed(() => props.slug === 'jeu-cartes-defis-coquin')
const isDice = computed(() => props.slug === 'des-coquins-phosphorescents')
const isBeads = computed(() => props.slug === 'perles-taille-baya')
const isOil = computed(() => props.slug === 'huile-massage-gourmande')
</script>

<template>
  <div class="relative flex h-48 items-center justify-center overflow-hidden rounded-xl" :style="{ backgroundColor: colors.bg }" role="img" :aria-label="`Illustration du produit ${name}`">
    <svg viewBox="0 0 320 190" class="h-full w-full" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <circle cx="160" cy="95" r="70" :fill="colors.accent" opacity=".28" />
      <circle cx="75" cy="40" r="18" :fill="colors.accent" opacity=".35" />
      <circle cx="256" cy="145" r="26" :fill="colors.accent" opacity=".22" />
      <g v-if="isBeads" fill="none" :stroke="colors.ink" stroke-width="3">
        <ellipse cx="160" cy="94" rx="53" ry="35" />
        <circle v-for="n in 15" :key="n" :cx="160 + 53 * Math.cos((n - 1) * 2 * Math.PI / 15)" :cy="94 + 35 * Math.sin((n - 1) * 2 * Math.PI / 15)" r="7" :fill="n % 3 ? colors.accent : colors.ink" stroke="white" stroke-width="2" />
      </g>
      <g v-else-if="isCards" transform="rotate(-9 160 95)">
        <rect x="119" y="46" width="72" height="100" rx="9" fill="white" :stroke="colors.ink" stroke-width="3" />
        <rect x="134" y="38" width="72" height="100" rx="9" :fill="colors.accent" :stroke="colors.ink" stroke-width="3" />
        <path d="M153 70c8-12 26-3 16 9l-10 12-10-12c-10-12 8-21 16-9" fill="white" />
        <path d="M151 111h38" :stroke="colors.ink" stroke-width="3" stroke-linecap="round" />
      </g>
      <g v-else-if="isDice">
        <rect x="112" y="64" width="52" height="52" rx="12" :fill="colors.ink" />
        <rect x="160" y="84" width="52" height="52" rx="12" :fill="colors.accent" :stroke="colors.ink" stroke-width="3" />
        <g fill="white"><circle cx="128" cy="80" r="4"/><circle cx="148" cy="100" r="4"/><circle cx="128" cy="100" r="4"/><circle cx="176" cy="100" r="4"/><circle cx="196" cy="120" r="4"/><circle cx="196" cy="100" r="4"/></g>
      </g>
      <g v-else-if="isPack">
        <rect x="111" y="54" width="98" height="92" rx="12" fill="white" :stroke="colors.ink" stroke-width="3" />
        <path d="M111 78h98" :stroke="colors.ink" stroke-width="3" />
        <path d="M145 54v-9h30v9" fill="none" :stroke="colors.ink" stroke-width="3" />
        <rect x="132" y="92" width="21" height="37" rx="5" :fill="colors.accent" />
        <rect x="164" y="99" width="26" height="30" rx="5" :fill="colors.ink" opacity=".85" />
        <path d="M142 106h2m30 5h9" stroke="white" stroke-width="3" stroke-linecap="round" />
      </g>
      <g v-else-if="isJar">
        <rect x="126" y="55" width="68" height="15" rx="5" :fill="colors.ink" />
        <rect x="119" y="68" width="82" height="75" rx="14" fill="white" :stroke="colors.ink" stroke-width="3" />
        <rect x="120" y="91" width="80" height="30" :fill="colors.accent" />
        <path d="M139 106h42" :stroke="colors.ink" stroke-width="3" stroke-linecap="round" />
      </g>
      <g v-else-if="isOil">
        <path d="M143 54h34v14h-34z" :fill="colors.ink" />
        <path d="M148 68h24v12l17 15v41a9 9 0 0 1-9 9h-40a9 9 0 0 1-9-9V95l17-15z" fill="white" :stroke="colors.ink" stroke-width="3" />
        <path d="M134 105h52v28a9 9 0 0 1-9 9h-34a9 9 0 0 1-9-9z" :fill="colors.accent" />
        <path d="M152 113c8 4 8 13 0 17 13 0 18-12 10-19-2 5-6 5-10 2" fill="white" />
      </g>
      <g v-else-if="theme === 'protection'">
        <rect x="116" y="54" width="88" height="91" rx="12" fill="white" :stroke="colors.ink" stroke-width="3" />
        <path d="M116 78h88" :stroke="colors.ink" stroke-width="3" />
        <circle cx="160" cy="108" r="18" :fill="colors.accent" />
        <path d="M160 97v22m-8-11h16" :stroke="colors.ink" stroke-width="3" stroke-linecap="round" />
      </g>
      <g v-else>
        <path d="M142 51h36v12h-36z" :fill="colors.ink" />
        <rect x="130" y="63" width="60" height="87" rx="13" fill="white" :stroke="colors.ink" stroke-width="3" />
        <rect x="132" y="98" width="56" height="31" :fill="colors.accent" />
        <path d="M148 111h24" :stroke="colors.ink" stroke-width="3" stroke-linecap="round" />
      </g>
      <path d="M145 165h30" :stroke="colors.ink" stroke-width="3" stroke-linecap="round" opacity=".4" />
    </svg>
    <span class="absolute bottom-3 left-3 rounded-full bg-white/80 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-stone-600">Visuel illustratif</span>
  </div>
</template>
