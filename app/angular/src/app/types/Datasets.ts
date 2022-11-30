export interface Dataset {
  id?: string;
  columns?: string[];
  timeOptions?: string[];
  featureOptions?: string[];
  geoSelected?: string;
  countryOptions?: string[];
  reshapeSelected?: string;
  timeSelected?: string;
  featureSelected?: string;
  possibleFeatures?: string[];
  token?: string;
  name?: string;
  initialColumns?: string[];
}

export interface Selections {
  datasets: Dataset[];
  selectedDataset?: string;
  totalCountries?: string[];
  selectedCountry?: string;
}

export interface Options {
  features?: string[];
  countries?: string[];
  reshape_column?: string;
}
