import React, { Component } from 'react';
import { Tag, Intent, Classes, Text, Button, Collapse, HTMLTable, Icon } from "@blueprintjs/core";

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import { withRouter, Link } from 'react-router-dom';
import { createBrowserHistory } from 'history'


// import { INTENT_DANGER } from '@blueprintjs/core/lib/esm/common/classes';
const history = createBrowserHistory();
const HISTORY_API_URL = '/api/history';

class CInfoCard extends Component {

    constructor(props) {
        super(props);

        this.state = {
            isOpen: false,
            history: [],
            componentName: '',
            limit: undefined,
            dateLower: undefined,
            dateUpper: undefined,
            url: undefined
        }

        this._isMounted = false;
        this.handleClick = this.handleClick.bind(this);
    }

    componentDidMount() {

        // set history if calling from history page
        if (this.props.showHistoryOnLoad === true) {
            let params = {
                component_name: this.props.src.name,
                limit: this.props.limit,
                date_lower: this.props.dateLower,
                date_upper: this.props.dateUpper
            };

            axios.get(HISTORY_API_URL, {
                params: params
            }).then(
                ({ data }) => {
                    this._isMounted && this.setState({ history: data, componentName: this.props.src.name, isOpen: true });
                }
            ).catch(e => {
                console.log(e);
                // this.setState({ output_id: this.props.output_id });
            });
        }
        this._isMounted = true;
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    handleClick() {
        this.setState({ isOpen: !this.state.isOpen });
    }


    render() {
        let info = this.props.src;
        history.listen(location => {
            if (location.action === "POP") {
                var args = location.pathname.split("/").filter(str => str !== "");
                this.props.commandHandler(args.join(" "));
            }
        });
        let description = info.description ? info.description : "no description found";
        let tagElements = info.tags.map((name, index) => {
            return (
                <Tag
                    minimal={true}
                    onClick={() => {
                        // this.props.history.push(`/tag/${name}`);
                        this.props.commandHandler("tag " + name);
                    }}
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
            outputs = String(outputs.join(','));
            var id =
                <div style={{ textAlign: 'right' }}>{cr.id}</div>;
            if (cr.stale !== undefined && cr.stale !== null && cr.stale.length >= 1) {
                id = (
                    <div>
                        <Icon icon="warning-sign" intent={Intent.WARNING} style={{ marginRight: '1em' }} />
                        {cr.id}
                    </div>
                )
            }

            return (
             
                    <tr key={'componentrun_' + index} 
                    onClick={() => {
                        this.props.history.push(`/inspect/${cr.id}`);
                        this.props.commandHandler("inspect " + cr.id);
                    }}>
                    {/* <Link to ={`/inspect/${cr.id}`}>   */}
                        <td>{id}</td>
                        {/* </Link> */}
                        <td>{cr.start_timestamp}</td>
                        <td>{(end - start) / 1000}sec</td>
                        <td style={{ fontFamily: 'monospace', maxWidth: '100%', wordWrap: 'break-word' }}>
                            {outputs}
                        </td>
                     </tr>

            )
        });

        return (
            <div>
                <h2>{info.name}</h2>
                <h4>Owner: {info.owner}</h4>
                <Text className={Classes.MINIMAL}>Description: {description}</Text>
                <div className='bp3-minimal' style={{ marginTop: '1em', maxWidth: '100%' }}>
                    <Button onClick={this.handleClick} className='bp3-minimal' outlined={true}>
                        {this.state.isOpen ? "Hide" : "Show"} recent runs
                    </Button>
                    <Collapse isOpen={this.state.isOpen} className='bp3-minimal' keepChildrenMounted={true} style={{ maxWidth: '100%', display: 'inline-block' }}>
                        <HTMLTable bordered={true} interactive={true} style={{ marginTop: '1em', maxWidth: '100%', display: 'inline-block', tableLayout: 'fixed' }}>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Start time</th>
                                    <th>Duration</th>
                                    <th>Outputs</th>
                                </tr>
                            </thead>
                            <tbody style={{ maxWidth: '100%' }}>
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

export default withRouter(CInfoCard);