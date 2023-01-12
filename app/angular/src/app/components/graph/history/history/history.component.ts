import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Plot, CountryData } from 'src/app/types/GraphData';
import { Selections } from 'src/app/types/Datasets';
import { HttpEventType } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { HistoryZoomComponent } from 'src/app/components/graph/history/history-zoom/history-zoom.component';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
})
export class HistoryComponent implements OnInit {
  constructor(private dataService: DataService, public dialog: MatDialog) {}

  public showSpinner: boolean = false;

  public historyPlot: Plot = {
    data: [],
    layout: {
      margin: { t: 70, b: 0, l: 35, r: 90 },
      legend: { title: { text: 'Countries' } },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
    },
    config: { responsive: true },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  createHistoryPlot(data: CountryData, selectedIdx: number) {
    if (
      Object.keys(data).includes(
        this.selections.datasets[selectedIdx].featureSelected!
      )
    ) {
      this.createPlotWithoutGeoReference(selectedIdx, data);
    } else {
      this.createPlotWithGeoReference(data, selectedIdx);
    }
  }

  private createPlotWithoutGeoReference(
    selectedIdx: number,
    data: CountryData
  ) {
    this.historyPlot = {
      data: [],
      layout: {
        margin: { t: 70, b: 50, l: 40, r: 10 },
        paper_bgcolor: '#424242',
        plot_bgcolor: '#424242',
        xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
        yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
        font: { color: '#f2f2f2' },
      },
      config: { responsive: true },
    };

    let trace: any = {
      type: 'scatter',
      mode: 'lines',
    };

    const timeSelected = this.selections.datasets[selectedIdx].timeSelected;
    const featureSelected =
      this.selections.datasets[selectedIdx].featureSelected;
    if (timeSelected !== undefined && featureSelected !== undefined) {
      trace.x = data[timeSelected];
      trace.y = data[featureSelected];
    }

    this.historyPlot.layout.yaxis.title = featureSelected;
    this.historyPlot.layout.xaxis.title = timeSelected;
    this.historyPlot.data.push(trace);
  }

  private createPlotWithGeoReference(data: CountryData, selectedIdx: number) {
    this.historyPlot = {
      data: [],
      layout: {
        margin: { t: 70, b: 0, l: 35, r: 90 },
        legend: { title: { text: 'Countries' } },
        paper_bgcolor: '#424242',
        plot_bgcolor: '#424242',
        xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
        yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
        font: { color: '#f2f2f2' },
      },
      config: { responsive: true },
    };

    let count = 0;
    for (const [key, value] of Object.entries(data)) {
      let trace: any = {
        type: 'scatter',
        mode: 'lines',
      };

      trace.name = key;

      if (count > 4) {
        trace.visible = 'legendonly';
      }
      count++;

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

  zoom() {
    this.dialog.open(HistoryZoomComponent, {
      data: this.historyPlot,
    });
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      if (this.selections.datasets.length > 0) {
        const selectedDatasetId = this.selections.selectedDataset;

        const selectedDatasetIdx = this.selections.datasets.findIndex(
          (dataset) => dataset.id == selectedDatasetId
        );

        if (this.selections.datasets[selectedDatasetIdx] !== undefined) {
          let selectedDataset = this.selections.datasets[selectedDatasetIdx];
          if (
            selectedDataset.featureSelected !== undefined &&
            selectedDataset.timeSelected !== undefined
          ) {
            if (
              selectedDataset.featureSelected !==
                this.oldSelections?.datasets[selectedDatasetIdx]
                  .featureSelected ||
              this.selections.selectedDataset !==
                this.oldSelections?.selectedDataset ||
              selectedDataset.timeSelected !==
                this.oldSelections?.datasets[selectedDatasetIdx].timeSelected
            ) {
              this.showSpinner = true;
              this.dataService
                .getData(selectedDataset, '/graph/history', {})
                .subscribe((event) => {
                  if (event.type === HttpEventType.Response) {
                    if (event.body) {
                      this.createHistoryPlot(
                        event.body as CountryData,
                        selectedDatasetIdx
                      );
                      this.showSpinner = false;
                    }
                  }
                });
              this.oldSelections = structuredClone(this.selections);
            }
          } else {
            this.historyPlot.data = [];
          }
        }
      }
    });
  }
}
