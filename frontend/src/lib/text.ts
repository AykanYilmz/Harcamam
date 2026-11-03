/**
 * A starting keyword for "save as rule": the first word that looks like a name.
 * "MIGROS KADIKÖY İSTANBUL" -> "MIGROS", "NETFLIX.COM" -> "NETFLIX", "A101 MODA" -> "A101".
 * Only a suggestion: the user can edit it before saving.
 */
export function suggestKeyword(description: string): string {
  const words = description.split(/[^\p{L}\p{N}]+/u).filter(Boolean)
  const word = words.find((candidate) => /\p{L}/u.test(candidate) && candidate.length >= 2)
  return word ?? description.trim()
}
