import {
  CircleHelp,
  LayoutDashboard,
  List,
  Settings,
  Tags,
  Upload,
  type LucideIcon,
} from 'lucide-react'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

/** Sidebar sections, separated by a divider. A page is listed only once it is built. */
export const NAV_SECTIONS: NavItem[][] = [
  [
    { to: '/', label: 'Özet', icon: LayoutDashboard },
    { to: '/islemler', label: 'İşlemler', icon: List },
    { to: '/yukle', label: 'Ekstre Yükle', icon: Upload },
    { to: '/kategoriler', label: 'Kategoriler', icon: Tags },
  ],
  [
    { to: '/ayarlar', label: 'Ayarlar', icon: Settings },
    { to: '/yardim', label: 'Yardım', icon: CircleHelp },
  ],
]

/** The title shown in the app bar for the current page. */
export function pageTitle(pathname: string): string {
  const item = NAV_SECTIONS.flat().find(({ to }) => to === pathname)
  return item?.label ?? 'Harcamam'
}
