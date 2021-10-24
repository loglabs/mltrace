import React, { Component } from 'react';
import { CustomToaster } from "../components/toaster.js";
import { HTMLTable, Intent, Tooltip, Classes } from "@blueprintjs/core";
import InfoCard from '../components/infocard.js';

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import "@blueprintjs/datetime/lib/css/blueprint-datetime.css";

const REVIEW_API_URL = '/api/review';

export default class Review extends Component {

    constructor(props) {
        super(props);

        this.state = {
            idsAndCrs: null,
        }
    }

    componentDidMount() {
        this.updateReviewState();
    }

    componentDidUpdate() {
        this.updateReviewState();
    }

    updateReviewState() {
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

        let componentRunCards = componentRuns.map((cr) => (
            <InfoCard key={'crcard_' + cr[0]} selected_id={'componentrun_' + cr[0]} commandHandler={this.props.commandHandler} style={childStyle} count={cr[1]} numOutputs={outputIds.length} />

        ));

        let outputIdContents = outputIds.map((outputId) => (
            <tr onClick={() => { this.props.commandHandler("trace " + outputId) }} key={'output_' + outputId}>
                <td>
                    {outputId}
                </td>
            </tr>
        ));

        let treeContent = (
            <div style={{ minWidth: '15%', maxWidth: '40%', height: '100vh', overflow: 'scroll' }} className="bp3-minimal">
                <div style={{ 'minHeight': '100%' }}>
                    <HTMLTable bordered={false} interactive={true} className='bp3-minimal' style={{ width: '100%' }}>
                        <thead>
                            <tr>
                                <th>
                                    <Tooltip className={Classes.TOOLTIP_INDICATOR} content={"Click an output ID to trace it."}>
                                        {"All flagged outputs (" + outputIds.length + ")"}
                                    </Tooltip>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {outputIdContents}
                        </tbody>
                    </HTMLTable>
                </div>
            </div >
        );

        return (
            <div className='bp3-minimal' style={{ margin: '1em' }}>
                <div style={{ display: 'flex' }}>
                    {/* <div style={{ width: '20%' }}></div> */}
                    <div style={{ width: '100%', height: '100vh', overflow: 'scroll' }}>
                        <div style={{ display: 'flex' }}>
                            <h3 className="bp3-heading" style={{ margin: '1em 0.5em' }}>
                                <Tooltip className={Classes.TOOLTIP_INDICATOR} content={"ComponentRun panels are sorted from most frequently used to least frequently used in producing the flagged outputs."}>
                                    Component runs
                        </Tooltip>
                            </h3>
                        </div >
                        {componentRunCards}
                    </div>
                    {treeContent}
                </div>
            </div >
        );
    }

}