import { LayoutDashboard, List, Tags, Upload, type LucideIcon } from 'lucide-react'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Özet', icon: LayoutDashboard },
  { to: '/yukle', label: 'Ekstre Yükle', icon: Upload },
  { to: '/islemler', label: 'İşlemler', icon: List },
  { to: '/kategoriler', label: 'Kategoriler', icon: Tags },
]
