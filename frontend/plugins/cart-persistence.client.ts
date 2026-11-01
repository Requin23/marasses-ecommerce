import { useCartStore } from '~/stores/cartStore'
export default defineNuxtPlugin(() => {
  const cart=useCartStore(); const key='marasses-cart-v1'
  try { const saved=localStorage.getItem(key); if(saved) cart.$patch(JSON.parse(saved)) } catch { localStorage.removeItem(key) }
  cart.$subscribe((_mutation,state)=>{ localStorage.setItem(key,JSON.stringify({lines:state.lines})) },{detached:true})
})
