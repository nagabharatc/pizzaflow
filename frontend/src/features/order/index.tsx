import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, FormProvider } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useQuery, useMutation } from '@tanstack/react-query'
import { AlertCircle } from 'lucide-react'
import { fetchMenu } from '@/api/menu'
import { submitOrder } from '@/api/orders'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { CustomerForm } from './components/CustomerForm'
import { PizzaBuilder } from './components/PizzaBuilder'
import { OrderSummary } from './components/OrderSummary'
import { orderFormSchema, type OrderFormValues, type CartItem } from './types'

function MenuSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  )
}

export function OrderPage() {
  const navigate = useNavigate()
  const [cart, setCart] = useState<CartItem[]>([])
  const [submitError, setSubmitError] = useState<string | null>(null)

  const methods = useForm<OrderFormValues>({
    resolver: zodResolver(orderFormSchema),
    defaultValues: { customer: { name: '', phone_number: '' } },
  })

  const { data: menu, isLoading: menuLoading, error: menuError } = useQuery({
    queryKey: ['menu'],
    queryFn: fetchMenu,
  })

  const { mutate: placeOrder, isPending } = useMutation({
    mutationFn: submitOrder,
    onSuccess: (order) => navigate(`/checkout/${order.order_id}`),
    onError: (err: Error) => setSubmitError(err.message),
  })

  const addToCart = (item: CartItem) => setCart((prev) => [...prev, item])
  const removeFromCart = (idx: number) =>
    setCart((prev) => prev.filter((_, i) => i !== idx))

  const handleSubmit = methods.handleSubmit((values) => {
    if (cart.length === 0) {
      setSubmitError('Please add at least one item to the order.')
      return
    }
    setSubmitError(null)
    placeOrder({
      customer: values.customer,
      items: cart.map((item) => ({
        menu_item_id: item.menuItemId,
        base_selected: item.baseSelected,
        toppings_selected: item.toppingsSelected,
        quantity: item.quantity,
      })),
    })
  })

  return (
    <FormProvider {...methods}>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left column — customer + menu */}
        <div className="lg:col-span-2 space-y-6">
          {/* Page title */}
          <div>
            <h1 className="font-display text-2xl font-semibold text-foreground">New Order</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Fill in customer details, then build the pizza order.
            </p>
          </div>

          {/* Customer details */}
          <Card>
            <CardHeader>
              <CardTitle>Customer Details</CardTitle>
            </CardHeader>
            <CardContent>
              <CustomerForm />
            </CardContent>
          </Card>

          {/* Menu */}
          <Card>
            <CardHeader>
              <CardTitle>Build Pizza</CardTitle>
            </CardHeader>
            <CardContent>
              {menuLoading && <MenuSkeleton />}
              {menuError && (
                <div className="flex items-center gap-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  Failed to load menu. Please refresh.
                </div>
              )}
              {menu && (
                <PizzaBuilder
                  items={menu.items}
                  bases={menu.bases}
                  toppings={menu.toppings}
                  onAdd={addToCart}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right column — order summary */}
        <div className="space-y-4">
          <div>
            <h2 className="font-display text-2xl font-semibold text-foreground opacity-0 select-none">
              Order
            </h2>
            <p className="mt-1 text-sm opacity-0 select-none">—</p>
          </div>

          {submitError && (
            <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              {submitError}
            </div>
          )}

          <OrderSummary
            cart={cart}
            onRemove={removeFromCart}
            onSubmit={handleSubmit}
            isSubmitting={isPending}
          />
        </div>
      </div>
    </FormProvider>
  )
}
