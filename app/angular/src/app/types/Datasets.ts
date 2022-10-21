export interface Dataset {
  id?: string;
  columns?: string[];
  timeOptions?: string[];
  featureOptions?: string[];
  geoSelected?: string;
  reshapeSelected?: string;
  timeSelected?: string;
  featureSelected?: string;
  isSelected?: boolean;
}

export interface Selections {
  datasets: Dataset[];
  selectedDataset?: string;
}
