import React, { Component } from 'react';
import { Classes, Tree } from "@blueprintjs/core";

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const TRACE_API_URL = "/trace";

function styleLabels(node) {
    // Set label to monospace style
    if (node.hasCaret === false) {
        node.label = (
            <div style={{ fontFamily: 'monospace' }}>{node.label}</div>
        )
    }

    if ('childNodes' in node) {
        node.childNodes.map(styleLabels);
    }
}

export default class TreeView extends Component {

    constructor(props) {
        super(props);
        this.state = {
            nodes: []
        }
    }

    componentDidMount() {
        // Call API
        axios.get(TRACE_API_URL, {
            params: {
                output_id: '9f6fc446-169d-48d2-8484-44b55ac7c83c'
            }
        }).then(
            ({ data }) => {
                // thing to do
                styleLabels(data);
                this.setState({ nodes: [data] });
            }
        ).catch(e => { console.log(e); });
    }

    render() {
        return (
            <Tree contents={this.state.nodes} className="bp3-minimal" />
        )
    }
}