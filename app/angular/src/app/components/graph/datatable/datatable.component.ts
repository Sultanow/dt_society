import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { TableData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-datatable',
  templateUrl: './datatable.component.html',
  styleUrls: ['./datatable.component.css'],
})
export class DatatableComponent implements OnInit {
  constructor(private dataService: DataService) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };
  private oldSelections?: Selections;

  public data: TableData[] = [];

  public columns: string[] = [];

  updateData(newdata: TableData[]) {
    this.columns = Object.keys(newdata[0]);

    if (newdata.length >= 100) {
      newdata = newdata.slice(0, 100);
      let additionaldata = {};
      for (let column of this.columns) {
        let pair = { [column]: '.\n.\n.' };
        additionaldata = { ...additionaldata, ...pair };
      }
      newdata.push(additionaldata);
    }
    this.data = newdata;
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      if (this.selections.datasets.length > 0) {
        const datasetId = this.selections.selectedDataset;

        const selectedDatasetIdx = this.selections.datasets.findIndex(
          (dataset) => dataset.id == datasetId
        );

        if (this.selections.datasets[selectedDatasetIdx] !== undefined) {
          this.dataService
            .getData(
              this.selections.datasets[selectedDatasetIdx],
              '/graph/datatable',
              {}
            )
            .subscribe((res) => {
              if (res.type === HttpEventType.Response) {
                if (res.body) {
                  this.updateData(res.body as TableData[]);
                }
              }
            });
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
