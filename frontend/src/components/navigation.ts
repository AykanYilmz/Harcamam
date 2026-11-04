import {
  CalendarDays,
  ChartColumn,
  CircleHelp,
  GraduationCap,
  LayoutDashboard,
  List,
  Settings,
  Target,
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
export const UNCATEGORIZED_PATH = '/kategori-egitimi'
export const BUDGETS_PATH = '/butceler'

export const NAV_SECTIONS: NavItem[][] = [
  [
    { to: '/', label: 'Özet', icon: LayoutDashboard },
    { to: '/islemler', label: 'İşlemler', icon: List },
    { to: '/takvim', label: 'Takvim', icon: CalendarDays },
    { to: '/raporlar', label: 'Raporlar', icon: ChartColumn },
    { to: BUDGETS_PATH, label: 'Bütçeler', icon: Target },
    { to: '/yukle', label: 'Ekstre Yükle', icon: Upload },
    { to: '/kategoriler', label: 'Kategoriler', icon: Tags },
    { to: UNCATEGORIZED_PATH, label: 'Kategori Eğitimi', icon: GraduationCap },
  ],
  [
    { to: '/ayarlar', label: 'Ayarlar', icon: Settings },
    { to: '/yardim', label: 'Yardım', icon: CircleHelp },
  ],
]

/** The title shown in the app bar for the current page. */
export function pageTitle(pathname: string): string {
  const item = NAV_SECTIONS.flat().find(({ to }) => to === pathname)
  return item?.label ?? 'HesapKitap'
}
