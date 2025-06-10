export type Result<T, E> = { ok: true; value: T } | { ok: false; value: E };

export function ok<T>(value: T): Result<T, never> {
    return { ok: true, value };
}

export function err<E>(value: E): Result<never, E> {
    return { ok: false, value };
}
