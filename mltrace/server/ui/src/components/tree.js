import React, { Component } from 'react';
import { Tree } from "@blueprintjs/core";
import { CustomToaster } from "./toaster.js";
import { Intent } from "@blueprintjs/core";
import InfoCard from "./infocard.js";

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
            selectedNode: {},
            selected_id: ''
        }

        this.onNodeClick = this.onNodeClick.bind(this);
    }

    onNodeClick(node) {
        // const type = node.hasCaret === true ? 'component' : 'io';
        let id = (node.parent !== undefined) ? node.parent : node.id;
        this.setState({ selectedNode: node, selected_id: id });
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
                this.setState({ nodes: [data], output_id: this.props.output_id, selectedNode: data, selected_id: data.id });
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
        var clone = Object.assign({}, this.state.selectedNode);
        delete clone.childNodes;

        let childStyle = {
            flex: '1',
            margin: '1em',
            // paddingRight: '10em'
        }

        // let treeStyle = childStyle;
        // treeStyle.width

        let cardComponent = null;
        if (this.state.selected_id !== '') {
            // cardComponent = (<InfoCard label={clone.label} src={clone.object}
            // style={childStyle} />);
            cardComponent = <InfoCard style={childStyle} selected_id={this.state.selected_id} />

            // Set selected node
            //let selectedID = this.state.selectedNode.id;
            // isSelected
        }

        return (
            <div style={{ display: 'flex', margin: '1em', width: '85%' }}>
                <div style={childStyle}>
                    <Tree
                        contents={this.state.nodes}
                        className="bp3-minimal"
                        onNodeClick={this.onNodeClick}
                    />
                </div>
                {cardComponent}
            </div >
        )
    }
}