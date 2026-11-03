import {
  ArrowLeftRight,
  Banknote,
  Car,
  CircleEllipsis,
  Film,
  HeartPulse,
  House,
  Receipt,
  Repeat,
  Shirt,
  ShoppingBag,
  ShoppingCart,
  Tag,
  Utensils,
  Wallet,
  type LucideIcon,
} from 'lucide-react'

/** Icon names stored on categories (see the default categories migration) -> components. */
export const CATEGORY_ICONS: Record<string, LucideIcon> = {
  'shopping-cart': ShoppingCart,
  utensils: Utensils,
  car: Car,
  receipt: Receipt,
  home: House,
  film: Film,
  'heart-pulse': HeartPulse,
  shirt: Shirt,
  'shopping-bag': ShoppingBag,
  repeat: Repeat,
  banknote: Banknote,
  'arrow-left-right': ArrowLeftRight,
  wallet: Wallet,
  'circle-ellipsis': CircleEllipsis,
  tag: Tag,
}

/** The category's icon on a chip in its own color: the category's identity everywhere. */
export function CategoryIcon({
  icon,
  color,
  className = 'size-8',
}: {
  icon: string
  color: string
  className?: string
}) {
  const Icon = CATEGORY_ICONS[icon] ?? Tag
  return (
    <span
      aria-hidden
      className={`flex shrink-0 items-center justify-center rounded-lg text-white ${className}`}
      style={{ backgroundColor: color }}
    >
      <Icon className="size-[55%]" />
    </span>
  )
}
