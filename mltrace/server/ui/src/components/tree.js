import React, { Component } from 'react';
import { Tree, Card } from "@blueprintjs/core";
import { CustomToaster } from "./toaster.js";
import { Intent } from "@blueprintjs/core";
import ReactJson from 'react-json-view'

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
            nodes: [],
            selected_node: {}
        }

        this.onNodeClick = this.onNodeClick.bind(this);
    }

    onNodeClick(node) {
        // const type = node.hasCaret === true ? 'component' : 'io';
        this.setState({ selected_node: node });
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
                this.setState({ nodes: [data], output_id: this.props.output_id, selected_node: data });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
            this.setState({ output_id: this.props.output_id });
        });
    }

    render() {
        var clone = Object.assign({}, this.state.selected_node);
        delete clone.childNodes;

        let childStyle = {
            flex: 1,
            margin: '10px',
        }

        return (
            <div style={{ display: 'flex', margin: '10px' }}>
                <Tree
                    contents={this.state.nodes}
                    className="bp3-minimal"
                    onNodeClick={this.onNodeClick}
                    style={childStyle}
                />
                <Card interactive={false} style={childStyle}>
                    <h1>{this.state.selected_node.label}</h1>
                    <ReactJson
                        src={clone}
                    />
                </Card>
            </div>
        )
    }
}