import React, { useState} from 'react'
import { Autocomplete, TextInput, Combobox, Button, Tooltip} from 'evergreen-ui'
// import { flex } from 'ui-box';
const SubgraphLabel: React.FC<{subgraphNodeIds: any[], label: string, setLabel: (string)=>void}> = ({subgraphNodeIds, label, setLabel}) => {
    // we would replace this with an API call to get a good set of labels to autocomplete
    let items = ['Test1', 'Test2', 'Test3', 'Test4'];

    return (
        <>
            <Combobox
                items={items}
                onChange={selected => setLabel(selected)}
                placeholder="Choose a Subgraph Label"
                autocompleteProps={{
                    // Used for the title in the autocomplete.
                    title: 'Subgraph Label'
                }}
            />
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