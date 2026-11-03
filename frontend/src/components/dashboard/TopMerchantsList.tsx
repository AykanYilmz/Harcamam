import type { MerchantSpending } from '../../api/types.ts'
import { formatCurrency } from '../../lib/format.ts'
import { Card } from '../ui/Card.tsx'

export function TopMerchantsList({ merchants }: { merchants: MerchantSpending[] }) {
  return (
    <Card>
      <h2 className="font-semibold text-fg">En çok harcama yapılan yerler</h2>
      {merchants.length === 0 ? (
        <p className="mt-4 text-sm text-fg-subtle">Bu ay harcama yok.</p>
      ) : (
        <ol className="mt-2 divide-y divide-line">
          {merchants.map((merchant, index) => (
            <li key={merchant.name} className="flex items-center gap-3 py-3">
              <span className="w-5 text-sm font-medium text-fg-faint tabular-nums">
                {index + 1}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-fg">{merchant.name}</p>
                <p className="text-xs text-fg-subtle">
                  {merchant.category_name} · {merchant.transaction_count} işlem
                </p>
              </div>
              <span className="text-sm font-semibold text-fg tabular-nums">
                {formatCurrency(merchant.amount)}
              </span>
            </li>
          ))}
        </ol>
      )}
    </Card>
  )
}
