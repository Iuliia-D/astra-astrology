export type AnalyticsPayload = Record<string, string | number | boolean | null>;

/** MVP analytics seam. Deliberately sends no data to an external service. */
export function track(eventName: string, payload: AnalyticsPayload = {}): void {
  void eventName;
  void payload;
}
