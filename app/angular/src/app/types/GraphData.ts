export interface GraphData {
  data: Trace[];
  layout: any;
  config?: {};
}

export interface MapForecastGraph {
  data: [Trace[]];
  layout: any;
  config?: {};
}

export interface Trace {
  [property: string]: any;
}

export interface TableData {
  [column: string]: number | string;
}

export interface ColumnValues {
  [column: string]: number[] | string[];
}

export interface CountryData {
  [country: string]: ColumnValues;
}

export interface Plot {
  data: any[];
  layout: any;
  config?: {};
}

export interface CorrelationMatrix {
  columns: string[];
  matrix: [number[] | null[]];
  matchingFrequencies: boolean;
}

export interface Frame {
  data: [
    {
      z: any[];
    }
  ];
}

export interface GraphControls {
  country?: string;
  features?: string | null | string[];
  frequency?: string;
  periods?: number;
  maxLags?: number;
  scenarios?: ScenarioData;
  dependentDataset?: string;
  predictions?: number;
}

export interface ProphetForecast {
  merge: ColumnValues;
  future: ColumnValues;
  forecast: { [id: string]: number[] };
  slidervalues?: string[];
}

export interface Scenario {
  active: boolean;
  selectable: boolean;
  data: number[];
}

export interface ScenarioData {
  [id: string]: Scenario;
}
