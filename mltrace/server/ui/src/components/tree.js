import React, { Component } from 'react';
import { Classes, Tree } from "@blueprintjs/core";

import 'normalize.css/normalize.css';
import '@blueprintjs/icons/lib/css/blueprint-icons.css';
import '@blueprintjs/core/lib/css/blueprint.css';

export default class TreeView extends Component {
    render() {
        let nodes = [
            {
                hasCaret: true,
                label: "serve",
                id: '0',
                isExpanded: true,
                childNodes: [
                    {
                        hasCaret: false,
                        icon: 'code-block',
                        label: (<div style={{ fontFamily: 'monospace' }}>{"@register(component_name='serve', inputs=['preds.pq'], output_vars=['x'], endpoint=True)\\ndef serve(x):\\n    print(f'serving output {x}!')\\n"}</div>),
                        id: '1'
                    },
                    {
                        hasCaret: false,
                        icon: 'th-derived',
                        label: 'preds.pq',
                        id: '2',
                    },
                    {
                        hasCaret: true,
                        label: "inference",
                        id: '3',
                        isExpanded: true,
                        childNodes: [
                            {
                                hasCaret: false,
                                icon: 'th-derived',
                                label: 'features.pq',
                                id: '4',
                            },
                            {
                                hasCaret: false,
                                icon: 'function',
                                label: 'model.joblib',
                                id: '5',
                            },
                            {
                                hasCaret: true,
                                label: "training",
                                id: '6',
                                isExpanded: true,
                                childNodes: [
                                    {
                                        hasCaret: false,
                                        icon: 'th-derived',
                                        label: 'train_set.pq',
                                        id: '8',
                                    },
                                    {
                                        hasCaret: false,
                                        icon: 'th-derived',
                                        label: 'test_set.pq',
                                        id: '9',
                                    },
                                    {
                                        hasCaret: false,
                                        icon: 'code-block',
                                        label: (<div style={{ fontFamily: 'monospace', wordWrap: 'break-word' }}> {"@register(component_name='training', inputs=['train_set.pq', 'test_set.pq'], outputs=['model.joblib', 'metrics.txt'])\\ndef train():\\n    time.sleep(4)\\n    print(\"training model\")\\n"}</div>),
                                        id: '10'
                                    }
                                ]
                            },
                            {
                                hasCaret: true,
                                label: "etl",
                                id: '7',
                                isExpanded: true,
                                childNodes: [
                                    {
                                        hasCaret: false,
                                        icon: 'document',
                                        label: 'cleaning_criteria.txt',
                                        id: '11',
                                    },
                                    {
                                        hasCaret: false,
                                        icon: 'th-derived',
                                        label: 'raw_data.csv',
                                        id: '12',
                                    }
                                ]
                            }
                        ]
                    },

                ],
            },
        ];

        return (
            <Tree contents={nodes} className="bp3-minimal" />
        )
    }
}