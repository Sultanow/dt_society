export interface Dataset {
  id?: string;
  separator?: string;
  columns?: string[];
  timeOptions?: string[];
  featureOptions?: string[];
  geoSelected?: string;
  countryOptions?: string[];
  reshapeSelected?: string;
  timeSelected?: string;
  featureSelected?: string;
  isSelected?: boolean;
}

export interface Selections {
  datasets: Dataset[];
  selectedDataset?: string;
}
