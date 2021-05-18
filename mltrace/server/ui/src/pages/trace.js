import React, { Component } from 'react';
import { Tree, Classes, Tooltip, Icon } from "@blueprintjs/core";
import { CustomToaster } from "../components/toaster.js";
import { Intent } from "@blueprintjs/core";
import InfoCard from "../components/infocard.js";

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const TRACE_API_URL = "api/trace";

function styleLabels(node) {
    // Set label to monospace style
    if (node.hasCaret === false) {
        node.label = (
            <div style={{ fontFamily: 'monospace', wordWrap: 'break-word' }}>{node.label}</div>
        )
    }

    if (node.stale !== undefined && node.stale !== null && node.stale.length >= 1) {
        node.secondaryLabel = (
            <Tooltip content="This component run may have stale dependencies.">
                <Icon icon="warning-sign" intent={Intent.WARNING} />
            </Tooltip>
        );
    }

    if ('childNodes' in node) {
        node.childNodes.map(styleLabels);
    }
}

export default class Trace extends Component {

    constructor(props) {
        super(props);
        this.state = {
            output_id: '',
            nodes: [],
            selected_id: ''
        }

        this.onNodeClick = this.onNodeClick.bind(this);
    }

    onNodeClick(node) {
        // const type = node.hasCaret === true ? 'component' : 'io';
        let id = (node.parent !== undefined) ? node.parent : node.id;
        this.setState({ selected_id: id });
    }

    componentDidUpdate() {
        if (this.state.output_id === this.props.output_id) {
            return null;
        }

        if (this.props.output_id === "") {
            this.setState({ output_id: this.props.output_id, nodes: [], selected_id: '' });
            return null;
        }

        axios.get(TRACE_API_URL, {
            params: {
                output_id: this.props.output_id
            }
        }).then(
            ({ data }) => {
                data.map((node) => styleLabels(node));
                this.setState({ nodes: data, output_id: this.props.output_id, selected_id: data[0].id });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
            // this.setState({ output_id: '' });
        });
    }

    render() {
        if (this.state.output_id === '') return null;

        let treeContent = (
            <div style={{ marginTop: '1em', marginBottom: '1em', marginRight: '1em', flex: '0 1 auto' }} className={Classes.MINIMAL}>
                <Tree
                    contents={this.state.nodes}
                    className="bp3-minimal"
                    onNodeClick={this.onNodeClick}
                />
            </div>
        );

        let style = { display: 'flex', margin: '1em' };

        return (
            <div style={style}>
                {treeContent}
                <InfoCard style={{
                    flex: '0 1 auto',
                    margin: '1em'
                }} selected_id={this.state.selected_id} commandHandler={this.props.commandHandler} />
            </div >
        )
    }
}