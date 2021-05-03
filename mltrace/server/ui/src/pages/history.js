import React, { Component } from 'react';
import { Intent, Card } from "@blueprintjs/core";
import { CustomToaster } from "../components/toaster.js";
import CInfoCard from '../components/infocards/cinfocard.js';

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const COMPONENT_API_URL = '/component';

export default class History extends Component {

    constructor(props) {
        super(props);
        this.state = {
            componentName: '',
            component: {},
            limit: undefined
        }
    }

    componentDidUpdate() {
        if (
            this.state.componentName === this.props.componentName &&
            (this.props.kwargs.limit === undefined || this.props.kwargs.limit === null || this.props.kwargs.limit === this.state.limit)
        ) {
            return null;
        }

        if (this.props.componentName === "") {
            this.setState({ componentName: this.props.componentName, component: {}, limit: this.props.kwargs.limit });
            return null;
        }

        axios.get(COMPONENT_API_URL, {
            params: {
                id: this.props.componentName,
            }
        }).then(
            ({ data }) => {
                this.setState({ componentName: this.props.componentName, component: data, limit: this.props.kwargs.limit });
            }
        ).catch(e => {
            CustomToaster.show({
                message: e.message,
                icon: "error",
                intent: Intent.DANGER,
            });
            // this.setState({ output_id: this.props.output_id });
        });

    }

    render() {
        if (this.state.componentName === '') return null;

        let childStyle = {
            flex: '0',
            margin: '1em',
            // paddingRight: '10em'
        }


        let renderedComponent = (
            <Card style={childStyle}>
                <CInfoCard src={this.state.component} commandHandler={this.props.commandHandler} showHistoryOnLoad={true} limit={this.state.limit} />
            </Card>
        );

        return (
            <div className='bp3-minimal' style={{ paddingBottom: '1em' }}>
                <div style={{ display: 'flex', margin: '1em' }}>
                    <h3> Showing history for component:
                    </h3>
                </div >
                {renderedComponent}
            </div>
        );
    }
}