import React, { Component } from 'react';
import './App.css';
import { Chart } from "react-google-charts";
import ReactJson from 'react-json-view'
import Header from "./components/header.js"
import TreeView from "./components/tree.js"
import { Classes } from "@blueprintjs/core";

const columns = [
  { type: "string", label: "Task ID" },
  { type: "string", label: "Task Name" },
  { type: "date", label: "Start Date" },
  { type: "date", label: "End Date" },
  { type: "number", label: "Duration" },
  { type: "number", label: "Percent Complete" },
  { type: "string", label: "Dependencies" },
];

const rows = [
  ["serve", "serve", new Date(1616800297), new Date(1616800298), null, 100, "inference"],
  ["inference", "inference", new Date(1616800295), new Date(1616800296), null, 100, "etl,training"],
  ["etl", "etl", new Date(1616800289), new Date(1616800290), null, 100, ""],
  ["training", "training", new Date(1616800290), new Date(1616800295), null, 100, ""]
];

const output_id = "9f6fc446-169d-48d2-8484-44b55ac7c83c";

const output_json = [{ "component_name": "serve", "inputs": ["preds.pq"], "outputs": ["9f6fc446-169d-48d2-8484-44b55ac7c83c"], "git_hash": "ee7c55410f8599c03be60e789d10045539a1350e", "code_snapshot": "@register(component_name='serve', inputs=['preds.pq'], output_vars=['x'], endpoint=True)\ndef serve(x):\n    print(f'serving output {x}!')\n", "start_timestamp": "1616800297", "end_timestamp": "1616800297", "dependencies": ["inference"] }, { "component_name": "inference", "inputs": ["features.pq", "model.joblib"], "outputs": ["preds.pq"], "git_hash": null, "code_snapshot": null, "start_timestamp": "1616800295", "end_timestamp": "1616800296", "dependencies": ["etl", "training"] }, { "component_name": "etl", "inputs": ["raw_data.csv", "cleaning_criteria.txt"], "outputs": ["features.pq"], "git_hash": null, "code_snapshot": null, "start_timestamp": "1616800289", "end_timestamp": "1616800290", "dependencies": [] }, { "component_name": "training", "inputs": ["train_set.pq", "test_set.pq"], "outputs": ["model.joblib", "metrics.txt"], "git_hash": "ee7c55410f8599c03be60e789d10045539a1350e", "code_snapshot": "@register(component_name='training', inputs=['train_set.pq', 'test_set.pq'], outputs=['model.joblib', 'metrics.txt'])\ndef train():\n    time.sleep(4)\n    print(\"training model\")\n", "start_timestamp": "1616800290", "end_timestamp": "1616800295", "dependencies": [] }];

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedRow: 0,
      themeName: getTheme(),
      useDarkTheme: getTheme() === DARK_THEME,
      output_id: ""
    };

    this.handleDarkSwitchChange = this.handleDarkSwitchChange.bind(this);
    this.handleCommand = this.handleCommand.bind(this);
  }

  handleDarkSwitchChange(useDark) {
    const nextThemeName = useDark ? DARK_THEME : LIGHT_THEME;
    setTheme(nextThemeName);
    this.setState({ themeName: nextThemeName, useDarkTheme: useDark });
  };

  handleCommand(input) {
    var args = input.split(" ").filter(str => str !== "");

    if (args.length === 0) return;

    var command = args[0].toLowerCase();
    args.shift();

    if (command === "trace") {
      // TODO(shreyashankar): error check here
      this.setState({ output_id: args[0] });
    }
  }

  render() {
    let darkstr = "";
    if (this.state.useDarkTheme === true) {
      darkstr = "bp3-dark";
    }
    let style = {
      backgroundColor: this.state.useDarkTheme === true ? '#293742' : '',
    };
    return (
      <div>
        <div className={darkstr} style={style}>
          <Header
            useDarkTheme={this.state.useDarkTheme}
            onToggleTheme={this.handleDarkSwitchChange}
            onCommand={this.handleCommand}
          />
          <TreeView output_id={this.state.output_id} />
          {/* <h1>{"Output: " + output_id}</h1>
          <h2>{"Showing metadata for the \"" + rows[this.state.selectedRow][0] + "\" component:"}</h2> */}
          {/* <ReactJson src={output_json[this.state.selectedRow]} /> */}
          {/* <Chart
            chartType="Gantt"
            data={[columns, ...rows]}
            width="100%"
            height="50%"
            chartEvents={[
              {
                eventName: 'select',
                callback: ({ chartWrapper }) => {
                  const chart = chartWrapper.getChart();
                  const selection = chart.getSelection()[0].row;
                  this.setState({ selectedRow: selection });
                },
              },
            ]}
            options={{
              tooltip: { isHtml: true },
              'gantt': {
                'criticalPathEnabled': false,
                // 'sortTasks': false,
                'percentEnabled': false,
                'backgroundColor': {
                  fill: 'transparent',
                },
                'innerGridHorizLine': {
                  stroke: '#ddd',
                  strokeWidth: 1,
                },
                // 'innerGridTrack': {
                //   fill: 'white'
                // },
                // 'innerGridDarkTrack': {
                //   fill: 'white'
                // },
                arrow: {
                  width: 3,
                  radius: 0
                },
              }
            }}
            legendToggle
          /> */}
        </div>
      </div>
    );
  }
}

const DARK_THEME = Classes.DARK;
const LIGHT_THEME = "";
const THEME_LOCAL_STORAGE_KEY = "blueprint-docs-theme";

/** Return the current theme className. */
export function getTheme() {
  return localStorage.getItem(THEME_LOCAL_STORAGE_KEY) || LIGHT_THEME;
}

/** Persist the current theme className in local storage. */
export function setTheme(themeName) {
  localStorage.setItem(THEME_LOCAL_STORAGE_KEY, themeName);
}


export default App;