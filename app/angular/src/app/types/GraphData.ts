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
  layout: {
    [property: string]: any;
    legend?: { title: { text: string }; groupclick?: string };
    paper_bgcolor: string;
    plot_bgcolor: string;
    xaxis: { gridcolor: string; title: string | undefined; range?: number[] };
    yaxis: { gridcolor: string; title: string | undefined };
    font: { color: string };
    margin?: { t?: number; r?: number; l?: number; b?: number };
    grid?: {};
    title?: string;
    autosize?: boolean;
  };
  config?: {};
}

export interface MapPlot {
  data: CountryData[];
  layout: any;
}

export interface CorrelationMatrix {
  columns: string[];
  matrix: [number[] | null[]];
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
}

export interface ProphetForecast {
  merge: ColumnValues;
  future: ColumnValues;
  forecast: { [id: string]: number[] };
}

export interface Scenario {
  active: boolean;
  selectable: boolean;
  data: number[];
}

export interface ScenarioData {
  [id: string]: Scenario;
}
