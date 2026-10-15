import type { ZodiacSign } from './zodiac';
import type { DailyHoroscope } from '../types/horoscope';
import generatedForecasts from './generated/horoscopes.json';

type PublishedForecast = DailyHoroscope & {
  source: 'backend';
  sign: ZodiacSign['id'];
  forecast_date: string;
};

const forecastsByDate = generatedForecasts.forecasts as unknown as Record<
  string,
  Partial<Record<ZodiacSign['id'], PublishedForecast>>
>;

export function getPublishedForecast(
  sign: ZodiacSign['id'],
  forecastDate: string,
): PublishedForecast | undefined {
  const forecast = forecastsByDate[forecastDate]?.[sign];
  if (
    forecast?.source !== 'backend' ||
    forecast.sign !== sign ||
    forecast.forecast_date !== forecastDate
  ) {
    return undefined;
  }
  return forecast;
}
