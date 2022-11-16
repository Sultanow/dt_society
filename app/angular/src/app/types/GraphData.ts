export interface GraphData {
  data: Array<Object>;
  layout: any;
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
    legend: { title: { text: string }; groupclick?: string };
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
  name: string;
}

export interface GraphControls {
  country?: string;
  features?: string | null | string[];
  frequency?: string;
  periods?: number;
  maxLags?: number;
  scenarios?: Scenarios;
  dependentDataset?: string;
}

export interface Models {
  [key: string]: string;
}

export interface Scenarios {
  [key: string]: number[];
}

export interface Forecast {
  [key: string]: number[];
}
export interface ProphetForecast {
  merge: ColumnValues;
  future: ColumnValues;
  forecast: Forecast;
}
