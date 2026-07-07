import { useState } from 'react'
import { Plus, Minus, ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn, formatCurrency } from '@/lib/utils'
import type { Base, MenuItem, Topping } from '@/types'
import type { CartItem } from '../types'

interface PizzaCardProps {
  item: MenuItem
  bases: Base[]
  toppings: Topping[]
  onAdd: (cartItem: CartItem) => void
}

function PizzaCard({ item, bases, toppings, onAdd }: PizzaCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [baseCode, setBaseCode] = useState(bases[0]?.code ?? '')
  const [toppingCodes, setToppingCodes] = useState<string[]>([])
  const [qty, setQty] = useState(1)

  const toggleTopping = (code: string) =>
    setToppingCodes((prev) => (prev.includes(code) ? prev.filter((x) => x !== code) : [...prev, code]))

  const selectedBase = bases.find((b) => b.code === baseCode)
  const selectedToppings = toppings.filter((t) => toppingCodes.includes(t.code))
  const unitPrice = item.price + (selectedBase?.price ?? 0) + selectedToppings.reduce((sum, t) => sum + t.price, 0)

  const handleAdd = () => {
    if (!selectedBase) return
    onAdd({
      menuItemId: item.id,
      name: item.name,
      category: item.category,
      baseSelected: selectedBase.name,
      toppingsSelected: selectedToppings.map((t) => t.name),
      quantity: qty,
      unitPrice,
    })
    setExpanded(false)
    setToppingCodes([])
    setQty(1)
  }

  return (
    <div
      className={cn(
        'rounded-xl border border-border bg-card shadow-card transition-shadow duration-200',
        expanded && 'shadow-card-hover',
      )}
    >
      {/* Header */}
      <button
        type="button"
        className="flex w-full items-start justify-between p-4 text-left"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-foreground truncate">{item.name}</span>
            <Badge variant="secondary" className="text-xs shrink-0">{item.category}</Badge>
          </div>
          <p className="mt-0.5 font-mono-numbers text-sm text-primary font-medium">
            {formatCurrency(item.price)}
          </p>
        </div>
        {expanded ? (
          <ChevronUp className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronDown className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
        )}
      </button>

      {/* Expanded customisation */}
      {expanded && (
        <div className="border-t border-border px-4 pb-4 pt-3 space-y-4 animate-fade-in">
          {/* Base */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Crust
            </p>
            <div className="flex flex-wrap gap-2">
              {bases.map((b) => (
                <button
                  key={b.code}
                  type="button"
                  onClick={() => setBaseCode(b.code)}
                  className={cn(
                    'rounded-full border px-3 py-1 text-sm transition-colors duration-100',
                    baseCode === b.code
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border bg-card text-foreground hover:border-primary/50',
                  )}
                >
                  {b.name} (+{formatCurrency(b.price)})
                </button>
              ))}
            </div>
          </div>

          {/* Toppings */}
          {toppings.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Extra Toppings
              </p>
              <div className="flex flex-wrap gap-2">
                {toppings.map((t) => (
                  <button
                    key={t.code}
                    type="button"
                    onClick={() => toggleTopping(t.code)}
                    className={cn(
                      'rounded-full border px-3 py-1 text-sm transition-colors duration-100',
                      toppingCodes.includes(t.code)
                        ? 'border-primary bg-primary text-primary-foreground'
                        : 'border-border bg-card text-foreground hover:border-primary/50',
                    )}
                  >
                    {t.name} (+{formatCurrency(t.price)})
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity + Add */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setQty((q) => Math.max(1, q - 1))}
              >
                <Minus className="h-3 w-3" />
              </Button>
              <span className="font-mono-numbers w-6 text-center text-sm font-medium">{qty}</span>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setQty((q) => q + 1)}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>

            <div className="flex items-center gap-3">
              <span className="font-mono-numbers text-sm font-medium text-foreground">
                {formatCurrency(unitPrice)}
              </span>
              <Button type="button" size="sm" onClick={handleAdd} disabled={!selectedBase}>
                <Plus className="h-3.5 w-3.5" />
                Add to Order
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

interface PizzaBuilderProps {
  items: MenuItem[]
  bases: Base[]
  toppings: Topping[]
  onAdd: (cartItem: CartItem) => void
}

export function PizzaBuilder({ items, bases, toppings, onAdd }: PizzaBuilderProps) {
  const categories = [...new Set(items.map((i) => i.category))]

  return (
    <div className="space-y-6">
      {categories.map((cat) => (
        <div key={cat}>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
            {cat}
          </h3>
          <div className="space-y-2">
            {items
              .filter((i) => i.category === cat)
              .map((item) => (
                <PizzaCard key={item.id} item={item} bases={bases} toppings={toppings} onAdd={onAdd} />
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}
