#!/usr/bin/env python3
"""Generate individual language_quiz/{id}.json files on the VM.
Covers TypeScript (ts_001–ts_030), Python (py_001–py_025), C# (cs_001–cs_025).
"""
import json
from pathlib import Path

OUT = Path("/mnt/c/Users/U/Documents/nanogrindv2/data_generated/language_quiz")
OUT.mkdir(exist_ok=True)

QUESTIONS = [
    # ══════════════════════════════════════════════════════════════════════════
    # TYPESCRIPT (ts_001 – ts_030)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Type System ─────────────────────────────────────────────────────────
    {
        "id": "ts_001",
        "language": "TypeScript",
        "topic": "Type System",
        "subtopic": "unknown vs any",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What's the difference between `unknown` and `any` in TypeScript?",
        "task": "Write a function `safeParseJson` that accepts `unknown` input and safely narrows it to a string.",
        "answer": {
            "key_points": [
                "`any` disables type checking — you can do anything with it, no errors.",
                "`unknown` is type-safe — you must narrow it before use (typeof, instanceof, type guard).",
                "Use `unknown` for values from external sources (API responses, JSON.parse) to force explicit handling.",
                "Prefer `unknown` over `any` at system boundaries."
            ],
            "example_solution": "function safeParseJson(input: unknown): string {\n  if (typeof input === 'string') return input;\n  throw new Error('Expected string');\n}"
        }
    },
    {
        "id": "ts_002",
        "language": "TypeScript",
        "topic": "Type System",
        "subtopic": "never type",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does this function's return type tell you, and why does the switch need a `default` with `never`?",
        "code": "type Shape = { kind: 'circle'; r: number } | { kind: 'square'; s: number };\n\nfunction area(shape: Shape): number {\n  switch (shape.kind) {\n    case 'circle': return Math.PI * shape.r ** 2;\n    case 'square': return shape.s ** 2;\n    default:\n      const _exhaustive: never = shape;\n      throw new Error('Unhandled shape');\n  }\n}",
        "answer": {
            "result": "Exhaustiveness check via never",
            "explanation": "In the default branch, `shape` has been narrowed to `never` (all union members handled). Assigning it to `never` is a compile-time exhaustiveness check — if you add a new Shape variant and forget to handle it, TypeScript errors here. It's a zero-cost runtime safety net."
        }
    },
    {
        "id": "ts_003",
        "language": "TypeScript",
        "topic": "Type System",
        "subtopic": "type vs interface",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are the key differences between `type` and `interface` in TypeScript? When do you choose one over the other?",
        "task": "Write an example showing declaration merging with `interface` and show why the same doesn't work with `type`.",
        "answer": {
            "key_points": [
                "Interfaces support declaration merging — defining the same interface twice merges them. Types don't.",
                "Types can express unions, intersections, tuples, mapped types, conditional types. Interfaces can't.",
                "Interfaces are open (mergeable), types are closed (exact definition).",
                "Use interface for public API shapes (libraries, class contracts). Use type for complex compositions.",
                "Both compile away — no runtime difference."
            ],
            "example_solution": "interface Window { myLib: string; }\ninterface Window { anotherProp: number; } // merges — OK\n\ntype MyWindow = { myLib: string; };\ntype MyWindow = { anotherProp: number; }; // Error: duplicate identifier"
        }
    },
    {
        "id": "ts_004",
        "language": "TypeScript",
        "topic": "Type System",
        "subtopic": "strictNullChecks",
        "difficulty": "beginner",
        "format": "snippet",
        "prompt": "With `strictNullChecks: true`, which line errors and why?",
        "code": "let name: string = 'Mayu';\nname = null;             // line A\n\nlet maybeName: string | null = null;\nmaybeName = 'Mayu';      // line B\n\nfunction greet(n: string | null) {\n  console.log(n.toUpperCase()); // line C\n}",
        "answer": {
            "result": "Line A and Line C error",
            "explanation": "Line A: `string` no longer includes `null` when strictNullChecks is on. You need `string | null`. Line C: `n` could be `null` — TS won't let you call `.toUpperCase()` without narrowing first (`if (n !== null)`). Line B is fine — `string | null` accepts both."
        }
    },
    {
        "id": "ts_005",
        "language": "TypeScript",
        "topic": "Type System",
        "subtopic": "void vs undefined",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What's the difference between `void` and `undefined` as return types? Why does it matter for callbacks?",
        "task": "Write a `forEach`-like function signature where the callback returns `void`, and explain why returning a value from the callback is still allowed.",
        "answer": {
            "key_points": [
                "`undefined` means the function literally returns `undefined`. Calling code can use the return value as `undefined`.",
                "`void` means 'I don't care what you return' — used for callbacks where the return value is intentionally ignored.",
                "A callback typed as `() => void` can return a value (string, number) without error — TS ignores it.",
                "This allows methods like `Array.prototype.push` (returns number) to be passed where `() => void` is expected."
            ],
            "example_solution": "function myForEach<T>(arr: T[], cb: (item: T) => void): void {\n  for (const item of arr) cb(item);\n}\n// Valid — push returns number but () => void ignores it:\nmyForEach([1, 2, 3], arr.push.bind(arr));"
        }
    },

    # ── Utility Types ────────────────────────────────────────────────────────
    {
        "id": "ts_006",
        "language": "TypeScript",
        "topic": "Utility Types",
        "subtopic": "Partial / Required / Readonly",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "Explain `Partial<T>`, `Required<T>`, and `Readonly<T>`. How are they implemented under the hood?",
        "task": "Write a `updateUser` function that accepts a `User` and a `Partial<User>` patch, merges them, and returns a `Readonly<User>`.",
        "answer": {
            "key_points": [
                "Partial<T>: makes all properties optional. `{ [K in keyof T]?: T[K] }`",
                "Required<T>: makes all properties required. `{ [K in keyof T]-?: T[K] }` (the `-?` removes optionality)",
                "Readonly<T>: makes all properties readonly. `{ readonly [K in keyof T]: T[K] }`",
                "All are mapped types over `keyof T`."
            ],
            "example_solution": "type User = { id: number; name: string; email: string };\nfunction updateUser(user: User, patch: Partial<User>): Readonly<User> {\n  return Object.freeze({ ...user, ...patch });\n}"
        }
    },
    {
        "id": "ts_007",
        "language": "TypeScript",
        "topic": "Utility Types",
        "subtopic": "Pick / Omit",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What are the types of `A` and `B`?",
        "code": "type User = { id: number; name: string; email: string; password: string };\n\ntype A = Pick<User, 'id' | 'name'>;\ntype B = Omit<User, 'password'>;",
        "answer": {
            "result": "A = { id: number; name: string }\nB = { id: number; name: string; email: string }",
            "explanation": "Pick keeps only the listed keys. Omit removes the listed keys (implemented as `Pick<T, Exclude<keyof T, K>>`). Common pattern: use Omit to create safe DTOs that strip sensitive fields like `password` before returning to clients."
        }
    },
    {
        "id": "ts_008",
        "language": "TypeScript",
        "topic": "Utility Types",
        "subtopic": "Record",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What does `Record<K, V>` do? How does it differ from `{ [key: string]: V }`?",
        "task": "Write a `groupBy` function typed with Record that groups an array of `{ id: number; category: string }` objects by category.",
        "answer": {
            "key_points": [
                "Record<K, V> creates an object type with keys of type K and values of type V.",
                "Unlike an index signature `{ [key: string]: V }`, Record requires K to be a specific union — TypeScript checks all keys are present when K is a string literal union.",
                "`Record<string, V>` ≈ `{ [key: string]: V }` but Record is cleaner.",
                "Common use: lookup maps, state machines, grouped data."
            ],
            "example_solution": "type Item = { id: number; category: string };\nfunction groupBy(items: Item[]): Record<string, Item[]> {\n  return items.reduce((acc, item) => {\n    (acc[item.category] ??= []).push(item);\n    return acc;\n  }, {} as Record<string, Item[]>);\n}"
        }
    },
    {
        "id": "ts_009",
        "language": "TypeScript",
        "topic": "Utility Types",
        "subtopic": "Exclude / Extract",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What are the types of `A`, `B`, `C`, and `D`?",
        "code": "type T = 'a' | 'b' | 'c' | 'd';\n\ntype A = Exclude<T, 'a' | 'b'>;\ntype B = Extract<T, 'b' | 'c' | 'z'>;\ntype C = Exclude<string | number | boolean, string>;\ntype D = NonNullable<string | null | undefined>;",
        "answer": {
            "result": "A = 'c' | 'd'\nB = 'b' | 'c'\nC = number | boolean\nD = string",
            "explanation": "Exclude removes members from a union that are assignable to the second argument. Extract keeps only members assignable to the second argument. NonNullable = Exclude<T, null | undefined>. These work via distributive conditional types."
        }
    },
    {
        "id": "ts_010",
        "language": "TypeScript",
        "topic": "Utility Types",
        "subtopic": "ReturnType / Parameters",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What are the types of `A`, `B`, and `C`?",
        "code": "function fetchUser(id: number, options: { cache: boolean }): Promise<{ name: string }> {\n  return Promise.resolve({ name: 'Mayu' });\n}\n\ntype A = ReturnType<typeof fetchUser>;\ntype B = Parameters<typeof fetchUser>;\ntype C = Awaited<A>;",
        "answer": {
            "result": "A = Promise<{ name: string }>\nB = [id: number, options: { cache: boolean }]\nC = { name: string }",
            "explanation": "ReturnType extracts the return type. Parameters extracts params as a tuple. Awaited unwraps a Promise (recursively). Together, these let you derive types from existing functions without repeating yourself — useful for decorators, middleware wrappers, and mocking."
        }
    },
    {
        "id": "ts_011",
        "language": "TypeScript",
        "topic": "Utility Types",
        "subtopic": "ConstructorParameters / InstanceType",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "What are the types of `A` and `B`, and when would you use them?",
        "code": "class ApiClient {\n  constructor(baseUrl: string, timeout: number) {}\n  fetch(path: string): Promise<unknown> { return Promise.resolve(); }\n}\n\ntype A = ConstructorParameters<typeof ApiClient>;\ntype B = InstanceType<typeof ApiClient>;",
        "answer": {
            "result": "A = [baseUrl: string, timeout: number]\nB = ApiClient",
            "explanation": "ConstructorParameters gives you the constructor args as a tuple — useful for factory functions and DI containers. InstanceType gives you the instance type from the class constructor — useful when you have `typeof MyClass` but need the instance shape. Together they let you build generic class wrappers without repeating type annotations."
        }
    },

    # ── Generics ─────────────────────────────────────────────────────────────
    {
        "id": "ts_012",
        "language": "TypeScript",
        "topic": "Generics",
        "subtopic": "constraints",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What does `T extends SomeType` mean as a generic constraint? How does it differ from a conditional type using `extends`?",
        "task": "Write a generic `getProperty<T, K extends keyof T>` function that safely reads a property from an object.",
        "answer": {
            "key_points": [
                "In `<T extends X>`: constrains T to types assignable to X. T must have at least X's shape.",
                "In conditional types `T extends X ? A : B`: distributes over unions, evaluates as a boolean check.",
                "The same keyword, two different contexts — generic parameter vs. conditional type.",
                "`K extends keyof T` ensures K is a valid key of T at compile time."
            ],
            "example_solution": "function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {\n  return obj[key];\n}\nconst user = { id: 1, name: 'Mayu' };\nconst name = getProperty(user, 'name'); // type: string"
        }
    },
    {
        "id": "ts_013",
        "language": "TypeScript",
        "topic": "Generics",
        "subtopic": "conditional types + infer",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "What does `UnpackPromise<T>` resolve to for each case?",
        "code": "type UnpackPromise<T> = T extends Promise<infer U> ? U : T;\n\ntype A = UnpackPromise<Promise<string>>;\ntype B = UnpackPromise<Promise<Promise<number>>>;\ntype C = UnpackPromise<boolean>;",
        "answer": {
            "result": "A = string\nB = Promise<number>\nC = boolean",
            "explanation": "`infer U` captures the type argument inside Promise. It only unwraps ONE level — B is Promise<number> not number (for recursive unwrapping you'd need Awaited<T>). C hits the false branch (boolean doesn't extend Promise<any>) so T is returned as-is. `infer` is the mechanism behind ReturnType, Parameters, and Awaited."
        }
    },
    {
        "id": "ts_014",
        "language": "TypeScript",
        "topic": "Generics",
        "subtopic": "mapped types",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "What is the type of `Result`? Explain each piece of the mapped type.",
        "code": "type Getters<T> = {\n  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];\n};\n\ntype User = { name: string; age: number };\ntype Result = Getters<User>;",
        "answer": {
            "result": "{ getName: () => string; getAge: () => number }",
            "explanation": "`[K in keyof T as ...]` is a key remapping mapped type. `as \\`get${Capitalize<string & K>}\\`` renames each key by capitalizing and prefixing with 'get'. `string & K` ensures K is treated as a string for Capitalize. The value `() => T[K]` turns each property into a getter function."
        }
    },
    {
        "id": "ts_015",
        "language": "TypeScript",
        "topic": "Generics",
        "subtopic": "distributive conditional types",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "Why does `A` differ from `B`, even though they look similar?",
        "code": "type ToArray<T> = T extends any ? T[] : never;\ntype Wrap<T> = [T] extends [any] ? T[] : never;\n\ntype A = ToArray<string | number>;\ntype B = Wrap<string | number>;",
        "answer": {
            "result": "A = string[] | number[]\nB = (string | number)[]",
            "explanation": "Conditional types distribute over naked type parameters in unions. `T extends any` with T = `string | number` runs twice: `string extends any ? string[] : never` | `number extends any ? number[] : never` = `string[] | number[]`. Wrapping in a tuple `[T] extends [any]` prevents distribution — it evaluates T as a whole union, giving `(string | number)[]`."
        }
    },
    {
        "id": "ts_016",
        "language": "TypeScript",
        "topic": "Generics",
        "subtopic": "default type parameters",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "How do default type parameters work in TypeScript generics? When are they useful?",
        "task": "Write a generic `createStore<S = {}>` function where S defaults to an empty object, and the store has a `getState(): S` method.",
        "answer": {
            "key_points": [
                "Default type params use `<T = DefaultType>` — if T is not provided or inferred, it falls back to DefaultType.",
                "Useful for optional generics in component libraries, framework utilities, and event emitters.",
                "Defaults can reference earlier type params: `<T, U = T[]>` is valid.",
                "If inference is possible, the inferred type takes precedence over the default."
            ],
            "example_solution": "function createStore<S = {}>(\n  initialState: S\n): { getState: () => S; setState: (s: Partial<S>) => void } {\n  let state = initialState;\n  return {\n    getState: () => state,\n    setState: (s) => { state = { ...state, ...s }; },\n  };\n}"
        }
    },

    # ── Advanced Patterns ────────────────────────────────────────────────────
    {
        "id": "ts_017",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "discriminated unions",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are discriminated unions and what makes them work well with TypeScript's control flow narrowing?",
        "task": "Model a `Result<T, E>` type as a discriminated union with `ok` as the discriminant, and write a `handleResult` function that narrows it.",
        "answer": {
            "key_points": [
                "A discriminated union is a union of object types sharing a literal type property (the discriminant).",
                "TypeScript narrows the type within switch/if branches based on the discriminant.",
                "All members must share the same discriminant key — they differ only in its literal value.",
                "Enables exhaustiveness checking with never in the default branch.",
                "Alternative to class hierarchies — no runtime overhead beyond the discriminant property."
            ],
            "example_solution": "type Result<T, E = Error> =\n  | { ok: true; value: T }\n  | { ok: false; error: E };\n\nfunction handleResult<T>(r: Result<T>): T {\n  if (r.ok) return r.value;\n  throw r.error;\n}"
        }
    },
    {
        "id": "ts_018",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "branded / nominal types",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "TypeScript uses structural typing — what problem does that cause, and how do branded (nominal) types solve it?",
        "task": "Create branded types `UserId` and `OrderId` (both underlying `number`) so that passing a `UserId` where `OrderId` is expected is a compile error.",
        "answer": {
            "key_points": [
                "Structural typing: two types with the same shape are interchangeable — UserId = number and OrderId = number are the same.",
                "This lets you accidentally pass a user ID where an order ID is needed — no compile error.",
                "Branded types add a phantom type tag that makes them nominally distinct at compile time.",
                "The brand is only in the type system — erased at runtime, zero cost.",
                "Common brand patterns: `type UserId = number & { _brand: 'UserId' }` or using unique symbols."
            ],
            "example_solution": "declare const _brand: unique symbol;\ntype Brand<T, B> = T & { [_brand]: B };\n\ntype UserId = Brand<number, 'UserId'>;\ntype OrderId = Brand<number, 'OrderId'>;\n\nconst toUserId = (n: number): UserId => n as UserId;\nfunction getOrder(id: OrderId): void {}\nconst uid = toUserId(1);\ngetOrder(uid); // Error: UserId is not assignable to OrderId"
        }
    },
    {
        "id": "ts_019",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "template literal types",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "What is the type of `EventNames` and `Handlers`?",
        "code": "type Events = 'click' | 'focus' | 'blur';\n\ntype EventNames = `on${Capitalize<Events>}`;\n\ntype Handlers = {\n  [E in Events as `on${Capitalize<E>}`]: (event: E) => void;\n};",
        "answer": {
            "result": "EventNames = 'onClick' | 'onFocus' | 'onBlur'\nHandlers = { onClick: (event: 'click') => void; onFocus: (event: 'focus') => void; onBlur: (event: 'blur') => void }",
            "explanation": "Template literal types compose string unions. Capitalize is a built-in intrinsic string type. The mapped type with `as` remaps keys using the template literal. This pattern is how libraries like Zustand and type-safe event emitters are built — no codegen needed."
        }
    },
    {
        "id": "ts_020",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "recursive types",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "What type does `DeepReadonly<User>` resolve to? What real-world problem does this pattern solve?",
        "code": "type DeepReadonly<T> = T extends (infer U)[]\n  ? ReadonlyArray<DeepReadonly<U>>\n  : T extends object\n  ? { readonly [K in keyof T]: DeepReadonly<T[K]> }\n  : T;\n\ntype User = { id: number; address: { city: string; zip: string } };\ntype R = DeepReadonly<User>;",
        "answer": {
            "result": "{ readonly id: number; readonly address: { readonly city: string; readonly zip: string } }",
            "explanation": "Recursive conditional types apply transformations at every depth. The array branch handles T[] → ReadonlyArray<DeepReadonly<U>>. The object branch maps each property recursively. The base case returns primitives unchanged. Real use: immutable state trees (Redux), config objects you don't want mutated downstream."
        }
    },
    {
        "id": "ts_021",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "type guards and assertion functions",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What's the difference between a type guard (`x is T`) and an assertion function (`asserts x is T`)? When would you use each?",
        "task": "Write a type guard `isApiError` and an assertion function `assertIsString` — show how control flow differs after each.",
        "answer": {
            "key_points": [
                "Type guard `(x: unknown): x is T` returns boolean — caller must check the return value in an if/else.",
                "Assertion function `(x: unknown): asserts x is T` throws if assertion fails — TS narrows after the call unconditionally.",
                "Assertion functions are useful at API boundaries where you want to throw immediately rather than branch.",
                "Both are compile-time annotations backed by runtime logic — TypeScript trusts you."
            ],
            "example_solution": "function isApiError(e: unknown): e is { code: number; message: string } {\n  return typeof e === 'object' && e !== null && 'code' in e;\n}\n\nfunction assertIsString(v: unknown): asserts v is string {\n  if (typeof v !== 'string') throw new TypeError('Expected string');\n}\n\nif (isApiError(err)) { console.log(err.code); }\nassertIsString(name); console.log(name.toUpperCase());"
        }
    },
    {
        "id": "ts_022",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "declaration merging and module augmentation",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is declaration merging? How do you use module augmentation to add properties to an existing library's types (e.g., adding `user` to Express's `Request`)?",
        "task": "Write the module augmentation to add `user: { id: string }` to Express's `Request` interface.",
        "answer": {
            "key_points": [
                "Declaration merging: when TypeScript sees two declarations with the same name, it merges them.",
                "Works for interfaces, namespaces, and enums — not for types or classes.",
                "Module augmentation: extend types from an external module by re-opening its module declaration.",
                "Must import something from the module (or use `export {}`) to make it a module, not a script."
            ],
            "example_solution": "import 'express';\n\ndeclare module 'express' {\n  interface Request {\n    user?: { id: string };\n  }\n}\n\napp.get('/me', (req, res) => {\n  console.log(req.user?.id);\n});"
        }
    },

    # ── Production / Config ──────────────────────────────────────────────────
    {
        "id": "ts_023",
        "language": "TypeScript",
        "topic": "Production Config",
        "subtopic": "strict mode options",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What does `\"strict\": true` enable? Name at least 5 sub-flags it turns on and what each catches.",
        "task": "Show a code example that passes without strict but fails with strict enabled.",
        "answer": {
            "key_points": [
                "strictNullChecks: null/undefined not assignable to other types.",
                "strictFunctionTypes: stricter checking of function parameter types (contravariance).",
                "strictPropertyInitialization: class properties must be initialized in constructor.",
                "noImplicitAny: error when TS can't infer a type and falls back to any.",
                "noImplicitThis: error when `this` has implicit any type.",
                "strictBindCallApply: stricter checking of bind/call/apply arguments.",
                "useUnknownInCatchVariables: catch variables are `unknown` not `any` (TS 4.4+)."
            ],
            "example_solution": "function greet(name) { console.log(name.toUpperCase()); } // noImplicitAny\n\nclass User { name: string; }  // strictPropertyInitialization\n\nconst el = document.getElementById('app');\nel.style.color = 'red'; // strictNullChecks: el could be null"
        }
    },
    {
        "id": "ts_024",
        "language": "TypeScript",
        "topic": "Production Config",
        "subtopic": "ESM vs CJS interop",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What's the difference between `module: 'CommonJS'` and `module: 'ESNext'` in tsconfig? What does `esModuleInterop` do, and what problem does it solve?",
        "task": "Show the difference in compiled output for `import fs from 'fs'` with and without `esModuleInterop`.",
        "answer": {
            "key_points": [
                "module: CommonJS compiles to require/exports. module: ESNext emits ES modules (import/export).",
                "CJS modules don't have a default export — they export an object. Importing with default import syntax breaks without interop.",
                "esModuleInterop adds a __importDefault helper that wraps CJS modules in { default: module }.",
                "allowSyntheticDefaultImports (implied by esModuleInterop) suppresses the type error.",
                "Without esModuleInterop: `import * as fs from 'fs'`. With it: `import fs from 'fs'` works."
            ],
            "example_solution": "// Without esModuleInterop:\nconst fs_1 = require('fs');\n\n// With esModuleInterop:\nconst __importDefault = (m) => m?.__esModule ? m : { default: m };\nconst fs_1 = __importDefault(require('fs'));\nconst fs = fs_1.default;"
        }
    },
    {
        "id": "ts_025",
        "language": "TypeScript",
        "topic": "Production Config",
        "subtopic": "const assertions and satisfies",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What are the types of `A`, `B`, and `C`? What's the difference between `as const` and `satisfies`?",
        "code": "const config1 = { port: 3000, env: 'production' };\ntype A = typeof config1.env;\n\nconst config2 = { port: 3000, env: 'production' } as const;\ntype B = typeof config2.env;\n\nconst config3 = { port: 3000, env: 'production' } satisfies { port: number; env: string };\ntype C = typeof config3.env;",
        "answer": {
            "result": "A = string\nB = 'production' (literal, readonly)\nC = 'production' (literal, mutable)",
            "explanation": "Without `as const`: TS widens 'production' to string. `as const`: all values become readonly literal types. `satisfies`: validates the object matches a type WITHOUT widening the inferred type — config3.env is still 'production' (literal) but config3 is mutable. Key: `as const` = readonly literals; `satisfies` = type-check without annotation widening."
        }
    },
    {
        "id": "ts_026",
        "language": "TypeScript",
        "topic": "Production Config",
        "subtopic": "declaration files",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are `.d.ts` declaration files? When do you write one manually vs. letting `tsc` generate it? What is `@types/` on npm?",
        "task": "Write a minimal `.d.ts` file for a JS module `math-utils.js` that exports `add(a, b)` and a constant `PI`.",
        "answer": {
            "key_points": [
                ".d.ts files describe the shape of JS code to TypeScript — no implementation, types only.",
                "tsc generates them automatically with `declaration: true` in tsconfig for library authors.",
                "Write manually when typing a JS library that has no types (or to extend existing types).",
                "@types/ packages on npm are community-maintained declaration files for popular JS libraries.",
                "TypeScript checks @types/ automatically — no import needed."
            ],
            "example_solution": "// math-utils.d.ts\nexport declare function add(a: number, b: number): number;\nexport declare const PI: number;"
        }
    },
    {
        "id": "ts_027",
        "language": "TypeScript",
        "topic": "Production Config",
        "subtopic": "moduleResolution",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is `moduleResolution: 'bundler'` and how does it differ from `'node'` and `'node16'`? Why does it matter for modern TS projects?",
        "task": "Show a tsconfig snippet for a modern Vite/ESM project and explain each relevant setting.",
        "answer": {
            "key_points": [
                "node: classic CJS resolution — looks for index.js, follows require() rules.",
                "node16/nodenext: strict ESM resolution — requires .js extensions in imports. Matches Node's actual ESM behavior.",
                "bundler: resolves like a bundler (Vite, esbuild) — no extension requirements, supports exports map. Doesn't enforce Node's strict ESM rules.",
                "Wrong moduleResolution causes 'Cannot find module' errors even when files exist."
            ],
            "example_solution": "{\n  \"compilerOptions\": {\n    \"target\": \"ESNext\",\n    \"module\": \"ESNext\",\n    \"moduleResolution\": \"bundler\",\n    \"strict\": true,\n    \"noEmit\": true,\n    \"allowImportingTsExtensions\": true\n  }\n}"
        }
    },
    {
        "id": "ts_028",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "function type variance",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "Which assignments are valid and which error? Explain why in terms of covariance and contravariance.",
        "code": "type Animal = { name: string };\ntype Dog = Animal & { breed: string };\n\nlet animalFn: (a: Animal) => Dog;\nlet dogFn: (d: Dog) => Animal;\n\nanimalFn = dogFn;  // A\ndogFn = animalFn;  // B",
        "answer": {
            "result": "A errors. B is valid.",
            "explanation": "Function parameters are contravariant: a function that accepts a wider type (Animal) is assignable where a narrower type (Dog) is expected — not vice versa. Return types are covariant: returning a narrower type (Dog) is assignable where a wider type (Animal) is expected. B: animalFn takes Animal (OK contravariance) and returns Dog (OK covariance). A: dogFn takes Dog (narrower input — unsafe)."
        }
    },
    {
        "id": "ts_029",
        "language": "TypeScript",
        "topic": "Type System",
        "subtopic": "keyof and typeof",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What are the types of `A`, `B`, `C`, and `D`?",
        "code": "const config = { host: 'localhost', port: 3000, debug: true };\n\ntype A = typeof config;\ntype B = keyof typeof config;\ntype C = typeof config[keyof typeof config];\n\nfunction getValue<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }\ntype D = ReturnType<typeof getValue<typeof config, 'port'>>;",
        "answer": {
            "result": "A = { host: string; port: number; debug: boolean }\nB = 'host' | 'port' | 'debug'\nC = string | number | boolean\nD = number",
            "explanation": "`typeof` in type position extracts the TypeScript type of a value. `keyof` gets the union of all keys. `T[K]` is an indexed access type — with K as the full keyof union, it gives the union of all value types. D uses ReturnType with specific type arguments to resolve the return type for that exact call signature."
        }
    },
    {
        "id": "ts_030",
        "language": "TypeScript",
        "topic": "Advanced Patterns",
        "subtopic": "decorators",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What are TypeScript decorators? What's the difference between the legacy decorator spec (experimentalDecorators) and the TC39 Stage 3 decorators? Write a practical example of a class method decorator.",
        "task": "Write a `@memoize` method decorator that caches the result of a method call by its first argument.",
        "answer": {
            "key_points": [
                "Decorators are functions that run at class definition time, not instance creation time.",
                "experimentalDecorators (legacy): TypeScript's own spec, widely used by Angular/NestJS. Parameters: (target, propertyKey, descriptor).",
                "TC39 Stage 3 (TS 5.0+): official JS spec. Parameters changed — `context` object replaces the three-arg signature.",
                "Class, method, property, accessor, and parameter decorators each have different signatures.",
                "Decorators are metadata — they can wrap implementations, add methods, modify descriptor."
            ],
            "example_solution": "function memoize(_target: any, _key: string, descriptor: PropertyDescriptor) {\n  const original = descriptor.value;\n  const cache = new Map();\n  descriptor.value = function (...args: any[]) {\n    const key = args[0];\n    if (cache.has(key)) return cache.get(key);\n    const result = original.apply(this, args);\n    cache.set(key, result);\n    return result;\n  };\n  return descriptor;\n}\n\nclass Calculator {\n  @memoize\n  expensiveCompute(n: number): number { return n * n; }\n}"
        }
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PYTHON (py_001 – py_025)
    # ══════════════════════════════════════════════════════════════════════════

    {
        "id": "py_001",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "annotations vs runtime enforcement",
        "difficulty": "beginner",
        "format": "explain",
        "prompt": "Python type hints are not enforced at runtime. What are they for, and how do tools like mypy use them?",
        "task": "Write a function `divide(a: float, b: float) -> float` and show what mypy catches vs. what Python doesn't.",
        "answer": {
            "key_points": [
                "Type hints are metadata — Python ignores them at runtime (`x: int = 'hello'` runs fine).",
                "mypy, pyright, pyright are static checkers that read annotations and flag mismatches before running.",
                "Annotations live in `__annotations__` dict and are readable via `typing.get_type_hints()`.",
                "`from __future__ import annotations` defers evaluation — annotations become strings (PEP 563).",
                "Libraries like Pydantic and dataclasses DO use annotations at runtime for validation/generation."
            ],
            "example_solution": "def divide(a: float, b: float) -> float:\n    return a / b\n\ndivide('10', 2)  # mypy error: Argument 1 has type 'str'; expected 'float'\n                 # Python: runs fine — str / int raises TypeError at runtime instead"
        }
    },
    {
        "id": "py_002",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "TypeVar and Generic classes",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What is `TypeVar` and how do you use it to write a generic function? How does it differ from using `Any`?",
        "task": "Write a generic `first(items: list[T]) -> T` function that returns the first element, preserving the element type.",
        "answer": {
            "key_points": [
                "TypeVar creates a type variable — a placeholder that gets bound to a concrete type at each call site.",
                "Unlike Any, TypeVar preserves the relationship between inputs and outputs (T in → T out).",
                "TypeVar can have bounds: `T = TypeVar('T', bound=Comparable)` — T must be a subtype of Comparable.",
                "TypeVar can have constraints: `T = TypeVar('T', int, str)` — T can only be int or str.",
                "Python 3.12+ syntax: `def first[T](items: list[T]) -> T` (no TypeVar declaration needed)."
            ],
            "example_solution": "from typing import TypeVar\nT = TypeVar('T')\n\ndef first(items: list[T]) -> T:\n    return items[0]\n\nresult = first([1, 2, 3])   # mypy infers result: int\nresult2 = first(['a', 'b']) # mypy infers result2: str"
        }
    },
    {
        "id": "py_003",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "Protocol vs ABC",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What is `typing.Protocol` and how does it enable structural subtyping (duck typing) with static analysis? How does it differ from `abc.ABC`?",
        "task": "Write a `Drawable` Protocol and a function `render(d: Drawable)` that works for any class with a `draw()` method, without inheritance.",
        "answer": {
            "key_points": [
                "Protocol defines a structural interface — any class with the required methods satisfies it, no explicit inheritance needed.",
                "ABC requires explicit inheritance (`class MyClass(MyABC)`). Protocol works without it.",
                "Protocol = structural subtyping (duck typing with static checking). ABC = nominal subtyping.",
                "Use Protocol for third-party types you can't modify. Use ABC when you want to enforce inheritance.",
                "`@runtime_checkable` makes Protocol work with isinstance() at runtime."
            ],
            "example_solution": "from typing import Protocol\n\nclass Drawable(Protocol):\n    def draw(self) -> None: ...\n\ndef render(d: Drawable) -> None:\n    d.draw()\n\nclass Circle:  # no inheritance from Drawable!\n    def draw(self) -> None:\n        print('drawing circle')\n\nrender(Circle())  # mypy: OK — Circle satisfies Drawable structurally"
        }
    },
    {
        "id": "py_004",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "dataclasses",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does `@dataclass` generate for this class? What's the difference between `field(default_factory=...)` and a plain default?",
        "code": "from dataclasses import dataclass, field\n\n@dataclass\nclass Config:\n    host: str = 'localhost'\n    port: int = 8080\n    tags: list[str] = field(default_factory=list)\n    _secret: str = field(default='', repr=False, compare=False)",
        "answer": {
            "result": "__init__, __repr__, __eq__ are auto-generated",
            "explanation": "@dataclass generates: `__init__` (with all fields as params with defaults), `__repr__` (shows field values, skipping repr=False), `__eq__` (compares all fields except compare=False). `field(default_factory=list)` creates a NEW list per instance — a plain `tags: list = []` would share the same list across all instances (classic mutable default bug). `repr=False` hides _secret from repr; `compare=False` excludes it from __eq__."
        }
    },
    {
        "id": "py_005",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "TypedDict vs NamedTuple",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are `TypedDict` and `NamedTuple`? When would you choose each over a `dataclass`?",
        "task": "Write a `UserRecord` as a TypedDict and a `Point` as a NamedTuple, and explain what you can and can't do with each.",
        "answer": {
            "key_points": [
                "TypedDict: typed dict at the type level only — instances ARE plain dicts at runtime. No methods. Great for JSON payloads.",
                "NamedTuple: typed tuple subclass — immutable, indexable by position AND name, iterable. Has __slots__ implicitly.",
                "dataclass: full class — mutable by default, supports methods, inheritance, post_init hooks.",
                "Choose TypedDict when receiving/sending dicts (APIs, JSON). NamedTuple when you want lightweight immutable records with positional access.",
                "TypedDict supports `total=False` for optional keys; `Required`/`NotRequired` per-key (3.11+)."
            ],
            "example_solution": "from typing import TypedDict, NamedTuple\n\nclass UserRecord(TypedDict):\n    id: int\n    name: str\n    email: str\n\nclass Point(NamedTuple):\n    x: float\n    y: float\n    z: float = 0.0\n\np = Point(1.0, 2.0)\nprint(p.x, p[0])  # both work\nx, y, z = p       # iterable"
        }
    },
    {
        "id": "py_006",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "Literal and Final",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What do `Literal` and `Final` do? Which of these assignments does mypy flag?",
        "code": "from typing import Literal, Final\n\nMode = Literal['read', 'write', 'append']\n\ndef open_file(path: str, mode: Mode) -> None: ...\n\nopen_file('log.txt', 'read')    # A\nopen_file('log.txt', 'delete')  # B\n\nMAX_SIZE: Final = 1024\nMAX_SIZE = 2048  # C",
        "answer": {
            "result": "B and C are flagged by mypy",
            "explanation": "Literal restricts a value to specific literal values — B passes 'delete' which isn't in the Literal union. Final marks a variable as constant — C tries to reassign it. Both compile and run in Python (no runtime enforcement) but mypy/pyright flag them. Literal is useful for mode strings, status codes, direction enums. Final is for module-level constants."
        }
    },
    {
        "id": "py_007",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "generators",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does this function return, and what's printed? Explain how generator state is preserved.",
        "code": "def countdown(n: int):\n    print('start')\n    while n > 0:\n        yield n\n        n -= 1\n    print('done')\n\ng = countdown(3)\nprint(next(g))\nprint(next(g))\nprint(list(g))",
        "answer": {
            "result": "start\\n3\\n2\\ndone\\n[1]",
            "explanation": "Calling countdown(3) returns a generator object immediately — 'start' is NOT printed yet. `next(g)` resumes until the first yield (prints 'start', yields 3). Second `next(g)` resumes, yields 2. `list(g)` exhausts the rest: yields 1, then 'done' prints, then StopIteration ends it. Generators preserve local state (n) between yields — they're suspended coroutines."
        }
    },
    {
        "id": "py_008",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "yield from and async/await",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What does `yield from` do? How do generators relate to `async/await` under the hood?",
        "task": "Write a `flatten` generator using `yield from`, then explain how `async def` is syntactic sugar over generator protocol.",
        "answer": {
            "key_points": [
                "`yield from iterable` delegates to a sub-generator: yields each item, passes send() and throw() through, and captures the return value.",
                "It's also the mechanism for coroutine chaining before async/await was added (asyncio used generators).",
                "`async def` functions are native coroutines — they use a CO_COROUTINE flag but implement the same __next__/__send__ protocol.",
                "`await expr` is equivalent to `yield from expr` but restricted to awaitable objects.",
                "asyncio's event loop calls .send(None) to advance coroutines, just like calling next() on generators."
            ],
            "example_solution": "def flatten(nested):\n    for item in nested:\n        if isinstance(item, list):\n            yield from flatten(item)\n        else:\n            yield item\n\nlist(flatten([1, [2, [3, 4]], 5]))  # [1, 2, 3, 4, 5]"
        }
    },
    {
        "id": "py_009",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "__slots__",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does `__slots__` do? What changes about memory and attribute access compared to a regular class?",
        "code": "class Regular:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\nclass Slotted:\n    __slots__ = ('x', 'y')\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\nr = Regular(1, 2)\nr.z = 99        # A\n\ns = Slotted(1, 2)\ns.z = 99        # B",
        "answer": {
            "result": "A succeeds. B raises AttributeError.",
            "explanation": "Regular classes store instance attributes in a per-instance `__dict__`. __slots__ replaces __dict__ with fixed-size C-level descriptors — no dict overhead, ~30–50% less memory per instance. The trade-off: you can't add arbitrary attributes (B fails), and you can't use weakrefs without adding '__weakref__' to slots. Best for value objects created in large quantities (points, records, tree nodes)."
        }
    },
    {
        "id": "py_010",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "descriptors",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is the descriptor protocol in Python? How do `property`, `classmethod`, and `staticmethod` use it?",
        "task": "Write a `Validated` descriptor that raises `ValueError` if a value is negative when set on a class attribute.",
        "answer": {
            "key_points": [
                "A descriptor is a class that defines `__get__`, `__set__`, or `__delete__` — controls attribute access on other classes.",
                "Data descriptor: defines __set__ (or __delete__) — takes priority over instance __dict__.",
                "Non-data descriptor: only __get__ — instance __dict__ takes priority.",
                "`property` is a data descriptor. `classmethod`/`staticmethod` are non-data descriptors.",
                "Descriptors enable reusable validation, lazy loading, and type coercion without repeating logic per-attribute."
            ],
            "example_solution": "class Validated:\n    def __set_name__(self, owner, name):\n        self.name = name\n\n    def __get__(self, obj, objtype=None):\n        if obj is None: return self\n        return obj.__dict__.get(self.name)\n\n    def __set__(self, obj, value):\n        if value < 0:\n            raise ValueError(f'{self.name} must be non-negative')\n        obj.__dict__[self.name] = value\n\nclass Circle:\n    radius = Validated()\n\nc = Circle()\nc.radius = 5   # OK\nc.radius = -1  # ValueError: radius must be non-negative"
        }
    },
    {
        "id": "py_011",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "metaclasses",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is a metaclass in Python? What does it let you do that you can't do with regular inheritance?",
        "task": "Write a metaclass `Singleton` that ensures only one instance of any class that uses it is ever created.",
        "answer": {
            "key_points": [
                "A metaclass is the class of a class — it controls class creation, just as a class controls instance creation.",
                "Default metaclass is `type`. `class Foo(metaclass=Meta)` makes Meta responsible for creating Foo.",
                "Metaclass `__new__`/`__init__` run when the class is defined, not when instances are created.",
                "Use cases: ORMs (Django models), API registration, enforcing interface contracts, singleton pattern.",
                "Prefer class decorators or `__init_subclass__` for simpler cases — metaclasses are powerful but complex."
            ],
            "example_solution": "class Singleton(type):\n    _instances = {}\n\n    def __call__(cls, *args, **kwargs):\n        if cls not in cls._instances:\n            cls._instances[cls] = super().__call__(*args, **kwargs)\n        return cls._instances[cls]\n\nclass AppConfig(metaclass=Singleton):\n    pass\n\na = AppConfig()\nb = AppConfig()\nprint(a is b)  # True"
        }
    },
    {
        "id": "py_012",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "GIL",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What is the GIL (Global Interpreter Lock)? When does it matter, and what are the workarounds?",
        "task": "Explain why two CPU-bound threads don't actually run in parallel in CPython, and when you'd use multiprocessing instead.",
        "answer": {
            "key_points": [
                "The GIL is a mutex that allows only ONE thread to execute Python bytecode at a time in CPython.",
                "I/O-bound code: threads still help — GIL is released during I/O waits, so threads overlap waits effectively.",
                "CPU-bound code: threads DON'T help — GIL prevents true parallelism. Two threads take the same time as one.",
                "Workarounds: `multiprocessing` (separate processes, no shared GIL), `concurrent.futures.ProcessPoolExecutor`, C extensions (numpy releases the GIL), or PyPy/GraalPy.",
                "Python 3.13+: experimental no-GIL build (--disable-gil) is in progress."
            ],
            "example_solution": "# CPU-bound: use multiprocessing\nfrom multiprocessing import Pool\n\ndef square(n): return n * n\n\nwith Pool(4) as p:\n    results = p.map(square, range(1000))\n\n# I/O-bound: threading is fine\nimport threading\nthreads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]\nfor t in threads: t.start()"
        }
    },
    {
        "id": "py_013",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "context managers",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What is printed, and what happens if an exception is raised inside the `with` block? Explain `__enter__` and `__exit__`.",
        "code": "class Timer:\n    def __enter__(self):\n        print('start')\n        return self\n\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        print('end')\n        return False  # don't suppress exceptions\n\nwith Timer() as t:\n    print('working')\n    raise ValueError('oops')",
        "answer": {
            "result": "start\\nworking\\nend\\nValueError: oops is raised",
            "explanation": "`__enter__` runs on entry, returns the `as` target. `__exit__` ALWAYS runs on exit (like finally), receiving exception info. Returning False (or None) means 'don't suppress the exception' — it propagates. Return True to suppress. `contextlib.contextmanager` lets you write context managers as generators: code before `yield` is __enter__, after `yield` is __exit__."
        }
    },
    {
        "id": "py_014",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "decorators and functools.wraps",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What does `@functools.wraps(func)` do and why do you need it? Write a `@timer` decorator and show the difference with and without `wraps`.",
        "task": "Write a `@retry(n)` parameterized decorator that retries a function up to n times on exception.",
        "answer": {
            "key_points": [
                "A decorator replaces the function — without @wraps, the wrapper's `__name__`, `__doc__`, `__module__` shadow the original's.",
                "@functools.wraps(func) copies these attributes from func to the wrapper — introspection tools (help(), pytest, logging) see the right name.",
                "Also preserves `__wrapped__` so you can unwrap the decorator for testing.",
                "Parameterized decorators are functions that return a decorator: `@retry(3)` = `retry(3)(func)`."
            ],
            "example_solution": "import functools, time\n\ndef retry(n: int):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            for attempt in range(n):\n                try:\n                    return func(*args, **kwargs)\n                except Exception as e:\n                    if attempt == n - 1: raise\n                    time.sleep(0.1)\n        return wrapper\n    return decorator\n\n@retry(3)\ndef flaky_request(): ...\n\nprint(flaky_request.__name__)  # 'flaky_request', not 'wrapper'"
        }
    },
    {
        "id": "py_015",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "overload decorator",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is `@typing.overload` and when do you use it? How does it differ from actual function overloading?",
        "task": "Write an `overloaded` version of `process` that accepts `str` → `str` and `int` → `int`, typed correctly.",
        "answer": {
            "key_points": [
                "@overload lets you declare multiple type signatures for a single function — mypy uses them for type narrowing.",
                "Only the overload stubs are type-checked — the actual implementation (without @overload) handles runtime dispatch.",
                "Python has no real function overloading — there's one function, one implementation.",
                "Use when the return type depends on the input type in a way Union can't express.",
                "All @overload variants must come before the real implementation."
            ],
            "example_solution": "from typing import overload\n\n@overload\ndef process(x: str) -> str: ...\n@overload\ndef process(x: int) -> int: ...\n\ndef process(x):\n    if isinstance(x, str):\n        return x.upper()\n    return x * 2\n\nresult: str = process('hello')  # mypy: OK\nresult2: int = process(5)       # mypy: OK\nresult3: str = process(5)       # mypy: error"
        }
    },
    {
        "id": "py_016",
        "language": "Python",
        "topic": "Type Hints",
        "subtopic": "ParamSpec",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is `ParamSpec` (Python 3.10+) and what problem does it solve when typing decorators?",
        "task": "Write a `@logged` decorator that preserves the full type signature of the wrapped function using ParamSpec.",
        "answer": {
            "key_points": [
                "ParamSpec captures the full parameter spec (positional + keyword args) of a callable as a single type variable.",
                "Before ParamSpec, decorators that wrapped functions lost the input signature — mypy saw (*args: Any, **kwargs: Any).",
                "P.args and P.kwargs let you type *args and **kwargs in the wrapper to match the original.",
                "Used together with TypeVar for return type: `Callable[P, T]`.",
                "Python 3.10+; backported via `typing_extensions`."
            ],
            "example_solution": "from typing import Callable, TypeVar\nfrom typing import ParamSpec\nimport functools\n\nP = ParamSpec('P')\nT = TypeVar('T')\n\ndef logged(func: Callable[P, T]) -> Callable[P, T]:\n    @functools.wraps(func)\n    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:\n        print(f'calling {func.__name__}')\n        return func(*args, **kwargs)\n    return wrapper\n\n@logged\ndef add(x: int, y: int) -> int: return x + y\n\nadd(1, 2)       # mypy: OK\nadd('a', 'b')   # mypy: error — signature preserved"
        }
    },
    {
        "id": "py_017",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "classmethod vs staticmethod",
        "difficulty": "beginner",
        "format": "snippet",
        "prompt": "What's the difference between `@classmethod`, `@staticmethod`, and a regular instance method? What does each receive as its first argument?",
        "code": "class MyClass:\n    count = 0\n\n    def instance_method(self):\n        return self\n\n    @classmethod\n    def class_method(cls):\n        return cls\n\n    @staticmethod\n    def static_method():\n        return 42\n\nobj = MyClass()\nobj.instance_method()   # A\nMyClass.class_method()  # B\nMyClass.static_method() # C",
        "answer": {
            "result": "A: receives obj instance. B: receives MyClass. C: receives nothing extra.",
            "explanation": "Instance method: receives the instance as `self` — access/modify instance state. @classmethod: receives the class as `cls` — used for alternative constructors (`cls()`) and class-level state. @staticmethod: no implicit first arg — a regular function namespaced in the class. Use classmethods for factory methods like `Date.from_string('2026-03-18')`, staticmethods for utility functions logically grouped with the class."
        }
    },
    {
        "id": "py_018",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "list comprehension vs generator expression",
        "difficulty": "beginner",
        "format": "snippet",
        "prompt": "What's the difference between these two expressions? When would you choose each?",
        "code": "squares_list = [x**2 for x in range(10)]\nsquares_gen  = (x**2 for x in range(10))\n\nprint(type(squares_list))  # A\nprint(type(squares_gen))   # B\nprint(len(squares_list))   # C\nprint(len(squares_gen))    # D",
        "answer": {
            "result": "A: <class 'list'>\\nB: <class 'generator'>\\nC: 10\\nD: TypeError: object of type 'generator' has no len()",
            "explanation": "List comprehension builds the entire list in memory immediately. Generator expression is lazy — it yields values one at a time on demand. Use generators when: processing large sequences you don't need all at once, chaining transformations (sum/any/all/next consume lazily), or feeding another iterator. Use lists when: you need random access, len(), or to iterate multiple times."
        }
    },
    {
        "id": "py_019",
        "language": "Python",
        "topic": "Production",
        "subtopic": "__init__.py and __all__",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What is `__init__.py` for? What does `__all__` control, and what happens to names not in `__all__` when someone does `from mypackage import *`?",
        "task": "Show a package structure where `__init__.py` re-exports selected symbols and `__all__` limits star imports.",
        "answer": {
            "key_points": [
                "`__init__.py` marks a directory as a Python package and runs when the package is imported.",
                "It can re-export symbols from submodules to create a clean public API.",
                "`__all__` = list of names exported by `from package import *`. Names NOT in __all__ are still importable directly.",
                "Without __all__, `import *` exports everything that doesn't start with underscore.",
                "Best practice: explicit `__all__` in every public module."
            ],
            "example_solution": "# mypackage/__init__.py\nfrom .models import User, Order\nfrom .utils import format_date\n\n__all__ = ['User', 'Order', 'format_date']\n\n# _internal is importable as mypackage._internal but NOT via import *\n\n# User code:\nfrom mypackage import User        # direct import — always works\nfrom mypackage import *           # only User, Order, format_date"
        }
    },
    {
        "id": "py_020",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "walrus operator",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does the walrus operator `:=` do? What does this code print?",
        "code": "data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n\nif (n := len(data)) > 5:\n    print(f'Long list: {n} items')\n\nresults = [y for x in data if (y := x**2) > 25]\nprint(results)",
        "answer": {
            "result": "Long list: 10 items\\n[36, 49, 64, 81, 100]",
            "explanation": "The walrus operator `:=` assigns AND returns a value in an expression. In the if-statement, `n` is assigned len(data) AND tested in the same line — no double call. In the comprehension, `y = x**2` is computed once and reused in the filter condition and the output — efficient and avoids recomputing. Useful in while loops: `while chunk := f.read(8192): process(chunk)`."
        }
    },
    {
        "id": "py_021",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "structural pattern matching",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does this match/case block print for each input? (Python 3.10+)",
        "code": "def classify(command):\n    match command:\n        case {'action': 'move', 'direction': d}:\n            return f'Moving {d}'\n        case {'action': 'attack', 'target': t, 'damage': dmg}:\n            return f'Attacking {t} for {dmg}'\n        case {'action': action}:\n            return f'Unknown action: {action}'\n        case _:\n            return 'Invalid command'\n\nprint(classify({'action': 'move', 'direction': 'north'}))\nprint(classify({'action': 'attack', 'target': 'dragon', 'damage': 50}))\nprint(classify({'action': 'flee'}))\nprint(classify('help'))",
        "answer": {
            "result": "Moving north\\nAttacking dragon for 50\\nUnknown action: flee\\nInvalid command",
            "explanation": "match/case does structural pattern matching — patterns can be literals, sequences, mappings, classes, or wildcards. Mapping patterns `{'key': var}` match dicts containing at least those keys; captured variables (d, t, dmg) bind the values. The `case _:` wildcard catches everything. Unlike switch statements, patterns are declarative — no break needed, first match wins."
        }
    },
    {
        "id": "py_022",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "abstractmethod",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What happens at each line A–D?",
        "code": "from abc import ABC, abstractmethod\n\nclass Animal(ABC):\n    @abstractmethod\n    def speak(self) -> str: ...\n\n    def describe(self) -> str:\n        return f'I say: {self.speak()}'\n\nclass Dog(Animal):\n    def speak(self) -> str:\n        return 'woof'\n\na = Animal()   # A\nd = Dog()      # B\nprint(d.describe())  # C\n\nclass Cat(Animal): pass\nc = Cat()      # D",
        "answer": {
            "result": "A: TypeError (can't instantiate abstract class)\\nB: OK\\nC: 'I say: woof'\\nD: TypeError (Cat doesn't implement speak)",
            "explanation": "ABCs with @abstractmethod cannot be instantiated directly (A). Subclasses must implement ALL abstract methods to be instantiatable (D fails). Dog implements speak, so it's fine (B). Concrete methods on the ABC (describe) can call abstract methods — they'll resolve to the subclass implementation at runtime via polymorphism (C)."
        }
    },
    {
        "id": "py_023",
        "language": "Python",
        "topic": "Production",
        "subtopic": "virtual environments and packaging",
        "difficulty": "beginner",
        "format": "explain",
        "prompt": "Why do Python projects need virtual environments? What's in a `pyproject.toml`, and how does it replace `setup.py`?",
        "task": "Show a minimal `pyproject.toml` for a package named `mylib` using hatchling as the build backend.",
        "answer": {
            "key_points": [
                "Virtual environments isolate per-project dependencies — no conflicts between projects needing different library versions.",
                "Without venvs, pip installs globally — one project's upgrade can break another.",
                "`pyproject.toml` (PEP 517/518) is the modern unified config replacing setup.py + setup.cfg + MANIFEST.in.",
                "It declares: build backend (hatchling/flit/setuptools), package metadata, dependencies, tool configs (black, mypy, pytest).",
                "`pip install -e .` in a venv installs the package in editable mode for development."
            ],
            "example_solution": "[build-system]\nrequires = ['hatchling']\nbuild-backend = 'hatchling.build'\n\n[project]\nname = 'mylib'\nversion = '0.1.0'\nrequires-python = '>=3.11'\ndependencies = ['httpx>=0.27', 'pydantic>=2']\n\n[project.optional-dependencies]\ndev = ['pytest', 'mypy']"
        }
    },
    {
        "id": "py_024",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "mutable default arguments",
        "difficulty": "beginner",
        "format": "snippet",
        "prompt": "What does this print? Why is this a classic Python gotcha?",
        "code": "def append_to(item, lst=[]):\n    lst.append(item)\n    return lst\n\nprint(append_to(1))\nprint(append_to(2))\nprint(append_to(3))\nprint(append_to(4, []))",
        "answer": {
            "result": "[1]\\n[1, 2]\\n[1, 2, 3]\\n[4]",
            "explanation": "Default argument values are evaluated ONCE at function definition time, not on each call. The list `[]` is created once and reused — each call without explicit `lst` mutates the same list object. This is a common bug. Fix: use `None` as the default and create a new list inside: `def append_to(item, lst=None): lst = lst if lst is not None else []`. The last call passes a fresh `[]` explicitly, so it's independent."
        }
    },
    {
        "id": "py_025",
        "language": "Python",
        "topic": "Runtime",
        "subtopic": "asyncio event loop",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "How does Python's asyncio event loop work? What's the difference between `async def`, `await`, `asyncio.gather`, and `asyncio.create_task`?",
        "task": "Show a minimal example fetching two URLs concurrently with `asyncio.gather` and explain the execution order.",
        "answer": {
            "key_points": [
                "asyncio runs on a single thread — the event loop drives coroutines by calling .send(None) when they're ready.",
                "`async def` defines a coroutine — calling it returns a coroutine object, doesn't run it.",
                "`await expr` suspends the current coroutine and yields control to the event loop until expr is done.",
                "`asyncio.gather(*coros)` schedules all coroutines concurrently and waits for all to finish.",
                "`asyncio.create_task(coro)` schedules a coroutine as a Task immediately — it starts running even before you await it. gather wraps in tasks internally."
            ],
            "example_solution": "import asyncio, httpx\n\nasync def fetch(url: str) -> str:\n    async with httpx.AsyncClient() as client:\n        r = await client.get(url)\n        return r.text\n\nasync def main():\n    # Both requests start concurrently — total time ≈ max(t1, t2), not t1+t2\n    results = await asyncio.gather(\n        fetch('https://api.example.com/a'),\n        fetch('https://api.example.com/b'),\n    )\n    print(results)\n\nasyncio.run(main())"
        }
    },

    # ══════════════════════════════════════════════════════════════════════════
    # C# (cs_001 – cs_025)
    # ══════════════════════════════════════════════════════════════════════════

    {
        "id": "cs_001",
        "language": "C#",
        "topic": "Type System",
        "subtopic": "value types vs reference types",
        "difficulty": "beginner",
        "format": "snippet",
        "prompt": "What is printed? Explain the difference between structs (value types) and classes (reference types).",
        "code": "struct Point { public int X, Y; }\nclass Box { public int Value; }\n\nPoint a = new Point { X = 1, Y = 2 };\nPoint b = a;\nb.X = 99;\nConsole.WriteLine(a.X);  // A\n\nBox c = new Box { Value = 1 };\nBox d = c;\nd.Value = 99;\nConsole.WriteLine(c.Value);  // B",
        "answer": {
            "result": "A: 1\\nB: 99",
            "explanation": "Structs are value types — assignment copies the entire struct. `b` is an independent copy; mutating b.X doesn't affect a. Classes are reference types — assignment copies the reference. `d` points to the same object as `c`; mutating d.Value changes what c sees. Stack vs. heap: structs typically live on the stack (or inline in arrays), classes on the heap."
        }
    },
    {
        "id": "cs_002",
        "language": "C#",
        "topic": "Type System",
        "subtopic": "boxing and unboxing",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What happens at each line? What are the performance implications?",
        "code": "int x = 42;\nobject obj = x;        // A — boxing\nint y = (int)obj;      // B — unboxing\n\nvar list = new System.Collections.ArrayList();\nlist.Add(1);           // C — implicit boxing\nint z = (int)list[0];  // D — unboxing",
        "answer": {
            "result": "All lines succeed. y = 42, z = 1.",
            "explanation": "Boxing (A, C): a value type is wrapped in a heap-allocated object — allocation + copy. Unboxing (B, D): extracts the value back — type check + copy. Costs: GC pressure from heap allocation, CPU for type check, cache misses. Avoid in hot paths. Fix: use generic collections `List<int>` instead of ArrayList — no boxing because T is known at compile time. Boxing commonly hides in: ArrayList, Hashtable, non-generic interfaces, string.Format (pre-C#6), enums in dictionary keys."
        }
    },
    {
        "id": "cs_003",
        "language": "C#",
        "topic": "Generics",
        "subtopic": "constraints",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are generic constraints in C#? What does each `where T :` clause mean?",
        "task": "Write a generic `Max<T>` function that returns the larger of two values, constrained to types that implement `IComparable<T>`.",
        "answer": {
            "key_points": [
                "`where T : class` — T must be a reference type.",
                "`where T : struct` — T must be a value type (non-nullable).",
                "`where T : new()` — T must have a parameterless constructor.",
                "`where T : IComparable<T>` — T must implement that interface.",
                "`where T : SomeBaseClass` — T must inherit from SomeBaseClass.",
                "Constraints enable calling methods on T that wouldn't be available on unconstrained generics."
            ],
            "example_solution": "T Max<T>(T a, T b) where T : IComparable<T>\n    => a.CompareTo(b) >= 0 ? a : b;\n\nConsole.WriteLine(Max(3, 7));       // 7\nConsole.WriteLine(Max(\"apple\", \"banana\")); // banana"
        }
    },
    {
        "id": "cs_004",
        "language": "C#",
        "topic": "LINQ",
        "subtopic": "query operators",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does this LINQ query return? Rewrite it in method syntax.",
        "code": "var numbers = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };\n\nvar result = from n in numbers\n             where n % 2 == 0\n             orderby n descending\n             select n * n;\n\nConsole.WriteLine(string.Join(\", \", result));",
        "answer": {
            "result": "100, 64, 36, 16, 4",
            "explanation": "Filters even numbers (2,4,6,8,10), orders descending (10,8,6,4,2), projects to squares (100,64,36,16,4). Method syntax equivalent:\n```csharp\nvar result = numbers\n    .Where(n => n % 2 == 0)\n    .OrderByDescending(n => n)\n    .Select(n => n * n);\n```\nBoth compile to the same IL. Query syntax is syntactic sugar — the compiler translates it to method calls. LINQ is lazy (deferred execution) — result is an IEnumerable<int> that evaluates when iterated."
        }
    },
    {
        "id": "cs_005",
        "language": "C#",
        "topic": "Async",
        "subtopic": "Task vs ValueTask",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What's the difference between `Task<T>` and `ValueTask<T>`? When should you return each from an async method?",
        "task": "Show a cache-backed async method that benefits from ValueTask when the result is cached (synchronous path).",
        "answer": {
            "key_points": [
                "Task<T>: always allocates a heap object. Fine for most async methods. Cacheable and awaitable multiple times.",
                "ValueTask<T>: a struct — zero allocation when the result is available synchronously (returns the value directly). Allocates when truly async.",
                "ValueTask is NOT safely awaited multiple times (unless converted to Task with .AsTask()).",
                "Use ValueTask for hot paths where the method frequently returns synchronously (cache hits, pooled connections).",
                "Don't default to ValueTask — the overhead of checking synchronous vs async adds complexity for no gain in purely async code."
            ],
            "example_solution": "private readonly Dictionary<int, User> _cache = new();\n\npublic ValueTask<User> GetUserAsync(int id)\n{\n    if (_cache.TryGetValue(id, out var user))\n        return ValueTask.FromResult(user); // no allocation — sync path\n\n    return new ValueTask<User>(FetchFromDbAsync(id)); // wraps Task\n}\n\nprivate async Task<User> FetchFromDbAsync(int id) { ... }"
        }
    },
    {
        "id": "cs_006",
        "language": "C#",
        "topic": "Resource Management",
        "subtopic": "IDisposable and using",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What pattern does this implement? What happens if an exception is thrown inside the using block?",
        "code": "using var connection = new SqlConnection(connectionString);\nawait connection.OpenAsync();\nvar result = await connection.QueryAsync<User>(\"SELECT * FROM Users\");\n// connection.Dispose() called here automatically",
        "answer": {
            "result": "Dispose() is always called — even if an exception is thrown.",
            "explanation": "`using var x = ...` is a C# 8+ declaration-style using statement. It calls `x.Dispose()` at the end of the enclosing scope (like a finally block). `using (var x = ...) { }` is the older block form. Both guarantee Dispose even on exception. For async cleanup, implement `IAsyncDisposable` and use `await using`. `IDisposable` should release: file handles, network connections, DB connections, unmanaged memory. The finalizer is a fallback — never rely on it for timely cleanup."
        }
    },
    {
        "id": "cs_007",
        "language": "C#",
        "topic": "Delegates and Events",
        "subtopic": "Func, Action, and events",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are delegates, `Func<>`, `Action<>`, and `event`? When would you use `event` over a plain delegate field?",
        "task": "Write a `Button` class with a `Clicked` event that multiple subscribers can handle, and show subscription and invocation.",
        "answer": {
            "key_points": [
                "Delegate: a type-safe function pointer. `delegate int Transform(int x)`.",
                "Func<T, TResult>: built-in generic delegate for functions that return a value.",
                "Action<T>: built-in generic delegate for void functions.",
                "`event`: wrapper over a delegate field — restricts external code to only += and -= (can't assign or invoke from outside).",
                "Without `event`, any external code could reset all subscribers (`button.Clicked = null`) or invoke it directly."
            ],
            "example_solution": "class Button\n{\n    public event EventHandler? Clicked;\n\n    public void Click()\n        => Clicked?.Invoke(this, EventArgs.Empty);\n}\n\nvar btn = new Button();\nbtn.Clicked += (s, e) => Console.WriteLine('First handler');\nbtn.Clicked += (s, e) => Console.WriteLine('Second handler');\nbtn.Click();\n// Output: First handler\\nSecond handler"
        }
    },
    {
        "id": "cs_008",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "extension methods",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are extension methods? How does C# resolve them, and what are their limitations?",
        "task": "Write an extension method `IsNullOrWhiteSpace` on `string` and a `ToSentenceCase` extension, and show usage.",
        "answer": {
            "key_points": [
                "Extension methods are static methods in a static class with `this T` as the first parameter — called as if they're instance methods.",
                "They're syntactic sugar — `str.IsNullOrWhiteSpace()` compiles to `StringExtensions.IsNullOrWhiteSpace(str)`.",
                "Can't access private members — they're not truly part of the class.",
                "Resolved at compile time based on the type of the first argument and imported namespaces.",
                "Instance methods always win over extension methods if a conflict exists.",
                "LINQ (Where, Select, etc.) are all extension methods on IEnumerable<T>."
            ],
            "example_solution": "public static class StringExtensions\n{\n    public static bool IsNullOrWhiteSpace(this string? s)\n        => string.IsNullOrWhiteSpace(s);\n\n    public static string ToSentenceCase(this string s)\n        => string.IsNullOrEmpty(s) ? s\n           : char.ToUpper(s[0]) + s[1..].ToLower();\n}\n\nstring name = 'hello world';\nConsole.WriteLine(name.ToSentenceCase()); // Hello world"
        }
    },
    {
        "id": "cs_009",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "pattern matching",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does each switch arm return for the given shapes? Explain each pattern type used.",
        "code": "record Circle(double Radius);\nrecord Rectangle(double Width, double Height);\nrecord Triangle(double Base, double Height);\n\ndouble Area(object shape) => shape switch\n{\n    Circle { Radius: var r }        => Math.PI * r * r,\n    Rectangle { Width: var w,\n                Height: var h }     => w * h,\n    Triangle { Base: var b,\n               Height: var h }      => 0.5 * b * h,\n    null                            => throw new ArgumentNullException(),\n    _                               => throw new NotSupportedException()\n};",
        "answer": {
            "result": "Area(new Circle(5)) ≈ 78.54\nArea(new Rectangle(4, 6)) = 24\nArea(new Triangle(3, 8)) = 12",
            "explanation": "C# switch expressions (C# 8+) with property patterns: `Circle { Radius: var r }` matches if shape is a Circle and captures Radius into r. No explicit type check needed — the pattern does it. `_` is the discard wildcard (default). Records work perfectly here because they generate positional + property-based deconstruction. This replaces long if/else chains with exhaustive, readable pattern matching."
        }
    },
    {
        "id": "cs_010",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "records and init-only setters",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are C# records (C# 9+)? What does `with` do? How do `init`-only properties work?",
        "task": "Define a `Person` record and show how to create a modified copy using `with`, then explain why records are ideal for immutable data.",
        "answer": {
            "key_points": [
                "Records generate: constructor, Deconstruct, ==, !=, GetHashCode, ToString — all based on declared properties.",
                "`with` expression creates a copy with specified properties changed — non-destructive mutation.",
                "`init` setters: settable only during object initialization (in constructors, object initializers, or `with`) — then read-only.",
                "record struct (C# 10): value-type record on the stack — no heap allocation.",
                "Records use value equality by default (comparing property values), unlike classes (reference equality)."
            ],
            "example_solution": "record Person(string Name, int Age);\n\nvar alice = new Person('Alice', 30);\nvar olderAlice = alice with { Age = 31 }; // copy with one change\n\nConsole.WriteLine(alice);        // Person { Name = Alice, Age = 30 }\nConsole.WriteLine(olderAlice);   // Person { Name = Alice, Age = 31 }\nConsole.WriteLine(alice == olderAlice); // False (different Age)\n\n// init-only:\npublic class Config\n{\n    public string Host { get; init; } = 'localhost';\n}\nvar c = new Config { Host = 'prod' }; // OK\nc.Host = 'other'; // Compile error after init"
        }
    },
    {
        "id": "cs_011",
        "language": "C#",
        "topic": "Type System",
        "subtopic": "nullable reference types",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "With `<Nullable>enable</Nullable>`, which lines does the compiler warn about and why?",
        "code": "string name = null;           // A\nstring? maybeName = null;     // B\n\nvoid Greet(string? input)\n{\n    Console.WriteLine(input.Length);   // C\n    if (input != null)\n        Console.WriteLine(input.Length); // D\n}\n\nstring GetName() => null;     // E",
        "answer": {
            "result": "Warnings on A, C, E",
            "explanation": "A: `string` (non-nullable) can't be assigned null — use `string?`. B: `string?` explicitly allows null — OK. C: `input` is nullable — dereferencing without null check is warned (possible NullReferenceException). D: after the null check, the compiler narrows input to non-nullable — safe. E: return type is `string` (non-nullable) but null is returned. Nullable reference types (C# 8+) don't prevent null at runtime — they're static analysis hints, like TypeScript's strictNullChecks."
        }
    },
    {
        "id": "cs_012",
        "language": "C#",
        "topic": "Performance",
        "subtopic": "Span<T> and Memory<T>",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is `Span<T>`? How does it let you slice arrays and strings without allocation? What's `Memory<T>` for?",
        "task": "Write a zero-allocation `SplitFirst` function that returns the part of a string before the first comma using `ReadOnlySpan<char>`.",
        "answer": {
            "key_points": [
                "Span<T> is a ref struct — a window into a contiguous block of memory (array, stack, unmanaged). No heap allocation.",
                "Slicing a Span: `span[1..5]` creates a new Span pointing into the same memory — no copy.",
                "Strings: `str.AsSpan()` gives `ReadOnlySpan<char>` — substring operations without allocating new strings.",
                "Limitation: Span is a ref struct — can't be stored in fields, used in async methods, or boxed.",
                "Memory<T>: heap-allocated wrapper for async scenarios where Span can't be used."
            ],
            "example_solution": "ReadOnlySpan<char> SplitFirst(ReadOnlySpan<char> input)\n{\n    int idx = input.IndexOf(',');\n    return idx >= 0 ? input[..idx] : input;\n}\n\nvar result = SplitFirst(\"hello,world\"); // no string allocation\nConsole.WriteLine(result.ToString());   // \"hello\""
        }
    },
    {
        "id": "cs_013",
        "language": "C#",
        "topic": "Type System",
        "subtopic": "covariance and contravariance",
        "difficulty": "advanced",
        "format": "snippet",
        "prompt": "Which assignments are valid? Explain `out` (covariance) and `in` (contravariance) on generic interfaces.",
        "code": "IEnumerable<string> strings = new List<string>();\nIEnumerable<object> objects = strings;          // A\n\nAction<object> actObj = (o) => Console.WriteLine(o);\nAction<string> actStr = actObj;                  // B\n\nIComparer<object> cmpObj = Comparer<object>.Default;\nIComparer<string> cmpStr = cmpObj;               // C",
        "answer": {
            "result": "A: valid (covariance). B: valid (contravariance). C: valid (contravariance).",
            "explanation": "IEnumerable<out T>: `out` = covariant — T only appears in output positions. A string IS an object, so IEnumerable<string> is safely assignable to IEnumerable<object> (you only read from it). Action<in T>: `in` = contravariant — T only appears in input positions. An Action<object> can handle any string (it handles objects), so it's safe as Action<string>. IComparer<in T>: same — if you can compare objects, you can compare strings. This mirrors TypeScript's covariance/contravariance rules."
        }
    },
    {
        "id": "cs_014",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "yield return and iterators",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does this method return, and what is printed? Explain the execution model.",
        "code": "IEnumerable<int> Fibonacci()\n{\n    Console.WriteLine('starting');\n    int a = 0, b = 1;\n    while (true)\n    {\n        yield return a;\n        (a, b) = (b, a + b);\n    }\n}\n\nvar fibs = Fibonacci();\nConsole.WriteLine('got enumerator');\nforeach (var n in fibs.Take(5))\n    Console.WriteLine(n);",
        "answer": {
            "result": "got enumerator\\nstarting\\n0\\n1\\n1\\n2\\n3",
            "explanation": "Fibonacci() returns an IEnumerable<int> immediately — 'starting' is NOT printed yet (lazy). 'got enumerator' prints next. On first MoveNext() (first foreach iteration), the method runs until the first `yield return 0`, printing 'starting' and returning 0. Each subsequent MoveNext() resumes from after the yield. `Take(5)` stops after 5 values. The method state (a, b) is preserved between yields. `yield return` is the C# equivalent of Python's `yield`."
        }
    },
    {
        "id": "cs_015",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "ref, out, and in parameters",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What are `ref`, `out`, and `in` parameter modifiers? How do they differ, and when would you use each?",
        "task": "Show examples of `TryParse` (out), a swap function (ref), and a readonly large-struct parameter (in).",
        "answer": {
            "key_points": [
                "`ref`: pass by reference — caller must initialize. Method can read AND write. Two-way alias.",
                "`out`: pass by reference — caller need not initialize. Method MUST write before returning. Used for multiple return values.",
                "`in`: pass by reference — caller must initialize. Method can only READ. For large structs to avoid copying without allowing mutation.",
                "All three avoid copying value types — useful for large structs (Matrix4x4, etc.).",
                "`out` is idiomatic for Try-patterns (TryParse, TryGetValue)."
            ],
            "example_solution": "// out — TryParse pattern\nif (int.TryParse('42', out int value))\n    Console.WriteLine(value);\n\n// ref — swap (or use tuple)\nvoid Swap<T>(ref T a, ref T b) { (a, b) = (b, a); }\nint x = 1, y = 2;\nSwap(ref x, ref y); // x=2, y=1\n\n// in — avoid copying large struct\nvoid Process(in Matrix4x4 m) { /* read-only access */ }"
        }
    },
    {
        "id": "cs_016",
        "language": "C#",
        "topic": "Type System",
        "subtopic": "abstract class vs interface",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "When would you use an `abstract class` vs an `interface` in C#? What changed in C# 8 with default interface methods?",
        "task": "Show a scenario where abstract class is the right choice over interface, and vice versa.",
        "answer": {
            "key_points": [
                "Interface: defines a contract — pure capability. No state. A class can implement many interfaces.",
                "Abstract class: partial implementation — can have state, constructors, concrete methods. Only single inheritance.",
                "Use abstract class when subclasses share code/state and represent an 'is-a' relationship (Animal → Dog).",
                "Use interface for 'can-do' capabilities that cut across hierarchies (ISerializable, IDisposable).",
                "C# 8+ default interface methods: interfaces can now have default implementations — reduces breaking changes in library evolution, but use sparingly (can't access state)."
            ],
            "example_solution": "// Abstract class: shared state + template method pattern\nabstract class Report\n{\n    protected string Title;\n    public void Generate() { Header(); Body(); Footer(); } // template\n    protected abstract void Body();\n    protected virtual void Header() => Console.WriteLine(Title);\n    protected virtual void Footer() => Console.WriteLine('---');\n}\n\n// Interface: capability contract across hierarchies\ninterface IExportable { byte[] Export(); }\nclass PdfReport : Report, IExportable { ... }\nclass CsvReport : Report, IExportable { ... }"
        }
    },
    {
        "id": "cs_017",
        "language": "C#",
        "topic": "Async",
        "subtopic": "async/await and CancellationToken",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What is `CancellationToken` and how should you use it in async methods? What's the difference between cooperative cancellation and aborting a thread?",
        "task": "Write an async `DownloadFileAsync` method that accepts a CancellationToken and checks it periodically.",
        "answer": {
            "key_points": [
                "CancellationToken is cooperative — code must check `token.IsCancellationRequested` or call `token.ThrowIfCancellationRequested()`.",
                "Cancelled operations throw `OperationCanceledException` — callers should catch this specifically.",
                "Pass tokens through the entire async call chain — every async method should accept one.",
                "Unlike thread abort (which was removed in .NET 5+), cancellation is graceful and safe.",
                "`CancellationTokenSource.Cancel()` triggers the token; `CancelAfter(TimeSpan)` for timeouts."
            ],
            "example_solution": "async Task DownloadFileAsync(string url, string path, CancellationToken ct)\n{\n    using var client = new HttpClient();\n    using var response = await client.GetAsync(url, ct);\n    response.EnsureSuccessStatusCode();\n\n    await using var fs = File.Create(path);\n    var buffer = new byte[8192];\n    using var stream = await response.Content.ReadAsStreamAsync(ct);\n\n    int read;\n    while ((read = await stream.ReadAsync(buffer, ct)) > 0)\n    {\n        ct.ThrowIfCancellationRequested();\n        await fs.WriteAsync(buffer.AsMemory(0, read), ct);\n    }\n}"
        }
    },
    {
        "id": "cs_018",
        "language": "C#",
        "topic": "Performance",
        "subtopic": "string vs StringBuilder",
        "difficulty": "beginner",
        "format": "explain",
        "prompt": "Why is concatenating strings in a loop inefficient in C#? When should you use `StringBuilder`, and when is it unnecessary?",
        "task": "Show the performance difference between string concatenation in a loop vs. StringBuilder, and explain the O(n²) problem.",
        "answer": {
            "key_points": [
                "Strings are immutable — every `+` creates a new string object and copies both halves.",
                "In a loop with n strings, concatenation is O(n²) in time and creates n intermediate strings.",
                "StringBuilder uses a mutable char buffer — Append() is O(1) amortized (doubles capacity when full).",
                "Don't use StringBuilder for 2-3 concatenations — the overhead isn't worth it. Use interpolation or +.",
                "`string.Join(sep, collection)` and `string.Concat` are optimized for known collections — prefer those over StringBuilder when you have a collection."
            ],
            "example_solution": "// Bad — O(n²), n allocations:\nstring result = '';\nfor (int i = 0; i < 10000; i++)\n    result += i.ToString(); // new string each iteration\n\n// Good — O(n) amortized:\nvar sb = new StringBuilder();\nfor (int i = 0; i < 10000; i++)\n    sb.Append(i);\nstring result2 = sb.ToString(); // one final string"
        }
    },
    {
        "id": "cs_019",
        "language": "C#",
        "topic": "LINQ",
        "subtopic": "deferred execution",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What is printed, and in what order? Explain LINQ deferred execution.",
        "code": "var numbers = new List<int> { 1, 2, 3 };\n\nvar query = numbers.Where(n => {\n    Console.WriteLine($'checking {n}');\n    return n > 1;\n});\n\nConsole.WriteLine('before iteration');\nnumbers.Add(4);\n\nforeach (var n in query)\n    Console.WriteLine($'got {n}');",
        "answer": {
            "result": "before iteration\\nchecking 1\\nchecking 2\\ngot 2\\nchecking 3\\ngot 3\\nchecking 4\\ngot 4",
            "explanation": "LINQ is lazy by default — `.Where()` returns an IEnumerable<int> but runs NO code yet. 'before iteration' prints, then 4 is added. When foreach starts, LINQ enumerates the list AS IT IS NOW (includes 4). Each element is checked on demand as foreach calls MoveNext(). Force immediate execution with .ToList() or .ToArray(). Common bug: mutating the source between query creation and iteration, or assuming query result is fixed."
        }
    },
    {
        "id": "cs_020",
        "language": "C#",
        "topic": "Concurrency",
        "subtopic": "lock and thread safety",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "What does `lock` do in C#? What are its limitations and when would you use `SemaphoreSlim` instead?",
        "task": "Show a thread-safe counter using `lock`, then explain why you'd replace it with `Interlocked.Increment` for a simple counter.",
        "answer": {
            "key_points": [
                "`lock(obj)` acquires a Monitor (mutual exclusion lock) — only one thread executes the block at a time.",
                "lock is NOT async-compatible — you can't await inside a lock block (deadlock risk).",
                "`SemaphoreSlim(1,1)` is the async equivalent — use `await semaphore.WaitAsync()` / `Release()`.",
                "`Interlocked.Increment/Decrement/Exchange` are atomic CPU instructions — faster than lock for simple numeric operations.",
                "Lock on a private object, never on `this` or public types (external code could also lock on them, causing deadlocks)."
            ],
            "example_solution": "// lock-based counter:\nclass Counter\n{\n    private int _count;\n    private readonly object _lock = new();\n    public void Increment() { lock (_lock) { _count++; } }\n    public int Value { get { lock (_lock) { return _count; } } }\n}\n\n// Better for simple counter — atomic, no lock overhead:\nclass AtomicCounter\n{\n    private int _count;\n    public void Increment() => Interlocked.Increment(ref _count);\n    public int Value => _count;\n}"
        }
    },
    {
        "id": "cs_021",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "primary constructors",
        "difficulty": "intermediate",
        "format": "snippet",
        "prompt": "What does this C# 12 primary constructor syntax do? What's the equivalent in earlier C#?",
        "code": "public class UserService(IUserRepository repo, ILogger<UserService> logger)\n{\n    public async Task<User?> GetUserAsync(int id)\n    {\n        logger.LogInformation('Getting user {Id}', id);\n        return await repo.FindByIdAsync(id);\n    }\n}",
        "answer": {
            "result": "Equivalent to declaring private fields for repo and logger, and a constructor that assigns them.",
            "explanation": "Primary constructors (C# 12) put constructor parameters directly in the class declaration. Parameters are captured as fields automatically when used in the class body. The equivalent pre-C#12 code is:\n```csharp\npublic class UserService\n{\n    private readonly IUserRepository repo;\n    private readonly ILogger<UserService> logger;\n    public UserService(IUserRepository repo, ILogger<UserService> logger)\n    { this.repo = repo; this.logger = logger; }\n}\n```\nNote: primary constructor params are NOT automatically readonly — use a regular constructor if you need readonly enforcement or XML docs on params."
        }
    },
    {
        "id": "cs_022",
        "language": "C#",
        "topic": "Type System",
        "subtopic": "IEquatable and GetHashCode",
        "difficulty": "intermediate",
        "format": "explain",
        "prompt": "Why should you override `GetHashCode` whenever you override `Equals`? What's the contract between them?",
        "task": "Implement `IEquatable<Point>` for a `Point` struct with X and Y coordinates, overriding both Equals and GetHashCode correctly.",
        "answer": {
            "key_points": [
                "Contract: if a.Equals(b) == true, then a.GetHashCode() == b.GetHashCode() MUST also be true.",
                "Hash-based collections (Dictionary, HashSet) use GetHashCode to find the bucket, then Equals to confirm.",
                "If you override Equals without GetHashCode: two 'equal' objects may hash to different buckets — can't find items in Dictionary/HashSet.",
                "Good hash: distribute evenly, cheap to compute, stable for the object's lifetime in a hash container.",
                "`HashCode.Combine(a, b)` (C# 8+) is the recommended way to combine multiple fields."
            ],
            "example_solution": "public struct Point : IEquatable<Point>\n{\n    public int X { get; }\n    public int Y { get; }\n\n    public Point(int x, int y) { X = x; Y = y; }\n\n    public bool Equals(Point other) => X == other.X && Y == other.Y;\n    public override bool Equals(object? obj) => obj is Point p && Equals(p);\n    public override int GetHashCode() => HashCode.Combine(X, Y);\n\n    public static bool operator ==(Point a, Point b) => a.Equals(b);\n    public static bool operator !=(Point a, Point b) => !a.Equals(b);\n}"
        }
    },
    {
        "id": "cs_023",
        "language": "C#",
        "topic": "Async",
        "subtopic": "ConfigureAwait",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What does `ConfigureAwait(false)` do? Why should library code use it but UI application code generally shouldn't?",
        "task": "Show an example where omitting ConfigureAwait(false) in library code can cause a deadlock in a WinForms/WPF app.",
        "answer": {
            "key_points": [
                "By default, `await` captures the current SynchronizationContext and resumes on it (e.g., UI thread in WinForms/WPF).",
                "ConfigureAwait(false): don't capture context — resume on any available thread pool thread.",
                "Library code should use ConfigureAwait(false) — it doesn't need to run on the UI thread and avoids deadlock.",
                "Deadlock scenario: UI thread calls .Result on a Task → blocks. Task tries to resume on UI thread (captured context) → deadlock.",
                "In ASP.NET Core, there's no SynchronizationContext — ConfigureAwait(false) has less impact but is still a best practice."
            ],
            "example_solution": "// Library code — use ConfigureAwait(false):\npublic async Task<string> FetchDataAsync()\n{\n    var data = await httpClient.GetStringAsync(url).ConfigureAwait(false);\n    return data.ToUpper(); // runs on thread pool, not UI thread\n}\n\n// Deadlock in WinForms without ConfigureAwait(false):\nvoid Button_Click(object s, EventArgs e)\n{\n    // UI thread blocks here:\n    var result = FetchDataAsync().Result; // DEADLOCK if FetchDataAsync captured UI context\n}"
        }
    },
    {
        "id": "cs_024",
        "language": "C#",
        "topic": "Language Features",
        "subtopic": "expression-bodied members and local functions",
        "difficulty": "beginner",
        "format": "snippet",
        "prompt": "What does each C# feature shown here do? Identify: expression-bodied member, local function, static local function, and tuple deconstruction.",
        "code": "public class MathHelper\n{\n    // A\n    public int Square(int n) => n * n;\n\n    // B\n    public (int Min, int Max) MinMax(int[] arr)\n    {\n        return (FindMin(), FindMax()); // C\n\n        int FindMin() => arr.Min();          // D\n        static int FindMax(int[] a) => a.Max(); // E — oops, won't compile as written\n    }\n\n    // F\n    var (min, max) = helper.MinMax(new[] { 3, 1, 4, 1, 5 });\n}",
        "answer": {
            "result": "A: expression body. B: tuple return. D: local function. F: tuple deconstruction.",
            "explanation": "A: `=>` expression body — single-expression methods without braces. B+C: returning a named tuple — callers access .Min and .Max. D: local function — defined inside a method, captures enclosing scope (arr). Local functions are compiled to private methods, avoid allocation unlike lambdas that capture. E as written won't compile (static local function can't capture arr without it being a parameter). F: tuple deconstruction — min and max are separate variables. Static local functions (C# 8+) explicitly can't capture outer variables, making the pure dependency explicit."
        }
    },
    {
        "id": "cs_025",
        "language": "C#",
        "topic": "Performance",
        "subtopic": "stackalloc and unsafe",
        "difficulty": "advanced",
        "format": "explain",
        "prompt": "What is `stackalloc` in C#? When would you use it and what are the risks? How does it interact with `Span<T>`?",
        "task": "Write a function that uses `stackalloc` to reverse a small byte array without heap allocation.",
        "answer": {
            "key_points": [
                "`stackalloc T[n]` allocates n elements on the stack — no GC pressure, no heap allocation.",
                "Stack memory is automatically reclaimed when the method returns — no cleanup needed.",
                "Risk: stack overflow if n is large. Only safe for small, bounded sizes (typically < 1KB).",
                "In modern C# (7.2+): `stackalloc` returns `Span<T>` when used in safe context — no `unsafe` keyword needed.",
                "Common use: small temp buffers in hot paths (crypto, parsers, network code)."
            ],
            "example_solution": "Span<byte> Reverse(ReadOnlySpan<byte> input)\n{\n    if (input.Length > 256)\n        throw new ArgumentException('Too large for stack allocation');\n\n    Span<byte> buffer = stackalloc byte[input.Length];\n    for (int i = 0; i < input.Length; i++)\n        buffer[i] = input[input.Length - 1 - i];\n    return buffer; // safe — caller receives it before method returns\n                   // NOTE: don't return stackalloc spans in production — undefined after return\n}"
        }
    },
]

for q in QUESTIONS:
    out = OUT / f"{q['id']}.json"
    out.write_text(json.dumps(q, indent=2) + "\n")

ts_count = sum(1 for q in QUESTIONS if q["id"].startswith("ts_"))
py_count = sum(1 for q in QUESTIONS if q["id"].startswith("py_"))
cs_count = sum(1 for q in QUESTIONS if q["id"].startswith("cs_"))
print(f"Written {len(QUESTIONS)} questions to {OUT}")
print(f"  TypeScript: {ts_count}, Python: {py_count}, C#: {cs_count}")
