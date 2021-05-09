import React, { Component } from 'react';
import './App.css';
import Header from "./components/header.js"
import Trace from "./pages/trace.js"
import TagView from "./pages/tagview.js"
import History from "./pages/history.js"
import Recent from "./pages/recent.js"
import Inspect from "./pages/inspect.js"
import { CustomToaster } from "./components/toaster.js";
import { Classes, Intent } from "@blueprintjs/core";
import { BrowserRouter, Route, Switch } from 'react-router-dom';

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      themeName: getTheme(),
      useDarkTheme: getTheme() === DARK_THEME,
      input: "recent",
      id: "",
      command: "recent",
      kwargs: {},
      showHelp: false
    };

    this.handleDarkSwitchChange = this.handleDarkSwitchChange.bind(this);
    this.handleCommand = this.handleCommand.bind(this);
    this.handleHelp = this.handleHelp.bind(this);
  }

  handleDarkSwitchChange(useDark) {
    const nextThemeName = useDark ? DARK_THEME : LIGHT_THEME;
    setTheme(nextThemeName);
    this.setState({ themeName: nextThemeName, useDarkTheme: useDark });
  };

  handleHelp() {
    this.setState({ showHelp: false });
  }

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

      this.setState({ command: 'trace', id: args[0], kwargs: {}, input: input });
    }
    else if (command === "tag") {
      if (args.length !== 1) {
        CustomToaster.show({
          message: "Please enter a valid tag name to show components for.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      this.setState({ command: 'tag', id: args[0], kwargs: {}, input: input });
    } else if (command === "history") {
      if (args.length === 0 || args.length > 2) {
        CustomToaster.show({
          message: "Please enter a valid component name to show run history for.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }
      let newState = { command: 'history', id: args[0], kwargs: {}, input: input };
      if (args.length === 2) {
        newState.kwargs = { 'limit': args[1] };
      }

      this.setState(newState);
    } else if (command === "recent") {
      if (args.length > 1) {
        CustomToaster.show({
          message: "Please enter a valid limit or no extra arguments.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      let newState = { command: 'recent', kwargs: {}, id: '', input: input }
      if (args.length === 1) {
        newState.kwargs = { 'limit': args[0] };
      }

      this.setState(newState);
    } else if (command === "inspect") {
      if (args.length !== 1) {
        CustomToaster.show({
          message: "Please enter a valid component run ID to show details for.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      this.setState({ command: command, id: 'componentrun_' + args[0], kwargs: {}, input: input });
    } else if (command === "help") {
      this.setState({ showHelp: true });
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
      minHeight: '100vh',
    };

    return (
      <div className={darkstr} style={style}>
        <Header
          useDarkTheme={this.state.useDarkTheme}
          onToggleTheme={this.handleDarkSwitchChange}
          onCommand={this.handleCommand}
          defaultValue={this.state.input}
          showHelp={this.state.showHelp}
          onHandleHelp={this.handleHelp}
        />
        <div id='spacing-div' style={{ paddingTop: '4em' }}></div>
        <BrowserRouter>
          <Switch>
            <Route path="/recent">
              <Recent render={this.state.command === "recent"} commandHandler={this.handleCommand} kwargs={this.state.kwargs} />
            </Route>
            <Route path="/">
              {<Recent render={this.state.command === "recent"} commandHandler={this.handleCommand} kwargs={this.state.kwargs} />}
              {<Trace commandHandler={this.handleCommand} output_id={this.state.command === 'trace' ? this.state.id : ""} />}
              {<TagView commandHandler={this.handleCommand} tagName={this.state.command === 'tag' ? this.state.id : ""} />}
              {<History commandHandler={this.handleCommand} kwargs={this.state.kwargs} componentName={this.state.command === 'history' ? this.state.id : ""} />}
              {<Inspect commandHandler={this.handleCommand} runId={this.state.command === "inspect" ? this.state.id : ""} />}
            </Route>
          </Switch>
        </BrowserRouter>
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