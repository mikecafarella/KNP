import React, {useEffect} from 'react'
import { Autocomplete, TextInput, Button, Dialog, SelectMenu} from 'evergreen-ui'
import { SubgraphProps, SelectedLabeledGraph, SubgraphNodeProps } from './KnownLocation';
import { arrayEquals } from './Utils';
import { useSession } from 'next-auth/client'

// see the knownlocations component for explanation of state props
const SubgraphLabel: React.FC<{
    validSubgraph: boolean,
    selectedSubgraphNodes: any[], 
    setSelectedSubgraphNodes: (selectedSubgraphNodes: any[]) => void,
    selectedLabeledSubgraph: SelectedLabeledGraph,
    setSelectedLabeledSubgraph: (selectedLabeledSubgraph: SelectedLabeledGraph) => void,
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
    selectedLabeledSubgraphIndexNum: string, 
    setSelectedLabeledSubgraphIndexNum: (selectedLabeledSubgraphIndexNum: string) => void,
    rootNodeFileName: string,
    predefinedRoot?: string,
    predefinedLabel?: string,
    predefinedIndexNum? : number,
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
       selectedLabeledSubgraphIndexNum, setSelectedLabeledSubgraphIndexNum,
       rootNodeFileName,
       predefinedRoot,
       predefinedLabel,
       predefinedIndexNum,
    }) => {
    const subgraphsUrl = '/api/subgraphs/' + dobjID;
    const [session, loading] = useSession();
    const handleResetLabeledSelection = () => {
        setSelectedLabeledSubgraphRootNode('');
        setSelectedLabeledSubgraphLabel('');
        setSelectedLabeledSubgraphIndexNum(null);
        setSelectedLabeledSubgraph(null);
        setLabel('');
        // Don't need to reset the custom label because closing the dialog component does that for us
    }
    // we currently check thru all possible labeled subgraphs and do an array equality check to see if we have previously 
    // labeled a set of nodes
    const haveLabeledInThePast = () => {
        // refactor to just being a list filter potentially, but this is a full stack change
        let selectedNodes = [...selectedSubgraphNodes].sort();
        for (let rootNodeName of Object.keys(labeledSubgraphs)) {
            for (let labelName of Object.keys(labeledSubgraphs[rootNodeName])) {
                let subgraphInfos: SubgraphNodeProps[] = labeledSubgraphs[rootNodeName][labelName]
                for (let subgraphInfo of subgraphInfos) {
                    if (arrayEquals(subgraphInfo.subgraphNodeMD5s, selectedNodes)) {
                        return {labeledInPast: true, oldLabel: subgraphInfo.label};
                    }
                }
            }
        }
        return {labeledInPast: false, oldLabel: 'invalid'};
    }

    useEffect(() => {
        if (predefinedIndexNum && predefinedLabel && predefinedRoot) {
            const selected = {
                "subgraphNodeMD5s":labeledSubgraphs[predefinedRoot][predefinedLabel][predefinedIndexNum].subgraphNodeMD5s,
                "rootNode":labeledSubgraphs[predefinedRoot][predefinedLabel][predefinedIndexNum].subgraphRootName,
            }
            setSelectedLabeledSubgraph(selected);
            setSelectedLabeledSubgraphRootNode(predefinedRoot);
            setSelectedLabeledSubgraphLabel(predefinedLabel);
            setSelectedLabeledSubgraphIndexNum(predefinedIndexNum.toString());

        }
    }, []);

    const labeledInThePastObj = haveLabeledInThePast();

    const submitSubgraph = async () => {
        let subgraphLabel = (customLabel) ? customLabel: label;
        // this sort call is important, but we can just as easily do this in the backend
        let selectedNodes = [...selectedSubgraphNodes].sort();
        let res; 
        if (labeledInThePastObj.labeledInPast || selectedLabeledSubgraph) {
            if (selectedLabeledSubgraph) {
                selectedNodes = selectedLabeledSubgraph.subgraphNodeMD5s;
            }
            let oldLabel = (selectedLabeledSubgraph) ? selectedLabeledSubgraphLabel: labeledInThePastObj.oldLabel
            res = await fetch(subgraphsUrl, {
                method: "PUT",
                body: JSON.stringify({
                    "uuid": dobjID,
                    "subgraphNodeMD5s": selectedNodes,
                    "oldLabel": oldLabel,
                    "newLabel": subgraphLabel,
                    "username": session.user.name,
                    "email": session.user.email,
                }),
            }).then(res=>res.json());
        } else {
            res = await fetch(subgraphsUrl, {
                method: "POST",
                body: JSON.stringify({
                    "uuid": dobjID,
                    'subgraphNodeMD5s': selectedNodes,
                    'label': subgraphLabel,
                    'subgraphRootName': rootNodeName,
                    'username': session.user.name,
                    'email': session.user.email,
                    'rootNodeFileName': rootNodeFileName,
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
    //TODO: replaced with API call to recommended labels
    let items = ['Test', 'Jest', 'Rest', 'Teests', 'Jeeps'];

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
    }        
    const labelComponent = (validSubgraph || selectedLabeledSubgraph) ? 
        <>
            <Autocomplete
                title="Label"
                onChange={changedItem => setLabel(changedItem)}
                items={items}
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
                            <Button onClick={handleResetUserSelection} disabled={selectedSubgraphNodes.length === 0}>Clear your Current Subgraph Selection</Button>
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
        if (labeledSubgraphs[selectedLabeledSubgraphRootNode][item.value].length === 1) {
            const selected = {
                "subgraphNodeMD5s":labeledSubgraphs[selectedLabeledSubgraphRootNode][item.value][0].subgraphNodeMD5s,
                "rootNode":labeledSubgraphs[selectedLabeledSubgraphRootNode][item.value][0].subgraphRootName
            }
            setSelectedLabeledSubgraph(selected);
        }
        // reset state dependency, more detailed comment on line 237
        if (selectedLabeledSubgraphIndexNum) {
            setSelectedLabeledSubgraphIndexNum('');
        }
    }

    const handleSelectedIndexNumSelection = (item) => {
        setSelectedLabeledSubgraphIndexNum(item.value);
        //refactor potentially for more performance, full stack change
        let indexNum = parseInt(item.value);
        const selected = {
            "subgraphNodeMD5s":labeledSubgraphs[selectedLabeledSubgraphRootNode][selectedLabeledSubgraphLabel][indexNum].subgraphNodeMD5s,
            "rootNode":labeledSubgraphs[selectedLabeledSubgraphRootNode][selectedLabeledSubgraphLabel][indexNum].subgraphRootName
        }
        setSelectedLabeledSubgraph(selected);
    }

    //we show this if there are previously labeled subgraphs and the user is not attempting to select a subgraph
    const subgraphRootMenu = (Object.keys(labeledSubgraphs).length > 0 && selectedSubgraphNodes.length === 0) ? 
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
            if (selectedLabeledSubgraphIndexNum) {
                setSelectedLabeledSubgraphIndexNum('');
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
            length = labeledSubgraphs[selectedLabeledSubgraphRootNode][selectedLabeledSubgraphLabel].length;
            // this is admittedly very hacky, there's an issue with the state being reset after submitting a label
        }  catch (TypeError) {
            length = 0;
            handleResetLabeledSelection();
        }      

    }
    // if there are more than one set of nodes for a root, we need to choose which index number to use 
    const subgraphLabelIndexNum = (selectedLabeledSubgraphLabel && selectedLabeledSubgraphRootNode && (length > 1)) ? 
    <SelectMenu 
        title="Subgraph Label Graph Num"
        options={Array.from(Array(length).keys()).map((num)=> {
            let label = num.toString();
            return {label, value: label};
        })}
        selected={selectedLabeledSubgraphIndexNum}
        onSelect={handleSelectedIndexNumSelection}
    >
        <Button>{selectedLabeledSubgraphIndexNum || "Select Number For Subgraph..."}</Button>
    </SelectMenu> :
    <> </>;


    return (
        <>
        {subgraphRootMenu}
        {subgraphLabelMenu}
        {subgraphLabelIndexNum}
        {/* This condition is there so we can clear early in the selection process */}
        {(selectedSubgraphNodes.length === 0 && Object.keys(labeledSubgraphs).length > 0) ?
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