// Friendly names for the types generated from the backend's OpenAPI schema (`npm run gen:api`).
import type { components } from './schema'

type Schemas = components['schemas']

export type User = Schemas['UserRead']
export type TokenPair = Schemas['TokenPair']
