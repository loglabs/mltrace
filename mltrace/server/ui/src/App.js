import React, { Component } from 'react';
import './App.css';
import Header from "./components/header.js"
import Trace from "./pages/trace.js"
import TagView from "./pages/tagview.js"
import History from "./pages/history.js"
import Recent from "./pages/recent.js"
import Inspect from "./pages/inspect.js"
import Review from "./pages/review.js"
import { CustomToaster } from "./components/toaster.js";
import { Classes, Intent } from "@blueprintjs/core";
import { Route, Switch, withRouter, Redirect } from 'react-router-dom';

import axios from "axios";
const FLAG_API_URL = "api/flag";
const UNFLAG_API_URL = "api/unflag";

let update_url = true;

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
    this.handleFlag = this.handleFlag.bind(this);
    this.handleUnflag = this.handleUnflag.bind(this);


  }

  handleDarkSwitchChange(useDark) {
    const nextThemeName = useDark ? DARK_THEME : LIGHT_THEME;
    setTheme(nextThemeName);
    this.setState({ themeName: nextThemeName, useDarkTheme: useDark });
  };

  handleHelp() {
    this.setState({ showHelp: false });
  }

  handleFlag(name) {
    // Update flag value
    axios.post(FLAG_API_URL, {
      id: name,
    }).then(
      ({ data }) => {
        CustomToaster.show({
          message: name + " flagged for review. Refresh this page to see changes reflected.",
          icon: "tick-error",
          intent: Intent.DANGER,
        });
      }
    ).catch(e => {
      CustomToaster.show({
        message: e.message,
        icon: "error",
        intent: Intent.DANGER,
      });
    });
  }

  handleUnflag(name) {
    // Update flag value
    axios.post(UNFLAG_API_URL, {
      id: name,
    }).then(
      ({ data }) => {
        CustomToaster.show({
          message: name + " unflagged. Refresh this page to see changes reflected.",
          icon: "tick-circle",
          intent: Intent.SUCCESS,
        });
      }
    ).catch(e => {
      CustomToaster.show({
        message: e.message,
        icon: "error",
        intent: Intent.DANGER,
      });
    });
  }


  handleCommand(input) {
    
    console.log("handleCommand")
    console.log(input)

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
      console.log("set")
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
    } else if (command === "flag") {
      if (args.length !== 1) {
        CustomToaster.show({
          message: "Please enter a valid output ID to flag for review.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      this.handleFlag(args[0]);
    } else if (command === "unflag") {
      if (args.length !== 1) {
        CustomToaster.show({
          message: "Please enter a valid output ID to unflag.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      this.handleUnflag(args[0]);
    } else if (command === "review") {
      if (args.length !== 0) {
        CustomToaster.show({
          message: "The review command does not take any parameters.",
          icon: "error",
          intent: Intent.DANGER,
        });
        return;
      }

      this.setState({ command: command, id: "", kwargs: {}, input: input });
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

    // rerender the website if the url command does not match with current state command
    var urlCommand = window.location.pathname.split("/").filter(str => str !== "");
    if (urlCommand.length === 0) {
      this.props.history.push('/recent');
    }
    if (urlCommand[0] !== this.state.command) {
      this.handleCommand(urlCommand.join(" "));
    }
    
    let darkstr = "";
    if (this.state.useDarkTheme === true) {
      darkstr = "bp3-dark";
    }
    let style = {
      backgroundColor: this.state.useDarkTheme === true ? '#293742' : '',
      minHeight: '100vh',
    };

    // console.log(this.state.command)
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
        <Switch>
          <Route exact path="/">
            {<Recent render={this.state.command === "recent"} commandHandler={this.handleCommand} kwargs={this.state.kwargs} />}
          </Route>
          <Route path="/history">
            {<History commandHandler={this.handleCommand} kwargs={this.state.kwargs} componentName={this.state.command === 'history' ? this.state.id : ""} />}
          </Route>
          <Route path="/recent">
            {<Recent render={this.state.command === "recent"} commandHandler={this.handleCommand} kwargs={this.state.kwargs} />}
          </Route>
          <Route path="/review">
            {<Review commandHandler={this.handleCommand} render={this.state.command === "review"} />}
          </Route>
          <Route path="/trace">
            {<Trace commandHandler={this.handleCommand} output_id={this.state.command === 'trace' ? this.state.id : ""} />}
          </Route>
          <Route path="/tag">
            {<TagView commandHandler={this.handleCommand} tagName={this.state.command === 'tag' ? this.state.id : ""} />}
          </Route>
          <Route path="/inspect">
            {<Inspect commandHandler={this.handleCommand} runId={this.state.command === "inspect" ? this.state.id : ""} />}
          </Route>
        </Switch>
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


export default withRouter(App);