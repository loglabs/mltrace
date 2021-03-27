import React, { Component } from 'react';
import { Tree } from "@blueprintjs/core";
import { CustomToaster } from "./toaster.js";
import { Intent } from "@blueprintjs/core";

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
            output_id: '',
            nodes: []
        }
    }

    componentDidUpdate() {
        if (this.props.output_id === "") {
            return null;
        }

        if (this.state.output_id === this.props.output_id) {
            return null;
        }

        axios.get(TRACE_API_URL, {
            params: {
                output_id: this.props.output_id
            }
        }).then(
            ({ data }) => {
                styleLabels(data);
                this.setState({ nodes: [data], output_id: this.props.output_id });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });;
            this.setState({ output_id: this.props.output_id });
        });
    }

    render() {
        return (
            <Tree contents={this.state.nodes} className="bp3-minimal" />
        )
    }
}