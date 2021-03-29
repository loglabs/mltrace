import React, { Component } from 'react';
import { Card, HTMLTable, Tag, Intent, Tree, Collapse, Button, Pre } from "@blueprintjs/core";

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

export default class CRInfoCard extends Component {

    constructor(props) {
        super(props);

        this.state = {
            showCode: false,
            showInputs: true,
            showOutputs: true
        };

        this.handleClick = this.handleClick.bind(this);
        this.onNodeToggle = this.onNodeToggle.bind(this);
    }

    handleClick() {
        this.setState({ showCode: !this.state.showCode });
    }

    onNodeToggle(e) {
        if (e.id === 'inputElement') {
            this.setState({ showInputs: !this.state.showInputs });
        } else {
            this.setState({ showOutputs: !this.state.showOutputs });
        }
    }

    render() {
        let info = JSON.parse(this.props.src);
        let commit = info.git_hash ? info.git_hash : "no commit found";
        let end = new Date(info.end_timestamp);
        let start = new Date(info.start_timestamp);

        let tags = ['demo', 'fake'];
        let tagElements = tags.map((name, index) => { return (<Tag minimal={true} intent={Intent.PRIMARY} style={{ marginRight: '5px' }} key={index}>{name}</Tag>) });

        let codeSnapshot = info.code_snapshot ? info.code_snapshot : 'no snapshot found';

        let inputElements = info.inputs.map((inp, index) =>
            (
                {
                    id: 'inp' + index,
                    label: (
                        <div style={{ fontFamily: 'monospace' }}>
                            {inp.name}
                        </div>
                    ),
                    hasCaret: false
                }
            )
        );
        let outputElements = info.outputs.map((out, index) =>
            (
                {
                    id: 'out' + index,
                    label: (
                        <div style={{ fontFamily: 'monospace' }}>
                            {out.name}
                        </div>
                    ),
                    hasCaret: false
                }
            )
        );
        let inputElement = {
            id: 'inputElement',
            label: 'Inputs',
            hasCaret: true,
            disabled: false,
            isExpanded: this.state.showInputs,
            childNodes: inputElements
        };
        let outputElement = {
            id: 'outputElement',
            label: 'Outputs',
            hasCaret: true,
            disabled: false,
            isExpanded: this.state.showOutputs,
            childNodes: outputElements
        };

        return (
            < div >
                <h2>{info.component_name}</h2>
                <HTMLTable bordered={false} interactive={false} className='bp3-minimal'>
                    <thead>
                        <tr>
                            <th style={{ paddingLeft: '0px' }}>Owner: shreyashankar</th>
                            <th>{tagElements}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style={{ paddingLeft: '0px' }}> <b>Started: </b>{info.start_timestamp} </td>
                            <td><b>Git commit: </b>{commit}</td>
                        </tr>
                        <tr>
                            <td style={{ paddingLeft: '0px' }}> <b>Finished: </b>{info.end_timestamp} </td>
                            <td><b>Duration: </b> {((end - start) / 1000) + 's'}</td>
                        </tr>
                    </tbody>
                </HTMLTable>
                <Tree
                    contents={[inputElement, outputElement]}
                    onNodeExpand={this.onNodeToggle}
                    onNodeCollapse={this.onNodeToggle}
                    style={{ padding: '15px 0px' }}
                />
                <div style={{ padding: '15px 0px' }}>
                    <Button className="bp3-minimal" outlined={true} onClick={this.handleClick}>{this.state.showCode ? "Hide" : "Show"} code snapshot </Button>
                    <Collapse isOpen={this.state.showCode} keepChildrenMounted={TextTrackCue} className='bp3-minimal'>
                        <Pre>
                            {codeSnapshot}
                        </Pre>
                    </Collapse>
                </div>
            </div >
        );
    }

}