import React, { useState, useEffect} from 'react'
import { Autocomplete, TextInput, Combobox, Button, Tooltip, Dialog, Popover, Overlay, Pane} from 'evergreen-ui'
// import { flex } from 'ui-box';
const SubgraphLabel: React.FC<{
    subgraphNodeIds: any[], 
    label: string, 
    setLabel: (label: string)=>void,
    makeOwnLabel: boolean,
    setMakeOwnLabel: (makeOwnLabel: boolean)=>void,
    customLabel: string,
    setCustomLabel: (customLabel: string) => void

}> = ({subgraphNodeIds, label, setLabel, makeOwnLabel, setMakeOwnLabel, customLabel, setCustomLabel}) => {
    // we would replace this with an API call to get a good set of labels to autocomplete
    // should be put in knownlocation[id].tsx in get serverside props potentially as well
    let items = ['Test', 'Jest', 'Rest', 'Teests', 'Jeeps'];
    const submitLabelButton = (label) ? <Button onClick={()=>console.log(label)} >Submit Subgraph Label</Button> : <></>
    const exitDialog = () => {
        setMakeOwnLabel(false);
        setCustomLabel('');
    }
    return (
        <>
            {/* <Combobox
                items={items}
                onChange={selected => setLabel(selected)}
                placeholder="Choose a Subgraph Label"
                autocompleteProps={{
                    // Used for the title in the autocomplete.
                    title: 'Subgraph Label'
                }}
            /> */}
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
                    onConfirm={()=> console.log(customLabel)}
                    width={350}
                >
                    <TextInput onChange={e => setCustomLabel(e.target.value)}/>
                </Dialog>
                {/* <Overlay isShown={makeOwnLabel}> */}
                 <Button appearance='minimal' onClick={()=>setMakeOwnLabel(true)}>Submit Your Own Label </Button>
                {/* </Overlay> */}
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