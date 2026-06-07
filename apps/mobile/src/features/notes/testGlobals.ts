type TestBody = () => void | Promise<void>;
type TestDeclaration = (name: string, body: TestBody) => void;
type Expectation = {
  readonly not: Expectation;
  readonly toBe: (expected: unknown) => void;
  readonly toEqual: (expected: unknown) => void;
  readonly toContain: (expected: unknown) => void;
  readonly toHaveLength: (expected: number) => void;
  readonly toMatchObject: (expected: unknown) => void;
};
type ExpectDeclaration = (actual: unknown) => Expectation;

const vitestGlobals = globalThis as typeof globalThis & {
  readonly describe: TestDeclaration;
  readonly expect: ExpectDeclaration;
  readonly it: TestDeclaration;
};

export const describe = vitestGlobals.describe;
export const expect = vitestGlobals.expect;
export const it = vitestGlobals.it;
