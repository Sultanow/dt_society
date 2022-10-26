export interface GraphData {
  data: Array<Object>;
  layout: any;
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
    xaxis: { gridcolor: string; title: string | undefined };
    yaxis: { gridcolor: string; title: string | undefined };
    font: { color: string };
    margin?: { t: number; r: number };
    grid?: {};
  };
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
    z: any[]
    }
  ];
  name: string;
}
