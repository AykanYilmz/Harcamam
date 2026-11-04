/**
 * Reads an amount typed the Turkish way into the API's decimal string, or null if it isn't
 * a positive amount: "8.000" -> "8000", "1.250,50" -> "1250.50", "₺850" -> "850".
 *
 * A dot followed by exactly three digits is a thousands separator ("8.000" is eight
 * thousand, as everywhere else in the app); otherwise it is read as a decimal point ("12.5").
 */
export function parseAmountInput(text: string): string | null {
  let value = text.replace(/\s|₺|TL/gi, '')
  if (value.includes(',')) {
    // Dots, if any, must group thousands properly: "1.250,50" yes, "1.23,45" no.
    if (!/^(\d{1,3}(\.\d{3})+|\d+),\d{1,2}$/.test(value)) return null
    value = value.replace(/\./g, '').replace(',', '.')
  } else if (/^\d{1,3}(\.\d{3})+$/.test(value)) {
    value = value.replace(/\./g, '')
  }
  if (!/^\d+(\.\d{1,2})?$/.test(value) || Number(value) <= 0) return null
  return value
}
