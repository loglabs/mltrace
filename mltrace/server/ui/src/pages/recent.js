import React, { Component } from 'react';
import { Intent } from "@blueprintjs/core";
import { CustomToaster } from "../components/toaster.js";

import axios from "axios";
import debounce from 'lodash.debounce';
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';
import InfoCard from '../components/infocard.js';

const RECENT_API_URL = 'api/recent';

export default class Recent extends Component {

    constructor(props) {
        super(props);
        this.state = {
            componentRuns: null,
        }

        window.onscroll = debounce(() => {
            const {
                loadComponentRuns
            } = this;

            if (window.innerHeight + document.documentElement.scrollTop === document.documentElement.offsetHeight) {
                loadComponentRuns();
            }
        }, 100);
    }

    loadComponentRuns = () => {
        let params = {
            limit: this.props.kwargs.limit,
        };

        if (this.state.componentRuns !== null && this.state.componentRuns.length !== 0) {
            params.last_run_id = this.state.componentRuns[this.state.componentRuns.length - 1];
        }


        axios.get(RECENT_API_URL, {
            params: params
        }).then(
            ({ data }) => {

                if (this.state.componentRuns === null) {
                    this.setState({ componentRuns: data });
                }

                else {
                    this.setState({ componentRuns: this.state.componentRuns.concat(data) });
                }
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
        });
    }

    componentDidMount() {
        // Ping API if this.props.render

        if (this.props.render === false) return;

        this.loadComponentRuns();
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

        this.loadComponentRuns();
    }

    render() {

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
            <div className='bp3-minimal' style={{ margin: '1em' }}>
                <div style={{ display: 'flex' }}>
                    <h3 className="bp3-heading" style={{ margin: '1em 0.5em' }}>  Latest component runs
                    </h3>
                </div >
                {componentRunCards}
            </div>
        );

    }


}