import React, { Component } from 'react';
import { Tag, Intent, Classes, Text } from "@blueprintjs/core";

export default class CInfoCard extends Component {

    render() {
        let info = this.props.src;
        let description = info.description ? info.description : "no description found";
        let tagElements = info.tags.map((name, index) => {
            return (
                <Tag
                    minimal={true}
                    onClick={() => (this.props.tagHandler("tag " + name))}
                    intent={Intent.PRIMARY}
                    style={{ marginRight: '0.5em', marginTop: '1em' }}
                    key={index}
                    interactive={true}>
                    {name}
                </Tag>)
        });

        return (
            <div>
                <h2>{info.name}</h2>
                <h4>Owner: {info.owner}</h4>
                <Text className={Classes.MINIMAL}>Description: {description}</Text>
                {tagElements}
            </div>
        )
    }

}