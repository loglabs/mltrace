import React, { Component } from 'react';
import { Card, Intent, Classes } from "@blueprintjs/core";
import { CustomToaster } from "./toaster.js";
import CRInfoCard from './infocards/crinfocard.js';
// import IOInfoCard from './infocards/ioinfocard.js';

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const CR_API_URL = "/api/component_run";
const IO_API_URL = "/api/io_pointer";

export default class InfoCard extends Component {

    constructor(props) {
        super(props);

        this.state = {
            node: {},
            selected_id: '',
            type: null
        }

        this.updateState = this.updateState.bind(this);
        this._isMounted = false;
    }

    updateState() {
        if (this.state.selected_id === this.props.selected_id) return;

        if (this.props.selected_id === '') {
            this.setState({ selected_id: this.props.selected_id });
        }

        const splitId = this.props.selected_id.split(/_(.+)/);
        const type = splitId[0];
        const id = splitId[1];

        // Call API
        let url = '';
        if (type === 'componentrun') url = CR_API_URL;
        else if (type === 'iopointer') url = IO_API_URL;
        else return;

        axios.get(url, {
            params: {
                id: id
            }
        }).then(
            ({ data }) => {
                this._isMounted && this.setState({ node: data, selected_id: this.props.selected_id, type: type });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
            // this.setState({ selected_id: '', type: '' });
        });

    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    componentDidMount() {
        this._isMounted = true;
        this.updateState();
    }

    componentDidUpdate() {
        this.updateState();
    }

    render() {
        if (this.state.selected_id === '') return null;

        let cardContent = null;
        if (this.state.type === 'componentrun') {
            cardContent = <CRInfoCard commandHandler={this.props.commandHandler} src={this.state.node} id={this.state.selected_id === '' ? '' : this.state.selected_id.split(/_(.+)/)[1]} count={this.props.count} numOutputs={this.props.numOutputs} />
        } else if (this.state.type === 'iopointer') {
            cardContent = this.state.selected_id;
        }

        return (
            < Card style={this.props.style} className={Classes.MINIMAL} >
                {cardContent}
            </Card>
        );
    }


}