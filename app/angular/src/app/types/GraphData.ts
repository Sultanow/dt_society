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
  data: CountryData[];
  layout: {
    legend: { title: { text: string } };
    paper_bgcolor: string;
    plot_bgcolor: string;
    xaxis: { gridcolor: string; title: string | undefined };
    yaxis: { gridcolor: string; title: string | undefined };
    font: { color: string };
    margin: { t: number; r: number };
  };
}

export interface MapPlot {
  data: CountryData[];
  layout: any;
}
