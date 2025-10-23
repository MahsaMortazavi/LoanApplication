// src/format.ts
export const currencyFmt = new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function toMoneyString(input: string | number): string {
  const n = typeof input === "number" ? input : parseFloat(String(input).replace(/[^\d.-]/g, ""));
  if (Number.isFinite(n)) return currencyFmt.format(n);
  return "";
}

export function parseMoney(input: string): string {
  // keep two decimals as string (e.g., "25000.00")
  const cleaned = input.replace(/[^\d.]/g, "");
  const parts = cleaned.split(".");
  if (parts.length === 1) return parts[0];
  return `${parts[0]}.${(parts[1] ?? "").slice(0, 2)}`;
}

export function formatSSN(value: string): string {
  // normalize to digits then format ###-##-####
  const digits = value.replace(/\D/g, "").slice(0, 9);
  const seg1 = digits.slice(0, 3);
  const seg2 = digits.slice(3, 5);
  const seg3 = digits.slice(5, 9);
  let out = seg1;
  if (seg2) out += `-${seg2}`;
  if (seg3) out += `-${seg3}`;
  return out;
}

export function validateEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function required(v: string) { return v.trim().length > 0; }

export function twoLetterState(v: string) { return /^[A-Za-z]{2}$/.test(v); }
