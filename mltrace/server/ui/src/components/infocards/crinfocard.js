import React, { Component } from 'react';
import { HTMLTable, Tag, Intent, Tree, Collapse, Button, Pre, Classes, Tooltip, Position, Callout, EditableText, Icon } from "@blueprintjs/core";
import { CustomToaster } from "../toaster.js";

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const NOTES_API_URL = "api/notes";
const FLAG_API_URL = "api/flag";
const UNFLAG_API_URL = "api/unflag";

export default class CRInfoCard extends Component {

    constructor(props) {
        super(props);

        this.state = {
            showCode: false,
            showInputs: true,
            showOutputs: true,
            notes: this.props.src.notes,
            inputs: this.props.src.inputs,
            outputs: this.props.src.outputs
        };

        this.handleClick = this.handleClick.bind(this);
        this.onNodeToggle = this.onNodeToggle.bind(this);
        this.onFinishEditingText = this.onFinishEditingText.bind(this);
        this.showIOPointerFlag = this.showIOPointerFlag.bind(this);
        this.onFlagIOPointer = this.onFlagIOPointer.bind(this);
        this.onUnflagIOPointer = this.onUnflagIOPointer.bind(this);
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

    onFinishEditingText(id, text) {
        if (text === this.state.notes) return;

        // Update notes if there's a change
        axios.post(NOTES_API_URL, {
            id: this.props.id,
            notes: text
        }).then(
            ({ data }) => {
                this.setState({ notes: data });
                CustomToaster.show({
                    message: "Description for ComponentRun " + id + " updated.",
                    icon: "tick-circle",
                    intent: Intent.SUCCESS,
                });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
        });
    }

    onFlagIOPointer(name, idx, inputIndicator) {
        // Update flag value
        axios.post(FLAG_API_URL, {
            id: name,
        }).then(
            ({ data }) => {
                let items = inputIndicator === true ? [...this.state.inputs] : [...this.state.outputs];
                let item = {
                    ...items[idx],
                    flag: data
                };
                items[idx] = item;

                if (inputIndicator) {
                    this.setState({ 'inputs': items });
                } else {
                    this.setState({ 'outputs': items });
                }

                CustomToaster.show({
                    message: item.name + " flagged for review.",
                    icon: "tick-circle",
                    intent: Intent.SUCCESS,
                });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
        });
    }

    onUnflagIOPointer(name, idx, inputIndicator) {
        // Update flag value
        axios.post(UNFLAG_API_URL, {
            id: name,
        }).then(
            ({ data }) => {
                let items = inputIndicator === true ? [...this.state.inputs] : [...this.state.outputs];
                let item = {
                    ...items[idx],
                    flag: data
                };
                items[idx] = item;

                if (inputIndicator) {
                    this.setState({ 'inputs': items });
                } else {
                    this.setState({ 'outputs': items });
                }

                CustomToaster.show({
                    message: item.name + " unflagged.",
                    icon: "tick-circle",
                    intent: Intent.SUCCESS,
                });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
        });
    }

    showIOPointerFlag(iopointer, idx, inputIndicator) {
        let placeholder = inputIndicator === true ? "input" : "output";

        return iopointer.flag === true ? (
            <Tooltip content={"This " + placeholder + " ID is flagged for review. Click to unflag."}>
                <Button icon="error" intent={Intent.DANGER} minimal={true} onClick={() => this.onUnflagIOPointer(iopointer.name, idx, inputIndicator)} />
            </Tooltip>
        ) : (
            <Tooltip content={"This " + placeholder + " ID does not have any known problems. Click to flag for review."}>
                <Button icon="tick-circle" intent={Intent.SUCCESS} minimal={true} onClick={() => this.onFlagIOPointer(iopointer.name, idx, inputIndicator)} />
            </Tooltip>
        );
    }

    render() {
        let info = this.props.src;

        let countContent = null;
        if (this.props.count) {
            countContent = (
                <Callout className={Classes.MINIMAL} intent={Intent.PRIMARY} style={{
                    marginBottom: '0.5em'
                }}>
                    This component run has <b>{this.props.count / this.props.numOutputs * 100}%</b> coverage: it was used <b>{this.props.count} {(this.props.count === 1) ? "time" : "times"}</b> in producing the flagged outputs.
                </Callout >
            );
        }

        let commit = info.git_hash ? info.git_hash : "no commit found";
        let end = new Date(info.end_timestamp);
        let start = new Date(info.start_timestamp);
        let stale = null;
        if (info.stale !== undefined && info.stale !== null && info.stale.length >= 1) {
            stale = (
                <Callout className={Classes.MINIMAL} intent={Intent.WARNING}>
                    Some dependencies may be stale:
                    <ul>
                        {info.stale.map((inf, index) => (<li key={"callout_" + index}>{inf}</li>))}
                    </ul>
                </Callout>
            );
        }

        let tagElements = info.tags.map((name, index) => {
            return (
                <Tag
                    minimal={true}
                    onClick={() => { this.props.commandHandler("tag " + name) }}
                    intent={Intent.PRIMARY}
                    style={{ marginRight: '0.5em' }}
                    key={index}
                    interactive={true}>
                    {name}
                </Tag>)
        });

        let codeSnapshot = info.code_snapshot ? info.code_snapshot : 'no snapshot found';

        let inputElements = this.state.inputs.map((inp, index) =>
        (
            {
                id: 'inp' + index,
                label: (
                    <Tooltip content={inp.pointer_type}>
                        {(<div style={{ fontFamily: 'monospace' }} onClick={() => (this.props.commandHandler("trace " + inp.name))}>
                            {inp.name}
                        </div>)}
                    </Tooltip>
                ),
                hasCaret: false,
                icon: this.showIOPointerFlag(inp, index, true)

            }
        )
        );

        let outputElements = this.state.outputs.map((out, index) =>
        (
            {
                id: 'out' + index,
                label: (
                    <Tooltip content={out.pointer_type}>
                        {(<div style={{ fontFamily: 'monospace' }} onClick={() => (this.props.commandHandler("trace " + out.name))}>
                            {out.name}
                        </div>)}
                    </Tooltip>
                ),
                hasCaret: false,
                icon: this.showIOPointerFlag(out, index, false)
            }
        )
        );

        let inputElement = {
            id: 'inputElement',
            label: <b>Inputs</b>,
            hasCaret: true,
            disabled: false,
            isExpanded: this.state.showInputs,
            childNodes: inputElements
        };
        let outputElement = {
            id: 'outputElement',
            label: <b>Outputs</b>,
            hasCaret: true,
            disabled: false,
            isExpanded: this.state.showOutputs,
            childNodes: outputElements
        };

        let description = info.description ? info.description : "no description found";

        return (
            < div >
                <Tooltip
                    content={"Description: " + description}
                    className={Classes.TOOLTIP_INDICATOR}
                    position={Position.RIGHT}
                >
                    {(<h2 onClick={() => (this.props.commandHandler("history " + info.component_name))}>{info.component_name}</h2>)}
                </Tooltip>
                {countContent}
                {stale}
                <HTMLTable bordered={false} interactive={false} className='bp3-minimal'>
                    <thead>
                        <tr>
                            <th style={{ paddingLeft: '0px' }}>Run ID: {this.props.id}</th>
                            <th>{tagElements}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style={{ paddingLeft: '0px' }}> <b>Started: </b>{info.start_timestamp} </td>
                            <td><b>Git commit: </b>{commit}</td>
                        </tr>
                        <tr>
                            <td style={{ paddingLeft: '0px' }}> <b>Owner:</b> {info.owner} </td>
                            <td><b>Duration: </b> {((end - start) / 1000) + 's'}</td>
                        </tr>
                    </tbody>
                </HTMLTable>
                <Tree
                    contents={[inputElement, outputElement]}
                    onNodeExpand={this.onNodeToggle}
                    onNodeCollapse={this.onNodeToggle}
                    style={{ margin: '1.5em 0em' }}
                />
                <div style={{ margin: '1.5em 0em' }}>
                    <Button className="bp3-minimal" outlined={true} onClick={this.handleClick}>{this.state.showCode ? "Hide" : "Show"} code snapshot </Button>
                    <Collapse isOpen={this.state.showCode} keepChildrenMounted={true} className='bp3-minimal'>
                        <Pre>
                            {codeSnapshot}
                        </Pre>
                    </Collapse>
                </div>
                <div style={{ marginTop: '0em' }}>
                    <h4><Icon icon="annotation" />  Notes</h4>
                    <EditableText
                        multiline={true}
                        minLines={2}
                        onConfirm={(e) => this.onFinishEditingText(this.props.id, e)}
                        defaultValue={this.state.notes}
                    />
                </div>
            </div >
        );
    }

}