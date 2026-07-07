import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle, AlertCircle, Receipt, CreditCard, Banknote, Smartphone } from 'lucide-react'
import { completeCheckout } from '@/api/checkout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatDate, cn } from '@/lib/utils'
import type { CompleteCheckoutResponse, PaymentMethod } from '@/types'

const PAYMENT_METHODS: { value: PaymentMethod; label: string; icon: React.ElementType }[] = [
  { value: 'card', label: 'Card', icon: CreditCard },
  { value: 'cash', label: 'Cash', icon: Banknote },
  { value: 'upi', label: 'UPI', icon: Smartphone },
]

function ReceiptView({ receipt }: { receipt: CompleteCheckoutResponse }) {
  return (
    <div className="mx-auto max-w-md animate-fade-in">
      {/* Success header */}
      <div className="mb-6 flex flex-col items-center text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-success/10">
          <CheckCircle className="h-8 w-8 text-success" />
        </div>
        <h2 className="mt-3 font-display text-2xl font-semibold">Payment Complete</h2>
        <p className="text-sm text-muted-foreground">Order #{receipt.order_id}</p>
      </div>

      {/* Receipt card */}
      <Card className="shadow-receipt border-2 border-border">
        <CardContent className="p-6">
          {/* Header */}
          <div className="mb-4 text-center">
            <p className="font-display text-lg font-semibold text-foreground">PizzaFlow</p>
            <p className="text-xs text-muted-foreground">Tax Invoice</p>
            <p className="mt-1 font-mono text-xs text-muted-foreground">
              {formatDate(receipt.paid_at)}
            </p>
          </div>

          <div className="my-4 border-t border-dashed border-border" />

          {/* Itemized lines */}
          <div className="space-y-2">
            {receipt.items.map((item, idx) => (
              <div key={idx} className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate text-sm text-foreground">
                    {item.name} <span className="text-muted-foreground">× {item.quantity}</span>
                  </p>
                  <p className="truncate text-xs text-muted-foreground">
                    {item.base_selected}
                    {item.toppings_selected.length > 0 && `, ${item.toppings_selected.join(', ')}`}
                  </p>
                </div>
                <span className="font-mono-numbers shrink-0 text-sm text-foreground">
                  {formatCurrency(item.line_total)}
                </span>
              </div>
            ))}
          </div>

          <div className="my-4 border-t border-dashed border-border" />

          {/* Bill breakdown */}
          <div className="space-y-0">
            <div className="receipt-line">
              <span className="text-sm text-muted-foreground">Subtotal</span>
              <span className="font-mono-numbers text-sm">
                {formatCurrency(receipt.bill.subtotal)}
              </span>
            </div>
            {receipt.bill.discount_amount > 0 && (
              <div className="receipt-line">
                <span className="text-sm text-success">
                  Discount ({receipt.bill.discount_rate}%)
                </span>
                <span className="font-mono-numbers text-sm text-success">
                  −{formatCurrency(receipt.bill.discount_amount)}
                </span>
              </div>
            )}
            <div className="receipt-line">
              <span className="text-sm text-muted-foreground">
                GST ({receipt.bill.gst_rate}%)
              </span>
              <span className="font-mono-numbers text-sm">
                {formatCurrency(receipt.bill.gst_amount)}
              </span>
            </div>
          </div>

          <div className="my-4 border-t-2 border-foreground/20" />

          <div className="flex items-center justify-between">
            <span className="font-display text-lg font-semibold">Total Paid</span>
            <span className="font-mono-numbers text-2xl font-semibold text-primary">
              {formatCurrency(receipt.bill.total_amount)}
            </span>
          </div>

          <div className="my-4 border-t border-dashed border-border" />

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Payment Method</span>
            <Badge variant="secondary" className="capitalize">
              {receipt.payment_method}
            </Badge>
          </div>

          <div className="my-4 border-t border-dashed border-border" />

          <p className="text-center text-xs text-muted-foreground">Thank you for your order!</p>
        </CardContent>
      </Card>

      <Button
        variant="outline"
        className="mt-6 w-full"
        onClick={() => window.location.href = '/order'}
      >
        New Order
      </Button>
    </div>
  )
}

export function CheckoutPage() {
  const { orderId } = useParams<{ orderId: string }>()
  const navigate = useNavigate()
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>('card')
  const [receipt, setReceipt] = useState<CompleteCheckoutResponse | null>(null)

  const pendingOrderId = Number(orderId)

  const { mutate: pay, isPending, error } = useMutation({
    mutationFn: completeCheckout,
    onSuccess: (data) => setReceipt(data),
  })

  if (!pendingOrderId || isNaN(pendingOrderId)) {
    return (
      <div className="flex flex-col items-center gap-4 pt-20 text-center">
        <AlertCircle className="h-10 w-10 text-muted-foreground" />
        <p className="text-muted-foreground">No order found. Please start a new order.</p>
        <Button onClick={() => navigate('/order')}>New Order</Button>
      </div>
    )
  }

  if (receipt) return <ReceiptView receipt={receipt} />

  return (
    <div className="mx-auto max-w-lg">
      <div className="mb-6">
        <h1 className="font-display text-2xl font-semibold">Checkout</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Order #{pendingOrderId} — Select payment method to complete.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Receipt className="h-5 w-5 text-primary" />
            Complete Payment
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Payment method selector */}
          <div>
            <p className="mb-3 text-sm font-medium text-foreground">Payment Method</p>
            <div className="grid grid-cols-3 gap-3">
              {PAYMENT_METHODS.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setSelectedMethod(value)}
                  className={cn(
                    'flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all duration-150',
                    selectedMethod === value
                      ? 'border-primary bg-accent text-primary'
                      : 'border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground',
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          <Separator />

          {/* Note */}
          <div className="rounded-lg bg-muted/60 px-4 py-3 text-sm text-muted-foreground">
            GST at 18% will be applied to your order total.
          </div>

          {error && (
            <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              {error.message}
            </div>
          )}

          <Button
            className="w-full"
            size="lg"
            disabled={isPending}
            onClick={() =>
              pay({
                pending_order_id: pendingOrderId,
                payment_method: selectedMethod,
              })
            }
          >
            {isPending ? 'Processing…' : `Pay with ${PAYMENT_METHODS.find((m) => m.value === selectedMethod)?.label}`}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
