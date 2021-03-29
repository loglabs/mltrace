import React, { Component } from 'react';
import { Navbar, Alignment, InputGroup, Button, ButtonGroup } from "@blueprintjs/core";

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

export default class Header extends Component {

    constructor(props) {
        super(props);

        this.onToggleTheme = this.onToggleTheme.bind(this);
        this.onChange = this.onChange.bind(this);
    }

    onToggleTheme() {
        this.props.onToggleTheme(!this.props.useDarkTheme);
    };

    onChange(e) {
        if (e.key === "Enter") {
            this.props.onCommand(e.target.value);
        }
    }

    render() {
        return (
            <Navbar>
                <Navbar.Group align={Alignment.LEFT}>
                    <Navbar.Heading>mltrace</Navbar.Heading>
                    <Navbar.Divider />
                    <InputGroup
                        className="bp3-minimal"
                        leftIcon="chevron-right"
                        placeholder="trace..."
                        onKeyUp={this.onChange}
                        style={{ width: '400px', fontFamily: 'monospace' }}
                    />
                </Navbar.Group>

                <Navbar.Group align={Alignment.RIGHT}>
                    <ButtonGroup minimal={true}>
                        <Button className="bp3-minimal" icon="git-repo" text="GitHub" onClick={() => window.open("https://www.github.com/shreyashankar/mltrace", "_blank")} />
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