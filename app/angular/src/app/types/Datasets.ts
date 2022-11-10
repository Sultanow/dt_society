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
}

export interface Selections {
  datasets: Dataset[];
  selectedDataset?: string;
}

export interface Options {
  features?: string[];
  countries?: string[];
}
