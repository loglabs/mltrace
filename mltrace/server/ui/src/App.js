import React, { Component } from 'react';
import './App.css';
import Header from "./components/header.js"
import TreeView from "./components/tree.js"
import { CustomToaster } from "./components/toaster.js";
import { Classes, Intent } from "@blueprintjs/core";

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
      if (args.length !== 1) {
        CustomToaster.show({
          message: "Please enter a valid name or ID to trace.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      this.setState({ output_id: args[0] });
    }
    else {
      CustomToaster.show({
        message: "Command `" + command + "` not supported.",
        icon: "error",
        intent: Intent.DANGER,
      });
    }
  }

  render() {
    let darkstr = "";
    if (this.state.useDarkTheme === true) {
      darkstr = "bp3-dark";
    }
    let style = {
      backgroundColor: this.state.useDarkTheme === true ? '#293742' : '',
      height: '100vh',
    };
    return (
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