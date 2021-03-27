import React, { Component } from 'react';
import { Navbar, Alignment, InputGroup, Button } from "@blueprintjs/core";

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
                    {/* <Button className="bp3-minimal" icon="home" text="Home" /> */}
                    <InputGroup
                        className="bp3-minimal"
                        leftIcon="chevron-right"
                        placeholder="trace..."
                        onKeyUp={this.onChange}
                        style={{ width: '400px', fontFamily: 'monospace' }}
                    />
                </Navbar.Group>

                <Navbar.Group align={Alignment.RIGHT}>
                    <Button
                        className="bp3-minimal"
                        icon={this.props.useDarkTheme ? "flash" : "moon"}
                        // text={this.props.useDarkTheme ? "Light theme" : "Dark theme"}
                        text=""
                        onClick={this.onToggleTheme}
                    />
                </Navbar.Group>
            </Navbar >
        );
    }
}