import React, { Component } from 'react';
import { AnchorButton, Navbar, Alignment, InputGroup, Button, ButtonGroup } from "@blueprintjs/core";
import HelpDialog from "./helpdialog.js";

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

export default class Header extends Component {

    constructor(props) {
        super(props);

        this.state = {
            value: this.props.defaultValue,
            submitted: true
        }

        this.onToggleTheme = this.onToggleTheme.bind(this);
        this.onKeyUp = this.onKeyUp.bind(this);
        this.onChange = this.onChange.bind(this);
    }

    onToggleTheme() {
        this.props.onToggleTheme(!this.props.useDarkTheme);
    };

    onKeyUp(e) {
        if (e.key === "Enter") {
            this.props.onCommand(e.target.value);
            this.setState({ submitted: true });
        }
    }

    onChange(e) {
        this.setState({ value: e.target.value, submitted: false });
    }

    componentDidUpdate() {
        if (this.state.submitted === true && this.props.defaultValue !== this.state.value) {
            this.setState({ value: this.props.defaultValue });
            return;
        }
    }

    render() {
        return (
            <Navbar className='bp3-minimal' fixedToTop={true}>
                <Navbar.Group align={Alignment.LEFT}>
                    <Navbar.Heading>mltrace</Navbar.Heading>
                    <Navbar.Divider />
                    <Button className="bp3-minimal" icon="home" text="Home" style={{ marginRight: '0.5em' }} onClick={() => this.props.onCommand("recent")} />
                    <InputGroup
                        className="bp3-minimal"
                        leftIcon="chevron-right"
                        placeholder="trace..."
                        onKeyUp={this.onKeyUp}
                        onChange={this.onChange}
                        style={{ width: '400px', fontFamily: 'monospace' }}
                        value={this.state.value}
                    />
                </Navbar.Group>

                <Navbar.Group align={Alignment.RIGHT}>
                    <ButtonGroup minimal={true}>
                        <AnchorButton className="bp3-minimal" icon="git-repo" text="GitHub" href="https://www.github.com/shreyashankar/mltrace" target="_blank" />
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
                    </ButtonGroup>
                </Navbar.Group>
            </Navbar >
        );
    }
}