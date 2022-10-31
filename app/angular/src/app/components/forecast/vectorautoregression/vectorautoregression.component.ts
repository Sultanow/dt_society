import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-vectorautoregression',
  templateUrl: './vectorautoregression.component.html',
  styleUrls: ['./vectorautoregression.component.css'],
})
export class VectorautoregressionComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: Plot = {
    data: [],
    layout: {
      legend: { title: { text: 'Pearson r' } },
      paper_bgcolor: '#232323',
      plot_bgcolor: '#232323',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
    },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  public countries: string[] = [];

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;

      var countries: string[] | undefined = [] || undefined;

      for (const data of this.selections.datasets) {
        countries = [...countries, ...(data.countryOptions || [])];
      }

      this.countries = [...new Set(countries)];
    });
  }
}
