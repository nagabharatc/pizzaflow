import { z } from 'zod'

export const orderFormSchema = z.object({
  customer: z.object({
    name: z
      .string()
      .min(1, 'Name is required')
      .max(15, 'Name must be at most 15 characters')
      .regex(/^[A-Za-z ]+$/, 'Name cannot contain numbers or special characters'),
    phone_number: z
      .string()
      .regex(/^[6-9]\d{9}$/, 'Enter a valid 10-digit phone number starting with 6-9'),
  }),
})

export type OrderFormValues = z.infer<typeof orderFormSchema>

export interface CartItem {
  menuItemId: number
  name: string
  category: string
  baseSelected: string
  toppingsSelected: string[]
  quantity: number
  unitPrice: number
}
