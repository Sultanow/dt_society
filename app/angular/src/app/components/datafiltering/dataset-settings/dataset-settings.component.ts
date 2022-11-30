import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Dataset, Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-dataset-settings',
  templateUrl: './dataset-settings.component.html',
  styleUrls: ['./dataset-settings.component.css']
})
export class DatasetSettingsComponent implements OnInit {

  public datasetId?: string;
  public geoEnabled: boolean = true;
  constructor(private dataService: DataService) { }

  public currentDataset?: Dataset;

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  onDeleteFile() {
    this.dataService.deleteDataset(this.datasetId, this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
    this.currentDataset = this.selections.datasets.filter(dataset => dataset.id == this.datasetId)[0];
  }

  showData(){
    if(this.currentDataset?.geoSelected === undefined){
      this.currentDataset!.geoSelected = "None";
    }
    this.selections.datasets.map(dataset => {
      if(dataset.id === this.datasetId){
        this.currentDataset;
      }
    })

    this.dataService.updateDataset(this.selections, this.datasetId)
    console.log(this.currentDataset)
    console.log(this.selections.datasets.filter(dataset => dataset.id == this.datasetId)[0])
  }

}
