import React, { Component } from 'react';
import { Navbar, Alignment, InputGroup, Button } from "@blueprintjs/core";

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

export default class Header extends Component {
    render() {
        return (
            <Navbar>
                <Navbar.Group align={Alignment.LEFT}>
                    <Navbar.Heading>mltrace</Navbar.Heading>
                    <Navbar.Divider />
                    <Button className="bp3-minimal" icon="home" text="Home" />
                    <InputGroup
                        className="bp3-minimal"
                        leftIcon="search"
                        placeholder="Search..."
                    />
                </Navbar.Group>
            </Navbar>
        );
    }
}