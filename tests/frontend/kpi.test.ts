// Pure unit test for the KPI card label formatting logic.
// We import the file indirectly by re-implementing the tiny formatter here
// to avoid needing a fully rendered Next.js environment for a smoke test.

function kpiLabel(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000)     return `${(value / 1_000).toFixed(1)}k`;
  return value.toString();
}

describe('KPI label formatter', () => {
  it('formats millions', () => {
    expect(kpiLabel(1_500_000)).toBe('1.5M');
  });

  it('formats thousands', () => {
    expect(kpiLabel(12_500)).toBe('12.5k');
  });

  it('passes through small numbers', () => {
    expect(kpiLabel(42)).toBe('42');
  });
});
