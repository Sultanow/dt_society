import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Plot, CountryData } from 'src/app/types/GraphData';
import { Selections } from 'src/app/types/Datasets';
import { HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
})
export class HistoryComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public historyPlot: Plot = {
    data: [],
    layout: {
      legend: { title: { text: 'Countries' } },
      paper_bgcolor: '#232323',
      plot_bgcolor: '#232323',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      margin: { t: 30, r: 100 },
    },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  createHistoryPlot(data: CountryData, selectedIdx: number) {
    if (this.historyPlot.data.length > 0) {
      this.historyPlot.data = [];
    }
    for (const [key, value] of Object.entries(data)) {
      let trace: any = {
        type: 'scatter',
        mode: 'lines',
      };

      trace.name = key;

      if (trace.name !== 'DEU') {
        trace.visible = 'legendonly';
      }

      const timeSelected = this.selections.datasets[selectedIdx].timeSelected;
      const featureSelected =
        this.selections.datasets[selectedIdx].featureSelected;
      if (timeSelected !== undefined && featureSelected !== undefined) {
        trace.x = value[timeSelected];
        trace.y = value[featureSelected];
      }
      this.historyPlot.layout.yaxis.title = featureSelected;
      this.historyPlot.layout.xaxis.title = timeSelected;
      this.historyPlot.data.push(trace);
    }
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      if (this.selections.datasets.length > 0) {
        const selectedDatasetId = this.selections.selectedDataset;

        const selectedDatasetIdx = this.selections.datasets.findIndex(
          (dataset) => dataset.id == selectedDatasetId
        );

        if (this.selections.datasets[selectedDatasetIdx] !== undefined) {
          if (
            this.selections.datasets[selectedDatasetIdx].geoSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].reshapeSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].featureSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].timeSelected !==
              undefined
          ) {
            if (
              this.selections.datasets[selectedDatasetIdx].featureSelected !==
                this.oldSelections?.datasets[selectedDatasetIdx]
                  .featureSelected ||
              this.selections.selectedDataset !==
                this.oldSelections?.selectedDataset ||
              this.selections.datasets[selectedDatasetIdx].timeSelected !==
                this.oldSelections?.datasets[selectedDatasetIdx].timeSelected
            ) {
              this.dataService
                .getData(
                  this.selections.datasets[selectedDatasetIdx],
                  '/graph/history',
                  {}
                )
                .subscribe((event) => {
                  if (event.type === HttpEventType.Response) {
                    if (event.body) {
                      this.createHistoryPlot(
                        event.body as CountryData,
                        selectedDatasetIdx
                      );
                    }
                  }
                });
            }
          }
        }
      }
      this.oldSelections = structuredClone(this.selections);
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
