import React, {useEffect , useState} from 'react'
import { Autocomplete, TextInput, Button, Dialog, SelectMenu} from 'evergreen-ui'
import { SubgraphProps, SubgraphNodeProps } from './KnownLocation';
import { arrayEquals, getSelectedSubgraphInfo } from './Utils';
import { useSession } from 'next-auth/client'

// see the knownlocations component for explanation of state props
const SubgraphLabel: React.FC<{
    validSubgraph: boolean,
    selectedSubgraphNodes: any[], 
    setSelectedSubgraphNodes: (selectedSubgraphNodes: any[]) => void,
    selectedLabeledSubgraph: SubgraphNodeProps,
    setSelectedLabeledSubgraph: (selectedLabeledSubgraph: SubgraphNodeProps) => void,
    labeledSubgraphs: SubgraphProps,
    setLabeledSubgraphs: (labeledSubgraphs: SubgraphProps) => void,
    label: string, 
    setLabel: (label: string)=>void,
    makeOwnLabel: boolean,
    setMakeOwnLabel: (makeOwnLabel: boolean)=>void,
    customLabel: string,
    setCustomLabel: (customLabel: string) => void,
    dobjID: string,
    rootNodeName: string,
    selectedLabeledSubgraphRootNode: string,
    setSelectedLabeledSubgraphRootNode: (selectedLabeledSubgraphRootNode: string) => void,
    selectedLabeledSubgraphLabel: string,
    setSelectedLabeledSubgraphLabel: (selectedLabeledSubgraphLabel: string) => void,
    selectedLabeledSubgraphId: string, 
    setSelectedLabeledSubgraphId: (selectedLabeledSubgraphId: string) => void,
    rootNodeFileName: string,
    autompleteItems: any[],
    setAutocompleteItems: (autocompleteItems: any[]) => void,
    subgraphRootId: string,
}> = ({validSubgraph, 
       selectedSubgraphNodes, setSelectedSubgraphNodes, 
       labeledSubgraphs, setLabeledSubgraphs, 
       label, setLabel, 
       makeOwnLabel, setMakeOwnLabel, 
       customLabel, setCustomLabel, 
       dobjID, 
       rootNodeName,
       selectedLabeledSubgraph, setSelectedLabeledSubgraph,
       selectedLabeledSubgraphRootNode, setSelectedLabeledSubgraphRootNode,
       selectedLabeledSubgraphLabel, setSelectedLabeledSubgraphLabel,
       selectedLabeledSubgraphId, setSelectedLabeledSubgraphId,
       rootNodeFileName,
       autompleteItems, setAutocompleteItems,
       subgraphRootId,
    }) => {
    const subgraphsUrl = '/api/subgraphs';
    const [session, loading] = useSession();
    const handleResetLabeledSelection = () => {
        setSelectedLabeledSubgraphRootNode('');
        setSelectedLabeledSubgraphLabel('');
        setSelectedLabeledSubgraphId('');
        setSelectedLabeledSubgraph(null);
        setLabel('');
        setAutocompleteItems([]);
        if (selectedSubgraphNodes) {
            setSelectedSubgraphNodes([]);
        }
        // Don't need to reset the custom label because closing the dialog component does that for us
    }
    // we currently check thru all possible labeled subgraphs and do an array equality check to see if we have previously 
    // labeled a set of nodes
    const haveLabeledInThePast = () => {
        // refactor to just being a list filter potentially, but this is a full stack change
        let selectedNodes = selectedSubgraphNodes.map(nd=>nd.uuid).sort();
        for (let rootNodeName of Object.keys(labeledSubgraphs)) {
            for (let labelName of Object.keys(labeledSubgraphs[rootNodeName])) {
                // let subgraphInfos: SubgraphNodeProps[] = labeledSubgraphs[rootNodeName][labelName]
                for (let uuid of Object.keys(labeledSubgraphs[rootNodeName][labelName])) {
                    let subgraphNode : SubgraphNodeProps = labeledSubgraphs[rootNodeName][labelName][uuid];
                    if (arrayEquals(subgraphNode.subgraphNodeUUIDs, selectedNodes)) {
                        return {labeledInPast: true, oldLabel: subgraphNode.label};
                    }
                }
            }
        }
        return {labeledInPast: false, oldLabel: 'invalid'};
    }

    const fetcher = async (url) => {
        let selectedNodes = selectedSubgraphNodes.filter(nd => nd.kind === "FileObservation");
        let data = await fetch(url, {
            method: "PUT",
            body: JSON.stringify({selectedNodes, subgraphRootId})
        }).then(res=>res.json())
        setAutocompleteItems(data);
        return data;   
    }


    useEffect(() => {
        if (validSubgraph) {
            fetcher(`${subgraphsUrl}/${dobjID}`)
        } else {
            setAutocompleteItems([]);
        }
    }, [selectedSubgraphNodes]);

    const labeledInThePastObj = haveLabeledInThePast();

    const submitSubgraph = async () => {
        let subgraphLabel = (customLabel) ? customLabel: label;
        // this sort call is important, but we can just as easily do this in the backend

        let sorted = selectedSubgraphNodes.sort((a, b) => {
            if (a.uuid < b.uuid) {
                return -1
            } else if (a.uuid > b.uuid) {
                return 1;
            }
            return 0;
        });

        let selectedNodes = sorted.map(nd=>nd.uuid);
        let res; 
        if (labeledInThePastObj.labeledInPast || selectedLabeledSubgraph) {
            if (selectedLabeledSubgraph) {
                selectedNodes = selectedLabeledSubgraph.subgraphNodeUUIDs;
            }
            let oldLabel = (selectedLabeledSubgraph) ? selectedLabeledSubgraphLabel: labeledInThePastObj.oldLabel
            res = await fetch(`${subgraphsUrl}/${dobjID}`, {
                method: "PATCH",
                body: JSON.stringify({
                    "uuid": dobjID,
                    "subgraphNodeUUIDs": selectedNodes,
                    "oldLabel": oldLabel,
                    "newLabel": subgraphLabel,
                    "username": session.user.name,
                    "email": session.user.email,
                }),
            }).then(res=>res.json());
        } else {
            res = await fetch(`${subgraphsUrl}/${dobjID}`, {
                method: "POST",
                body: JSON.stringify({
                    "subgraphRootId": subgraphRootId,
                    'subgraphNodeUUIDs': selectedNodes,
                    'label': subgraphLabel,
                    'subgraphRootName': rootNodeName,
                    'username': session.user.name,
                    'email': session.user.email,
                    'rootNodeFileName': rootNodeFileName,
                    'uuid': dobjID,
                    'subgraphNodesInfo': sorted,
                }),
            }).then(res => res.json());
        }
        setLabeledSubgraphs(res.subgraphs);
        if (selectedLabeledSubgraph && Object.keys(selectedLabeledSubgraph).length > 0) {
            handleResetLabeledSelection();
        }
        setLabel('');
        setSelectedSubgraphNodes([]);
        if (customLabel) {
            exitDialog();
        }
    }

    const submitLabelButton = (label) ? 
        <Button 
            onClick={submitSubgraph}>
            {(labeledInThePastObj.labeledInPast || selectedLabeledSubgraph) ? "Update Subgraph Label " : "Submit Subgraph Label"}
        </Button> : 
        <></>;
    const exitDialog = () => {
        setMakeOwnLabel(false);
        setCustomLabel('');
    }

    const handleResetUserSelection = () => {
        setSelectedSubgraphNodes([]);
        setLabel('');
        setAutocompleteItems([]);
    }        
    const labelComponent = (validSubgraph || selectedLabeledSubgraph) ? 
        <>
            <Autocomplete
                title="Label"
                onChange={changedItem => setLabel(changedItem)}
                items={autompleteItems}
                >
                {props => {
                    const { getInputProps, getRef, inputValue, openMenu } = props
                    return (
                        <>
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
                            <Button onClick={handleResetUserSelection} disabled={selectedSubgraphNodes.length === 0 || selectedLabeledSubgraph}>Clear your Current Subgraph Selection</Button>
                        </>
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
            <Button appearance='minimal' onClick={()=>setMakeOwnLabel(true)}>{(labeledInThePastObj.labeledInPast || selectedLabeledSubgraph)? "Update Label with Your Own Label" : "Submit Your Own Label" }</Button>

        </>
        :
        <> </>;


    const handleSelectedLabelSelection = (item) => {
        //refactor potentially for more performance, full stack change
        setSelectedLabeledSubgraphLabel(item.value);
        if (Object.keys(labeledSubgraphs[selectedLabeledSubgraphRootNode][item.value]).length === 1) {
            let uuid = Object.keys(labeledSubgraphs[selectedLabeledSubgraphRootNode][item.value])[0]
            let node: SubgraphNodeProps = labeledSubgraphs[selectedLabeledSubgraphRootNode][item.value][uuid];
            setSelectedLabeledSubgraph(node);
            setSelectedSubgraphNodes(getSelectedSubgraphInfo(node));
        }
        // reset state dependency, more detailed comment on line 237
        if (selectedLabeledSubgraphId) {
            setSelectedLabeledSubgraphId('');
        }
    }

    const handleSelectedIdSelection = (item) => {
        setSelectedLabeledSubgraphId(item.value);
        let node: SubgraphNodeProps = labeledSubgraphs[selectedLabeledSubgraphRootNode][selectedLabeledSubgraphLabel][item.value];
        setSelectedLabeledSubgraph(node);
        setSelectedSubgraphNodes(getSelectedSubgraphInfo(node));
    }

    //we show this if there are previously labeled subgraphs and the user is not attempting to select a subgraph
    const subgraphRootMenu = (Object.keys(labeledSubgraphs).length > 0) ? 
    <SelectMenu 
        title="Subgraph Root Node"
        options={Object.keys(labeledSubgraphs).map((label) => ({ label, value: label }))}
        selected={selectedLabeledSubgraphRootNode}
        onSelect={(item) => {
            setSelectedLabeledSubgraphRootNode(item.value);
            //if we choose a new root, we must update the two dependencies after for a selection component
            if (selectedLabeledSubgraphLabel) {
                setSelectedLabeledSubgraphLabel('');
            }
            if (selectedLabeledSubgraphId) {
                setSelectedLabeledSubgraphId('');
            }
        }}>
            <Button >{selectedLabeledSubgraphRootNode || "Select Root Node for Subgraph..."}</Button>
    </SelectMenu> :
    <></>;
    
    // only show this is the user chose which root node to view subgraphs for
    const subgraphLabelMenu = (selectedLabeledSubgraphRootNode) ?
    <SelectMenu 
        title="Subgraph Label"
        options={Object.keys(labeledSubgraphs[selectedLabeledSubgraphRootNode]).map((label) => ({ label, value: label }))}
        selected={selectedLabeledSubgraphLabel}
        onSelect={handleSelectedLabelSelection}
    >
        <Button>{selectedLabeledSubgraphLabel || "Select Label For Subgraph..."}</Button>
    </SelectMenu> :
    <> </>;

    let length = 0;
    if (selectedLabeledSubgraphLabel && selectedLabeledSubgraphRootNode) {
        try {
            length = Object.keys(labeledSubgraphs[selectedLabeledSubgraphRootNode][selectedLabeledSubgraphLabel]).length;
            // this is admittedly very hacky, there's an issue with the state being reset after submitting a label
        }  catch (TypeError) {
            length = 0;
            handleResetLabeledSelection();
        }      
    }

    const subgraphLabelId = (selectedLabeledSubgraphLabel && selectedLabeledSubgraphRootNode && (length > 1)) ? 
    <SelectMenu 
        title="Subgraph Label Graph UUID"
        options={Object.keys(labeledSubgraphs[selectedLabeledSubgraphRootNode][selectedLabeledSubgraphLabel]).map((node)=> {
            let label = node;
    
            return {label, value: label};
        })}
        selected={selectedLabeledSubgraphId}
        onSelect={handleSelectedIdSelection}
        width={300}
    >
        <Button>{selectedLabeledSubgraphId || "Select UUID For Subgraph..."}</Button>
    </SelectMenu> :
    <> </>;


    return (
        <>
        {subgraphRootMenu}
        {subgraphLabelMenu}
        {subgraphLabelId}
        {/* This condition is there so we can clear early in the selection process */}
        {(Object.keys(labeledSubgraphs).length > 0) ?
            <Button 
                onClick={handleResetLabeledSelection} 
                disabled={!selectedLabeledSubgraphRootNode}
            >
                Clear Current Labeled Subgraph Selection
            </Button> :
            <></>}
        {labelComponent}
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