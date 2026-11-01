import { defineStore } from 'pinia'

type Variant = { id: string; name: string | null; price: number; stock: number }
type CartLine = { variant: Variant; productName: string; quantity: number }

export const useCartStore = defineStore('cart', {
  state: () => ({ lines: [] as CartLine[] }),
  getters: {
    subtotal: state => state.lines.reduce((sum, line) => sum + line.variant.price * line.quantity, 0),
    count: state => state.lines.reduce((sum, line) => sum + line.quantity, 0),
  },
  actions: {
    add(productName: string, variant: Variant) {
      if (variant.stock < 1) return
      const line = this.lines.find(item => item.variant.id === variant.id)
      if (line) {
        if (line.quantity < variant.stock) line.quantity += 1
        return
      }
      this.lines.push({ productName, variant, quantity: 1 })
    },
    increment(variantId: string) {
      const line = this.lines.find(item => item.variant.id === variantId)
      if (line && line.quantity < line.variant.stock) line.quantity += 1
    },
    decrement(variantId: string) {
      const line = this.lines.find(item => item.variant.id === variantId)
      if (line && line.quantity > 1) line.quantity -= 1
    },
    remove(variantId: string) {
      this.lines = this.lines.filter(item => item.variant.id !== variantId)
    },
    clear() {
      this.lines = []
    },
  },
})
