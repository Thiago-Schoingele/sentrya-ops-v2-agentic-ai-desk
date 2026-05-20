export function compactNumber(value: number) {
  return Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function number(value: number) {
  return Intl.NumberFormat("en").format(value);
}

export function percent(value: number) {
  return `${value.toFixed(2)}%`;
}

export function latency(value: number) {
  return value >= 1000 ? `${(value / 1000).toFixed(2)}s` : `${Math.round(value)}ms`;
}

export function shortTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(new Date(value));
}
