import React, { Component } from 'react';
import { CustomToaster } from "../components/toaster.js";
import { HTMLTable, Intent, Tooltip, Classes } from "@blueprintjs/core";
import InfoCard from '../components/infocard.js';

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import "@blueprintjs/datetime/lib/css/blueprint-datetime.css";

const REVIEW_API_URL = 'api/review';

export default class Review extends Component {

    constructor(props) {
        super(props);

        this.state = {
            idsAndCrs: null,
        }
    }

    componentDidUpdate() {
        if (this.props.render === false && this.state.idsAndCrs === null) {
            return;
        }

        if (this.props.render === false) {
            this.setState({ idsAndCrs: null });
            return;
        }

        if (this.state.idsAndCrs !== null) {
            return;
        }

        axios.get(REVIEW_API_URL, {
        }).then(
            ({ data }) => {
                this.setState({ idsAndCrs: data });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
        });
    }

    render() {
        if (this.props.render === false) return null;

        if (this.state.idsAndCrs === null || this.state.idsAndCrs.length === 0) return null;

        let childStyle = {
            flex: '0',
            margin: '1em',
            // paddingRight: '10em'
        }

        let outputIds = this.state.idsAndCrs[0];
        let componentRuns = this.state.idsAndCrs[1];
        console.log(componentRuns);

        let componentRunCards = componentRuns.map((cr) => (
            <InfoCard key={'crcard_' + cr[0]} selected_id={'componentrun_' + cr[0]} commandHandler={this.props.commandHandler} style={childStyle} count={cr[1]} />

        ));

        let outputIdContents = outputIds.map((outputId) => (
            <tr onClick={() => { this.props.commandHandler("trace " + outputId) }}>
                <td>
                    {outputId}
                </td>
            </tr>
        ));

        let treeContent = (
            <div style={{ flex: '0 1 auto' }} className="bp3-minimal">
                <HTMLTable bordered={false} interactive={true} className='bp3-minimal'>
                    <thead>
                        <tr>
                            <th>
                                <Tooltip className={Classes.TOOLTIP_INDICATOR} content={"Click an output ID to trace it."}>
                                    {"Outputs"}
                                </Tooltip>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {outputIdContents}
                    </tbody>
                </HTMLTable>
            </div>
        );

        return (
            <div className='bp3-minimal' style={{ margin: '1em' }}>
                <div style={{ display: 'flex' }}>
                    <h3> Reviewing flagged outputs
                    </h3>
                </div >
                <div style={{ display: 'flex' }}>
                    {treeContent}
                    <div style={{ width: '100%' }}>
                        {componentRunCards}
                    </div>
                </div>
            </div>
        );
    }

}