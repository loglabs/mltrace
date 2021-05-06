import React, { Component } from 'react';
import { Intent } from "@blueprintjs/core";
import { CustomToaster } from "../components/toaster.js";

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import InfoCard from '../components/infocard.js';

const RECENT_API_URL = '/recent';

export default class Recent extends Component {

    constructor(props) {
        super(props);
        this.state = {
            componentRuns: null,
        }
    }

    componentDidMount() {
        // Ping API if this.props.render

        if (this.props.render === false) return;

        axios.get(RECENT_API_URL, {
            params: {
                limit: this.props.kwargs.limit,
            }
        }).then(
            ({ data }) => {
                this.setState({ componentRuns: data });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
        });
    }

    componentDidUpdate() {
        if (this.props.render === false && this.state.componentRuns === null) {
            return;
        }

        if (this.props.render === false) {
            this.setState({ componentRuns: null });
            return;
        }

        if (this.state.componentRuns !== null) {
            return;
        }

        axios.get(RECENT_API_URL, {
            params: {
                limit: this.props.kwargs.limit,
            }
        }).then(
            ({ data }) => {
                this.setState({ componentRuns: data });
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

        console.log(this.state.componentRuns);

        if (this.state.componentRuns === null || this.state.componentRuns.length === 0) return null;

        let childStyle = {
            flex: '0',
            margin: '1em',
            // paddingRight: '10em'
        }

        let componentRunCards = this.state.componentRuns.map((crId) => (
            <InfoCard key={'crcard_' + crId} selected_id={'componentrun_' + crId} commandHandler={this.props.commandHandler} style={childStyle} />

        ));

        return (
            <div className='bp3-minimal' style={{ paddingBottom: '1em' }}>
                <div style={{ display: 'flex', margin: '1em' }}>
                    <h3> Recent runs
                    </h3>
                </div >
                {componentRunCards}
            </div>
        );

    }


}