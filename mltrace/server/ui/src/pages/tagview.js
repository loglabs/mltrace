import React, { Component } from 'react';
import { Intent, Card, Tag } from "@blueprintjs/core";
import { CustomToaster } from "../components/toaster.js";
import CInfoCard from '../components/infocards/cinfocard.js';

import axios from "axios";
import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

const TAG_API_URL = '/tag'

export default class TagView extends Component {

    constructor(props) {
        super(props);
        this.state = {
            tagName: '',
            components: []
        }
    }

    componentDidUpdate() {
        if (this.state.tagName === this.props.tagName) {
            return null;
        }

        if (this.props.tagName === "") {
            this.setState({ tagName: this.props.tagName, components: [] });
            return null;
        }

        axios.get(TAG_API_URL, {
            params: {
                id: this.props.tagName
            }
        }).then(
            ({ data }) => {
                this.setState({ components: data, tagName: this.props.tagName });
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
        if (this.state.tagName === '') return null;

        let childStyle = {
            flex: '0',
            margin: '1em',
            // paddingRight: '10em'
        }

        let renderedComponents = this.state.components.map((c) => (
            <Card key={'component' + c.name} style={childStyle}>
                <CInfoCard src={c} commandHandler={this.props.commandHandler} />
            </Card>
        ));

        return (
            <div className='bp3-minimal' style={{ maxWidth: '80%', paddingBottom: '1em' }}>
                <div style={{ display: 'flex', margin: '1em' }}>
                    <h3> Showing components with tag: <Tag intent={Intent.PRIMARY} minimal={true} large={true}>{this.state.tagName}</Tag>
                    </h3>
                </div >
                {renderedComponents}
            </div>
        );
    }
}