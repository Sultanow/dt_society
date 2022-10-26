import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { CorrelationMatrix, Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-heatmap',
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css'],
})
export class HeatmapComponent implements OnInit {
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

  public features = {
    availableFeatures: [],
  };

  selectedFeaturesControl = new FormControl('');

  private oldSelections?: Selections;
  public selectedFeatures: string | null = null;

  createHeatmapPlot(data: CorrelationMatrix) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let heatmap: any = {};

    let replacedZeroes = data.matrix.map((row) =>
      row.map((value) => {
        if (value === 0) {
          return null;
        }
        return value;
      })
    );

    heatmap.z = replacedZeroes.reverse();
    heatmap.x = data.columns;
    heatmap.y = data.columns.slice().reverse();
    heatmap.type = 'heatmap';
    heatmap.colorscale = 'Viridis';
    heatmap.colorbar = { title: 'Pearson r' };

    this.data.data.push(heatmap);
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      if (this.selections.datasets.length > 0) {
        if (
          !this.selections.datasets.some(
            (dataset) =>
              dataset.geoSelected === undefined ||
              dataset.timeSelected === undefined
          )
        ) {
          this.dataService
            .getData(this.selections.datasets, '/graph/heatmap')
            .subscribe((event) => {
              if (event.type === HttpEventType.Response) {
                if (event.body) {
                  this.createHeatmapPlot(event.body as CorrelationMatrix);
                }
              }
            });
        }
      }
    }
    this.oldSelections = structuredClone(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
    this.selectedFeaturesControl.valueChanges.subscribe((value) => {
      this.selectedFeatures = value;
    });
  }
}
