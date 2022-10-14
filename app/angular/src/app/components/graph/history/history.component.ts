import { Component, Input, OnInit, OnChanges, SimpleChange } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Columns } from "src/app/Columns";
import { GraphData } from 'src/app/GraphData';
import { SelectedDatasets } from 'src/app/Datasets'

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
})
export class HistoryComponent implements OnInit {

  constructor(private dataService: DataService) { }

  public data: GraphData = {
    data: [],
    layout: {},

  };

  public columns: Columns = {
    geo: [],
    x: ["Time"],
    rshp: [],
    y: ["Y15-74"],
    id: 0,

  }
  @Input()
  public selectedDatasets: SelectedDatasets = {
    datasets: []
  }

  ngOnChanges(changes: SimpleChange) {
    if (this.selectedDatasets.datasets.length > 0) {
      if (this.selectedDatasets.datasets[0].geoColumn != undefined &&
        this.selectedDatasets.datasets[0].reshapeColumn != undefined
      ) {
        this.columns.geo[0] = this.selectedDatasets.datasets[0].geoColumn
        this.columns.rshp[0] = this.selectedDatasets.datasets[0].reshapeColumn
        this.dataService.getData(this.columns, "/graph/history").subscribe(data => this.data = {
          data: data.data,
          layout: data.layout
        });
      }
    }


  }

  ngOnInit(): void {

  }

}
