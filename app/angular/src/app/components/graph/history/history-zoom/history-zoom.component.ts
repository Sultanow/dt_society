import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-history-zoom',
  templateUrl: './history-zoom.component.html',
  styleUrls: ['./history-zoom.component.css'],
})
export class HistoryZoomComponent implements OnInit {
  constructor(@Inject(MAT_DIALOG_DATA) public plotData: Plot) {}

  public data: Plot = {
    data: [],
    layout: {},
    config: { responsive: true },
  };

  ngOnInit(): void {
    this.data = structuredClone(this.plotData);
    this.data.layout.width = 1400;
    this.data.layout.height = 1000;
  }
}
