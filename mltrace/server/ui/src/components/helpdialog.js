import React, { Component } from 'react';
import { HTMLTable, Dialog, Classes, Button } from "@blueprintjs/core";


export default class HelpDialog extends Component {

    constructor(props) {
        super(props);
        this.state = {
            isOpen: false
        }

        this.handleOpen = this.handleOpen.bind(this);
        this.handleClose = this.handleClose.bind(this);
    }

    handleOpen() {
        this.setState({ isOpen: true });
    }

    handleClose() {
        this.props.onHandleHelp();
        this.setState({ isOpen: false });
    }

    static getDerivedStateFromProps(props, state) {
        if (props.showHelp && !state.isOpen) {
            return { isOpen: true };
        }

        return null;
    }

    render() {
        return (
            <div>
                <Button className={Classes.MINIMAL} onClick={this.handleOpen} icon="help" text="" />
                <Dialog className={Classes.MINIMAL} icon="help" isOpen={this.state.isOpen} onClose={this.handleClose} title="Help">
                    <div className={Classes.DIALOG_BODY}>
                        <p> <strong>mltrace, version 0.1 command list </strong> </p>
                        <p> These commands are currently supported by the UI. Type <tt>help</tt> in the command bar to see this list. Press the <tt>esc</tt> key or click outside this dialog to close the dialog.</p>
                        <HTMLTable className={Classes.MINIMAL} interactive={false}>
                            <thead>
                                <tr>
                                    <th>Command</th>
                                    <th>Description</th>
                                    <th>Usage</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><tt>recent</tt></td>
                                    <td>Displays the most recent runs across all components. Also serves as the default or "home" page.</td>
                                    <td><tt>recent</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>history</tt></td>
                                    <td>Displays most recent runs for a given component name. Shows latest 10 runs by default, but you can specify the number of runs you want to see by appending a positive integer to the command.</td>
                                    <td><tt>history COMPONENT_NAME 15</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>inspect</tt></td>
                                    <td>Displays information such as inputs/outputs, code, git snapshot, owner, and more for a given component run ID.</td>
                                    <td><tt>inspect COMPONENT_RUN_ID</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>trace</tt></td>
                                    <td>Displays a trace of versioned steps that produced a given output.</td>
                                    <td><tt>trace OUTPUT_NAME</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>tag</tt></td>
                                    <td>Displays all components with the given tag name.</td>
                                    <td><tt>tag TAG_NAME</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>flag</tt></td>
                                    <td>Flags an output ID for further review. Necessary to see any results from the <tt>review</tt> command.</td>
                                    <td><tt>flag OUTPUT_ID</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>unflag</tt></td>
                                    <td>Unflags an output ID. Removes this output ID from any results from the <tt>review</tt> command.</td>
                                    <td><tt>unflag OUTPUT_ID</tt></td>
                                </tr>
                                <tr>
                                    <td><tt>review</tt></td>
                                    <td>Shows a list of output IDs flagged for review and the common component runs involved in producing the output IDs.</td>
                                    <td><tt>review</tt></td>
                                </tr>
                            </tbody>
                        </HTMLTable>
                    </div>
                    <div className={Classes.DIALOG_FOOTER}>
                        <div className={Classes.DIALOG_FOOTER_ACTIONS}>
                            <Button onClick={this.handleClose}>Close</Button>
                        </div>
                    </div>
                </Dialog>
            </div>
        )
    }

}