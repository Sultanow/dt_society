export interface DatasetOptions {
  datasetId: string;
  columns: string[];
  timeOptions?: string[];
  featureOptions?: string[];
}

export interface DatasetSelection {
  datasetId?: string;
  geoColumn?: string;
  reshapeColumn?: string;
  timeColumn?: string;
  featureColumn?: string;
}

export interface AvailableDatasets {
  datasets: DatasetOptions[];
}

export interface SelectedDatasets {
  datasets: DatasetSelection[];
  inFocusDataset?: string;
}
