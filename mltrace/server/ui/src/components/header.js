import React, { Component } from 'react';
import { AnchorButton, Navbar, Alignment, InputGroup, Button, Intent, Text, Tooltip, Position } from "@blueprintjs/core";
import HelpDialog from "./helpdialog.js";
import { CustomToaster } from "./toaster.js";

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import { Link, withRouter } from 'react-router-dom';

class Header extends Component {

    constructor(props) {
        super(props);

        this.state = {
            value: this.props.defaultValue,
            submitted: true
        }

        this.onToggleTheme = this.onToggleTheme.bind(this);
        this.onKeyUp = this.onKeyUp.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onShare = this.onShare.bind(this);
    }

    onToggleTheme() {
        this.props.onToggleTheme(!this.props.useDarkTheme);
    };

    onKeyUp(e) {
        if (e.key === "Enter") {
            this.props.onCommand(e.target.value);
            
            // update urlPath when user input different command 
            var urlPath = "/" + e.target.value.split(" ").filter(str => str !== "").join("/");
            this.props.history.push(urlPath);

            this.setState({ submitted: true });
        }
    }

    onChange(e) {
        this.setState({ value: e.target.value, submitted: false });
    }

    onShare() {
        this.inputValue.select();
        document.execCommand("copy");

        CustomToaster.show({
            message: <div>
                <Text>
                    <tt>{this.inputValue.value}</tt> copied to clipboard.
                </Text>
            </div>,
            icon: "tick",
            intent: Intent.SUCCESS,
        });
    }

    componentDidUpdate() {
        if (this.state.submitted === true && this.props.defaultValue !== this.state.value) {
            this.setState({ value: this.props.defaultValue });
            return;
        }
    }

    render() {
        let rightInputButton = (
            <Tooltip content={"Copy Command"} disabled={this.state.value === ""} position={Position.LEFT}>
                <Button minimal={true} icon="duplicate" onClick={this.onShare} disabled={this.state.value === ""} intent={Intent.PRIMARY} />
            </Tooltip>
        );
        return (
            <Navbar className='bp3-minimal' fixedToTop={true}>
                <Navbar.Group align={Alignment.LEFT}>
                    <Navbar.Heading>mltrace</Navbar.Heading>
                    <Navbar.Divider />
                    <Link to="/recent"><Button className="bp3-minimal" icon="home" text="Home" style={{ marginRight: '0.5em' }} onClick={() => this.props.onCommand("recent")} /></Link>
                    <InputGroup
                        className="bp3-minimal"
                        leftIcon="chevron-right"
                        placeholder="recent"
                        onKeyUp={this.onKeyUp}
                        onChange={this.onChange}
                        style={{ width: '40em', fontFamily: 'monospace' }}
                        value={this.state.value}
                        inputRef={el => this.inputValue = el}
                        rightElement={rightInputButton}
                    />
                </Navbar.Group>

                <Navbar.Group align={Alignment.RIGHT}>
                    <AnchorButton className="bp3-minimal" icon="document" text="Docs" href="https://mltrace.readthedocs.io" target="_blank" />
                    <AnchorButton className="bp3-minimal" icon="git-repo" text="GitHub" href="https://www.github.com/shreyashankar/mltrace" target="_blank" />
                    <Navbar.Divider />
                    <HelpDialog showHelp={this.props.showHelp}
                        onHandleHelp={this.props.onHandleHelp} />
                    <Button
                        className="bp3-minimal"
                        icon={this.props.useDarkTheme ? "flash" : "moon"}
                        // text={this.props.useDarkTheme ? "Use light theme"
                        // : "Use dark theme"}
                        text=""
                        onClick={this.onToggleTheme}
                    />
                </Navbar.Group>
            </Navbar >
        );
    }
}

export default withRouter(Header);