// ── Reference ────────────────────────────────────────────────────────────────

export interface MenuItem {
  id: number
  code: string
  name: string
  category: string
  price: number
}

export interface Base {
  id: number
  code: string
  name: string
  price: number
}

export interface Topping {
  id: number
  code: string
  name: string
  price: number
}

export interface MenuResponse {
  items: MenuItem[]
  bases: Base[]
  toppings: Topping[]
}

// ── Order ─────────────────────────────────────────────────────────────────────

export interface CustomerRequest {
  name: string
  phone_number: string
}

export interface OrderItemRequest {
  menu_item_id: number
  base_selected: string
  toppings_selected: string[]
  quantity: number
}

export interface SubmitOrderRequest {
  customer: CustomerRequest
  items: OrderItemRequest[]
}

export interface CustomerSummary {
  name: string
  phone_number: string
}

export interface OrderItemResponse {
  menu_item_id: number
  name: string
  base_selected: string
  toppings_selected: string[]
  quantity: number
  unit_price: number
}

export interface PendingOrderResponse {
  order_id: number
  status: string
  customer: CustomerSummary
  items: OrderItemResponse[]
  created_at: string
}

// ── Checkout ──────────────────────────────────────────────────────────────────

export type PaymentMethod = 'cash' | 'card' | 'upi'

export interface CompleteCheckoutRequest {
  pending_order_id: number
  payment_method: PaymentMethod
}

export interface BillResponse {
  subtotal: number
  gst_rate: number
  gst_amount: number
  total_amount: number
}

export interface CompleteCheckoutResponse {
  order_id: number
  status: string
  bill: BillResponse
  payment_method: string
  paid_at: string
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export interface AnalyticsFilters {
  from_date?: string
  to_date?: string
  customer_id?: number
  payment_method?: string
  pizza_id?: number
  category?: string
}

export interface RevenueMetrics {
  total_revenue: number
  total_gst_collected: number
  average_order_value: number
}

export interface SalesMetrics {
  total_orders: number
  total_items_sold: number
  average_items_per_order: number
}

export interface CustomerMetrics {
  total_customers: number
  new_customers: number
  returning_customers: number
}

export interface ProductMetrics {
  top_selling_items: Record<string, number>
  revenue_by_category: Record<string, number>
  most_popular_base: string
}

export interface PaymentMetrics {
  revenue_by_payment_method: Record<string, number>
  orders_by_payment_method: Record<string, number>
}

export interface GrowthMetrics {
  week_over_week_revenue_change: number
  month_over_month_revenue_change: number
}

export interface BusinessIntelligenceModel {
  revenue: RevenueMetrics
  sales: SalesMetrics
  customers: CustomerMetrics
  products: ProductMetrics
  payments: PaymentMetrics
  growth: GrowthMetrics
}

export interface AnalyticsResponse {
  filters_applied: AnalyticsFilters
  intelligence: BusinessIntelligenceModel
}

// ── AI Advisor ────────────────────────────────────────────────────────────────

export interface AIQueryRequest {
  question: string
  filters?: AnalyticsFilters
}

export interface AIQueryResponse {
  question: string
  answer: string
  intelligence_snapshot: BusinessIntelligenceModel
}

// ── Cart (client-only, never sent as-is to backend) ───────────────────────────

export interface CartItem {
  menuItemId: number
  name: string
  category: string
  baseSelected: string
  toppingsSelected: string[]
  quantity: number
  unitPrice: number
}
