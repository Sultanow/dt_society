import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { GraphData } from 'src/app/types/GraphData';
import { Selections } from 'src/app/types/Datasets';
import { HttpEventType } from '@angular/common/http';
import { time } from 'console';
import { transcode } from 'buffer';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
})
export class HistoryComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: GraphData = {
    data: [],
    layout: {
      legend: { title: { text: 'Countries' } },
      paper_bgcolor: '#232323',
      plot_bgcolor: '#232323',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)' },
      font: { color: '#f2f2f2' },
      margin: { t: 30, r: 100 },
    },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  createHistoryPlot(data: {}, selectedIdx: number) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }
    for (const [key, value] of Object.entries(data)) {
      let trace: any = {
        type: 'scatter',
        markers: 'lines+markers',
      };

      trace.name = key;

      if (trace.name !== 'DEU') {
        trace.visible = 'legendonly';
      }

      const timeSelected = this.selections.datasets[selectedIdx].timeSelected;
      const featureSelected =
        this.selections.datasets[selectedIdx].featureSelected;
      if (timeSelected !== undefined && featureSelected !== undefined) {
        trace.x = (value as any)[timeSelected];
        trace.y = (value as any)[featureSelected];
      }
      this.data.layout.yaxis.title = featureSelected;
      this.data.layout.xaxis.title = timeSelected;
      this.data.data.push(trace);
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
              this.selections.datasets[selectedDatasetIdx].featureOptions !==
              this.oldSelections?.datasets[selectedDatasetIdx].featureSelected
            ) {
              this.dataService
                .getData(
                  this.selections.datasets[selectedDatasetIdx],
                  '/graph/history'
                )
                .subscribe((data) => {
                  if (data.type === HttpEventType.Response) {
                    if (data.body) {
                      // this.data.data = (data.body as any).data;
                      // this.data.layout = data.body.layout;

                      this.createHistoryPlot(data.body, selectedDatasetIdx);
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
