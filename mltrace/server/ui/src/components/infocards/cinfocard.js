import React, { Component } from 'react';
import { Tag, Intent, Classes, Text, Button, Collapse, HTMLTable } from "@blueprintjs/core";

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const HISTORY_API_URL = '/history';

export default class CInfoCard extends Component {

    constructor(props) {
        super(props);

        this.state = {
            isOpen: false,
            renderedHistory: false,
            history: []
        }

        this._isMounted = false;
        this.handleClick = this.handleClick.bind(this);
    }

    componentDidMount() {
        this._isMounted = true;
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    handleClick() {
        this.setState({ isOpen: !this.state.isOpen });
    }

    componentDidUpdate() {
        if (this.state.renderedHistory === true) return;

        axios.get(HISTORY_API_URL, {
            params: {
                component_name: this.props.src.name
            }
        }).then(
            ({ data }) => {
                this._isMounted && this.setState({ history: data, renderedHistory: true });
            }
        ).catch(e => {
            console.log(e);
            // this.setState({ output_id: this.props.output_id });
        });
    }

    render() {
        let info = this.props.src;
        let description = info.description ? info.description : "no description found";
        let tagElements = info.tags.map((name, index) => {
            return (
                <Tag
                    minimal={true}
                    onClick={() => (this.props.tagHandler("tag " + name))}
                    intent={Intent.PRIMARY}
                    style={{ marginRight: '0.5em', marginTop: '1.5em' }}
                    key={index}
                    interactive={true}>
                    {name}
                </Tag>)
        });
        let runElements = this.state.history.map((cr, index) => {
            let end = new Date(cr.end_timestamp);
            let start = new Date(cr.start_timestamp);
            var outputs = cr.outputs.map((elem) => (String(elem.name)));
            outputs = String(outputs.join(', '));

            return (
                <tr key={'componentrun_' + index}>
                    <td>{cr.id}</td>
                    <td>{cr.start_timestamp}</td>
                    <td>{(end - start) / 1000}sec</td>
                    <td style={{ fontFamily: 'monospace' }}>
                        <Text ellipsize={true}>
                            {outputs}
                        </Text>
                    </td>
                </tr>
            )
        });

        return (
            <div>
                <h2>{info.name}</h2>
                <h4>Owner: {info.owner}</h4>
                <Text className={Classes.MINIMAL}>Description: {description}</Text>
                <div className='bp3-minimal' style={{ marginTop: '1em' }}>
                    <Button onClick={this.handleClick} className='bp3-minimal' outlined={true}>
                        {this.state.isOpen ? "Hide" : "Show"} recent runs
                    </Button>
                    <Collapse isOpen={this.state.isOpen} className='bp3-minimal'>
                        <HTMLTable bordered={true} interactive={true} style={{ marginTop: '1em' }}>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Start time</th>
                                    <th>Duration</th>
                                    <th>Outputs</th>
                                </tr>
                            </thead>
                            <tbody>
                                {runElements}
                            </tbody>
                        </HTMLTable>
                    </Collapse>
                </div>
                <div className='bp3-minimal'>
                    {tagElements}
                </div>
            </div>
        )
    }

}