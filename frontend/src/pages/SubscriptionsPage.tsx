import { EyeOff, Repeat, TrendingUp } from 'lucide-react'
import { useState } from 'react'
import {
  useDismissSubscription,
  useRestoreSubscription,
  useSubscriptions,
} from '../api/subscriptions.ts'
import type { Subscription } from '../api/types.ts'
import { CategoryIcon } from '../components/CategoryIcon.tsx'
import { ErrorAlert } from '../components/ui/Alert.tsx'
import { Card } from '../components/ui/Card.tsx'
import { PageLoader } from '../components/ui/Spinner.tsx'
import { errorMessage } from '../lib/errors.ts'
import { formatCurrency, formatDate } from '../lib/format.ts'

function SubscriptionRow({ subscription }: { subscription: Subscription }) {
  const dismiss = useDismissSubscription()

  return (
    <li className="flex flex-wrap items-start gap-x-3 gap-y-2 py-4">
      <CategoryIcon icon={subscription.icon} color={subscription.color} />
      <div className="min-w-0 flex-1">
        <p className="font-medium text-fg">{subscription.name}</p>
        <p className="text-xs text-fg-subtle">
          {subscription.category_name} · {subscription.charge_count} ödeme · ilk:{' '}
          {formatDate(subscription.first_charge)}
        </p>
        {subscription.previous_amount && (
          <p className="mt-1 inline-flex items-center gap-1 rounded-full bg-warning-soft px-2 py-0.5 text-xs font-medium text-warning-fg">
            <TrendingUp aria-hidden className="size-3.5" />
            Zam: {formatCurrency(subscription.previous_amount)} →{' '}
            {formatCurrency(subscription.amount)}
          </p>
        )}
        {dismiss.isError && (
          <div className="mt-2">
            <ErrorAlert>{errorMessage(dismiss.error)}</ErrorAlert>
          </div>
        )}
      </div>
      <div className="text-right">
        <p className="font-semibold text-fg tabular-nums">
          {formatCurrency(subscription.amount)}
          <span className="text-xs font-normal text-fg-subtle"> / ay</span>
        </p>
        <p className="text-xs text-fg-subtle">
          {subscription.active && subscription.next_charge
            ? `Sonraki: ${formatDate(subscription.next_charge)}`
            : `Son ödeme: ${formatDate(subscription.last_charge)}`}
        </p>
        <button
          type="button"
          onClick={() => dismiss.mutate(subscription.key)}
          disabled={dismiss.isPending}
          className="mt-1 inline-flex items-center gap-1 rounded text-xs text-fg-subtle hover:text-fg disabled:opacity-60"
        >
          <EyeOff aria-hidden className="size-3.5" />
          Abonelik değil
        </button>
      </div>
    </li>
  )
}

export function SubscriptionsPage() {
  const report = useSubscriptions()
  const restore = useRestoreSubscription()
  const [showDismissed, setShowDismissed] = useState(false)

  if (report.isPending) return <PageLoader />
  if (report.isError) return <ErrorAlert>{errorMessage(report.error)}</ErrorAlert>

  const { subscriptions, dismissed } = report.data
  const active = subscriptions.filter((subscription) => subscription.active)
  const stopped = subscriptions.filter((subscription) => !subscription.active)

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      {subscriptions.length === 0 ? (
        <Card className="flex flex-col items-center py-12 text-center">
          <Repeat aria-hidden className="size-10 text-fg-faint" />
          <p className="mt-3 font-medium text-fg-secondary">Düzenli ödeme bulunamadı</p>
          <p className="mt-1 max-w-sm text-sm text-fg-subtle">
            Aynı yere en az üç ay üst üste benzer tutarda ödeme yaptığında burada görünür. Birkaç
            aylık ekstre yükle.
          </p>
        </Card>
      ) : (
        <>
          <Card>
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-sm text-fg-subtle">{active.length} düzenli ödeme, ayda</p>
                <p className="text-2xl font-semibold text-fg tabular-nums">
                  {formatCurrency(report.data.monthly_total)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-fg-subtle">Yılda</p>
                <p className="text-lg font-semibold text-fg tabular-nums">
                  {formatCurrency(report.data.yearly_total)}
                </p>
              </div>
            </div>
            <p className="mt-3 text-xs text-fg-subtle">
              Her ay benzer tutarda tekrar eden ödemeler; abonelik olmayanları "Abonelik değil" ile
              gizleyebilirsin.
            </p>
          </Card>

          {active.length > 0 && (
            <Card>
              <h2 className="font-semibold text-fg">Aktif</h2>
              <ul className="divide-y divide-line">
                {active.map((subscription) => (
                  <SubscriptionRow key={subscription.key} subscription={subscription} />
                ))}
              </ul>
            </Card>
          )}

          {stopped.length > 0 && (
            <Card>
              <h2 className="font-semibold text-fg">Durmuş görünenler</h2>
              <p className="mt-1 text-sm text-fg-subtle">
                Bir buçuk aydır ödeme yok; iptal ettiysen her şey yolunda.
              </p>
              <ul className="divide-y divide-line">
                {stopped.map((subscription) => (
                  <SubscriptionRow key={subscription.key} subscription={subscription} />
                ))}
              </ul>
            </Card>
          )}
        </>
      )}

      {dismissed.length > 0 && (
        <Card>
          <button
            type="button"
            onClick={() => setShowDismissed(!showDismissed)}
            aria-expanded={showDismissed}
            className="text-sm font-medium text-fg-muted hover:text-fg"
          >
            Gizlenenler ({dismissed.length})
          </button>
          {showDismissed && (
            <ul className="mt-2 space-y-1">
              {dismissed.map((item) => (
                <li key={item.key} className="flex items-center justify-between gap-3 text-sm">
                  <span className="text-fg-muted">{item.name}</span>
                  <button
                    type="button"
                    onClick={() => restore.mutate(item.key)}
                    disabled={restore.isPending}
                    className="font-medium text-accent-fg hover:underline disabled:opacity-60"
                  >
                    Geri al
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </div>
  )
}
