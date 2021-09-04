import React, { Component } from 'react';
import InfoCard from '../components/infocard.js';

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

export default class Inspect extends Component {

    render() {
        if (this.props.runId === "") return null;

        let childStyle = {
            flex: '0 1 auto',
            margin: '1em',
            // paddingRight: '10em'
        }

        return (
            <InfoCard selected_id={this.props.runId} style={childStyle} commandHandler={this.props.commandHandler} />
        )
    }

}