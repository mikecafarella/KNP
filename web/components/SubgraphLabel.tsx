import React, { useState, useEffect} from 'react'
import { Autocomplete, TextInput, Combobox, Button, Tooltip, Dialog, Popover, Overlay, Pane} from 'evergreen-ui'
// import { flex } from 'ui-box';
const SubgraphLabel: React.FC<{
    selectedSubgraphNodes: any[], 
    setSelectedSubgraphNodes: (selectedSubgraphNodes: any[]) => void,
    label: string, 
    setLabel: (label: string)=>void,
    makeOwnLabel: boolean,
    setMakeOwnLabel: (makeOwnLabel: boolean)=>void,
    customLabel: string,
    setCustomLabel: (customLabel: string) => void,
    dobjID: string,
    rootNodeName: string,

}> = ({selectedSubgraphNodes, setSelectedSubgraphNodes, label, setLabel, makeOwnLabel, setMakeOwnLabel, customLabel, setCustomLabel, dobjID, rootNodeName}) => {
    // we would replace this with an API call to get a good set of labels to autocomplete
    // should be put in knownlocation[id].tsx in get serverside props potentially as well
    const subgraphsUrl = '/api/subgraphs/' + dobjID;
    const submitSubgraph = async () => {
        let subgraphLabel = (customLabel) ? customLabel: label;
        let selectedNodes = [...selectedSubgraphNodes].sort();
        await fetch(subgraphsUrl, {
            method: "POST",
            body: JSON.stringify({
                "uuid": dobjID,
                'subgraphNodeMD5s': selectedNodes,
                'label': subgraphLabel,
                'subgraphRootName': rootNodeName,
            }),
        });
        setLabel('');
        setSelectedSubgraphNodes([]);
        if (customLabel) {
            exitDialog();
        }
    }
    let items = ['Test', 'Jest', 'Rest', 'Teests', 'Jeeps'];
    const submitLabelButton = (label) ? <Button onClick={submitSubgraph} >Submit Subgraph Label</Button> : <></>
    const exitDialog = () => {
        setMakeOwnLabel(false);
        setCustomLabel('');
    }
    return (
        <>
            <Autocomplete
                title="Label"
                onChange={changedItem => setLabel(changedItem)}
                items={items}
                >
                {props => {
                    const { getInputProps, getRef, inputValue, openMenu } = props
                    return (
                        <TextInput
                        placeholder="Label"
                        value={inputValue}
                        ref={getRef}
                        {...getInputProps({
                            onFocus: () => {
                            openMenu()
                            }
                        })}
                        />
                    )
                }}
            </Autocomplete>
            {submitLabelButton}
            <Dialog
                isShown={makeOwnLabel}
                title="Submit Your Own Label"
                onCloseComplete={exitDialog}
                confirmLabel="Submit Your Label"
                onConfirm={submitSubgraph}
                width={350}
            >
                <TextInput onChange={e => setCustomLabel(e.target.value)}/>
            </Dialog>
            <Button appearance='minimal' onClick={()=>setMakeOwnLabel(true)}>Submit Your Own Label </Button>
            {/* We can use this button later on to generate code for a specific label */}
            {/* <Button 
                onClick={() => console.log('clicked')}
                disabled={!label}
            >Label Subgraph
            </Button> */}
        </>
    )
}



export default SubgraphLabel