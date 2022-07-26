
import React, { useState, useCallback, useEffect} from 'react'
import Router, {useRouter} from 'next/router'
import { readString } from 'react-papaparse';
import { majorScale, Pre, Popover, Dialog, Spinner, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table, Badge, Small } from 'evergreen-ui'
import Tree from 'react-d3-tree'
import MD5 from "crypto-js/md5";
import { isValidSubgraphKnownLocations, getUUID, getSelectedSubgraphInfo } from './Utils';
import SubgraphLabel from './SubgraphLabel';


export type FileProps = {
  fileid: string;
  filename: string;
  modified: string;
  owner: string;
  isLatest: number;
}

// TODO: types for more granular selection if that's what we want
export type SubgraphProps = {
  rootNodeName: SubgraphLabelProps,
}

export type SubgraphLabelProps = {
  graphLabelName: SubgraphNodeProps,
}

export type SubgraphNodeProps = {
  uuid: string;
  label: string;
  subgraphRootName: string;
  owner: string;
  subgraphNodeUUIDs: string[];
  modified: number;
  subgraphRootId: number;
  ownerEmail: string;
  fullRootFileName: string;
  provenanceGraphRootId: string;
  subgraphNodesInfo: string;
}

export type FileLogProps = {
  id: string;
  owner: string;
  filename: string;
  modified: string;
  synctime: string;
  prevId: string;
  nextId: string;
  isLatest: number;
  md5hash: string;
}

const FileLog: React.FC<{dobj: FileLogProps}> = ({dobj}) => {
  const bytesetLink = "/byteset/" + dobj.md5hash
  const datasetLink = "/dataset/" + (dobj.datasets.length > 0 ? dobj.datasets[0].uuid : "")
  const previousLink = "/filelog/" + dobj.prevId

  const actionNameMap = {
    'PLOT_PAPER_DATA': 'CREATE_BAR_CHART'
  }

  console.log(dobj)

  const hasForwardData = (dobj.forwardData && dobj.forwardData.children && dobj.forwardData.children[0] &&
    dobj.forwardData.children[0].children  && dobj.forwardData.children[0].children[0] && dobj.forwardData.children[0].children[0].id !== dobj.id
  )

  console.log(dobj.id, dobj.forwardData.children[0].children[0].id )

  const nextLink = hasForwardData ?  "/filelog/" + dobj.forwardData.children[0].children[0].id : ""
  let nextAction = hasForwardData ? dobj.forwardData.children[0].name : ""

  if (hasForwardData && actionNameMap[nextAction]) {
    nextAction = actionNameMap[nextAction]
  }

  const [highlightedNode, setHighlightedNode] = useState("")
  const [selectedNode, setSelectedNode] = useState("")
  // this is to let us know if in subgraph selection mode or not
  const [subgraphSelection, setSubgraphSelection] = useState(false);
  // these are the nodes selected by the user
  const [selectedSubgraphNodes, setSelectedSubgraphNodes] = useState([]);
  // these are label state components, one for suggested label and the other for user submitted label
  const [label, setLabel] = useState("");
  const [makeOwnLabel, setMakeOwnLabel] = useState(false);
  const [customLabel, setCustomLabel] = useState('');
  // this state is for previously labeled subgraphs
  const [labeledSubgraphs, setLabeledSubgraphs] = useState<SubgraphProps>(null);
  // this state is for the selected subgraph a user wants to see or update (previously labeled graphs)
  const [selectedLabeledSubgraph, setSelectedLabeledSubgraph] = useState<SubgraphNodeProps>(null);
  // the state here is for the select menus so the component knows which previously labeled subgraph a user wants to see
  const [selectedLabeledSubgraphRootNode, setSelectedLabeledSubgraphRootNode] = useState('');
  const [selectedLabeledSubgraphLabel, setSelectedLabeledSubgraphLabel] = useState('');
  const [selectedLabeledSubgraphId, setSelectedLabeledSubgraphId] = useState('');
  // this state is the result of an API call to the classifier
  const [autocompleteItems, setAutocompleteItems] = useState([]);

  const {query} = useRouter();

  const selectNode = (nodeDatum) => {
      if (nodeDatum.kind === 'SharingEvent') {
        return;
      }
      if (nodeDatum === selectedNode) {
        setSelectedNode('');
      } else {
        setSelectedNode(nodeDatum)
      }
  }
  console.log(selectedNode)

  const isSelected = (nodeDatum) => {
    if (nodeDatum.uuid) {
      return selectedNode.uuid === nodeDatum.uuid;
    } else {
      return MD5(nodeDatum.receivedOnOrBefore).toString() === MD5(selectedNode.receivedOnOrBefore).toString()
    }
  }

  const useCenteredTree = (defaultTranslate = { x: 0, y: 0 }) => {
    const [translate, setTranslate] = useState(defaultTranslate);
    const containerRef = useCallback((containerElem) => {
      if (containerElem !== null) {
        const { width, height } = containerElem.getBoundingClientRect();
        setTranslate({ x: width*.6,  y: height * 0.5 });
      }
    }, []);
    return [translate, containerRef];
  };

  const useCenteredTreeReversed = (defaultTranslate = { x: 100, y: 200 }) => {
    const [translateRev, setTranslate] = useState(defaultTranslate);
    const containerRef = useCallback((containerElem) => {
      if (containerElem !== null) {
        const { width, height } = containerElem.getBoundingClientRect();
        setTranslate({ x: width*.1,  y: height * 0.5 });
      }
    }, []);
    return [translateRev, containerRef];
  };

  const shouldHighlight = (nodeDatum) => {
    if (nodeDatum.uuid) {
      return highlightedNode === nodeDatum.uuid;
    } else {
      return highlightedNode === MD5(nodeDatum.receivedOnOrBefore).toString();
    }
  }

  const getSelectSubgraphButtonText  = () => {
    return (subgraphSelection) ? "Exit Subgraph Selection Mode" : "Enter Subgraph Selection Mode"
  }

  const highLightNode = (nodeDatum) => {
    if (nodeDatum.uuid) {
      setHighlightedNode(nodeDatum.uuid);
    } else {
      setHighlightedNode(MD5(nodeDatum.receivedOnOrBefore).toString());
      }
  }

  const partOfSubgraph = (nodeDatum) => {
    let selectedUUIDs = selectedSubgraphNodes.map(nd=>nd.uuid);
    return (selectedLabeledSubgraph && selectedLabeledSubgraph.subgraphNodeUUIDs.includes(getUUID(nodeDatum))) || (selectedUUIDs.includes(getUUID(nodeDatum)));
  }

  const [translate, containerRef] = useCenteredTree();
  const [translateRev, containerRefRev] = useCenteredTreeReversed();

  let isValidSubgraphObj = true //isValidSubgraphKnownLocations(selectedSubgraphNodes, dobj);
  let validSubgraph = isValidSubgraphObj.validSubgraph;
  let rootNodeName = isValidSubgraphObj.rootNode;
  let rootNodeLongName = isValidSubgraphObj.rootNodeLongName;
  let rootNodeId = isValidSubgraphObj.rootId;
  let labelBadge = (customLabel || label) ? <Badge color='blue'>{customLabel || label}</Badge> : '';

  const subGraphLabeling = (subgraphSelection) ?
    <Pane>
      <SubgraphLabel
        validSubgraph={validSubgraph}
        selectedSubgraphNodes={selectedSubgraphNodes}
        setSelectedSubgraphNodes={setSelectedSubgraphNodes}
        selectedLabeledSubgraph={selectedLabeledSubgraph}
        setSelectedLabeledSubgraph={setSelectedLabeledSubgraph}
        labeledSubgraphs={labeledSubgraphs}
        setLabeledSubgraphs={setLabeledSubgraphs}
        label={label}
        setLabel={setLabel}
        customLabel={customLabel}
        setCustomLabel={setCustomLabel}
        makeOwnLabel={makeOwnLabel}
        setMakeOwnLabel={setMakeOwnLabel}
        dobjID={dobj.id}
        rootNodeName={rootNodeName}
        selectedLabeledSubgraphId={selectedLabeledSubgraphId}
        setSelectedLabeledSubgraphId={setSelectedLabeledSubgraphId}
        selectedLabeledSubgraphLabel={selectedLabeledSubgraphLabel}
        setSelectedLabeledSubgraphLabel={setSelectedLabeledSubgraphLabel}
        selectedLabeledSubgraphRootNode={selectedLabeledSubgraphRootNode}
        setSelectedLabeledSubgraphRootNode={setSelectedLabeledSubgraphRootNode}
        rootNodeFileName={rootNodeLongName}
        autompleteItems={autocompleteItems}
        setAutocompleteItems={setAutocompleteItems}
        subgraphRootId={rootNodeId}/>

      <Paragraph size={400}>
        Your Proposed Operator for your selected subgraph: {labelBadge}
      </Paragraph>
      <Paragraph marginY="0.5em">
        <Small>Click on Nodes to Select a Subgraph and label the subgraph with an Operator</Small>
      </Paragraph>
    </Pane> :
    <> </>;

  const renderForeignObjectNode = ({
    nodeDatum,
    toggleNode,
    foreignObjectProps
  }) => (
        <g>
      {(nodeDatum.kind == 'ProcessObservation') &&
        <g>
          { partOfSubgraph(nodeDatum) &&
            <rect width="70" height="60" y="-30" x="-40" fill='cyan' strokeWidth={"2"}></rect>
          }
          <svg height="50" y="-25" x="-25" width="50">

              <polygon points="0,0 0,50 50,25"
              fill={isSelected(nodeDatum) ? 'yellow' : 'lightgrey'}
              stroke="black" strokeWidth={(shouldHighlight(nodeDatum)) ? "5" : "1"}
              onMouseOut={()=>setHighlightedNode("")}
              onMouseOver={()=>highLightNode(nodeDatum)} onClick={()=>selectNode(nodeDatum)}></polygon>
            </svg>

        <text fontFamily="Arial, Helvetica, sans-serif"
          fill="blue" onClick={()=>Router.push(`/filelog/${nodeDatum.uuid}`)} strokeWidth="1" y="-20" x="40">
            Action: {nodeDatum.name  == actionNameMap[nodeDatum.name] ? actionNameMap[nodeDatum.name] : nodeDatum.name}
          </text>
          <text fontFamily="Times New Roman, serif" fill="grey" strokeWidth="0.5" fontSize="smaller" x="40" dy="-20">
            <tspan x="40" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
            <tspan x="40" dy="1.2em">Started on: {nodeDatum.startedOn}</tspan>
          </text>
        </g>
      }

      {(nodeDatum.kind == 'SharingEvent') &&
        <g>
        { partOfSubgraph(nodeDatum) &&
          <rect fill="cyan" width="100" height="50" y="-25" x="-25" strokeWidth="2"></rect>
        }

        <svg height="50" width="100" x="-25" y="-25">
          <ellipse cx="50" cy="25" rx="45" ry="20" fill="purple" stroke="black" strokeWidth={(shouldHighlight(nodeDatum)) ? "5" : "1"}
          onMouseOut={()=>setHighlightedNode("")}
          onMouseOver={()=>highLightNode(nodeDatum)} onClick={()=>selectNode(nodeDatum)}>
          </ellipse >
        </svg>
        <text fontFamily="Arial, Helvetica, sans-serif"
          fill="blue" onClick={()=>Router.push(`/filelog/${nodeDatum.uuid}`)} strokeWidth="1" y="-20" x="77">
            Likely sharing event
          </text>
          <text fontFamily="Times New Roman, serif" fill="grey" strokeWidth="0.5" fontSize="smaller">
            <tspan x="77" dy="60+.6em">Source: {nodeDatum.source}</tspan>
            <tspan x="77" dy="1.2em">Received on/before: {new Date(nodeDatum.receivedOnOrBefore * 1000).toLocaleString()}</tspan>
        </text>
        </g>
      }

      {(nodeDatum.kind == 'FileObservation') &&
        <g >
        {(nodeDatum.rootNode) &&
        <g>
        { partOfSubgraph(nodeDatum) &&
          <rect fill="cyan" width="60" height="60" y="-30" x="-20" strokeWidth="2"></rect>
        }

        <rect fill={isSelected(nodeDatum) ? 'yellow' : 'orange'}
        width="40" height="40" y="-20" strokeWidth={(shouldHighlight(nodeDatum)) ? "5" : "1"}
        x="-10" onMouseOut={()=>setHighlightedNode("")}
        onMouseOver={()=>highLightNode(nodeDatum)} onClick={()=>selectNode(nodeDatum)}></rect>
        </g>
      }
        {(nodeDatum.curatedSets.length > 0) &&
          (nodeDatum.rootNode == "True") &&
        <g>
        { partOfSubgraph(nodeDatum) &&
          <rect fill="cyan" width="60" height="60" y="-30" x="-20" strokeWidth="2"></rect>
        }
        <rect fill={isSelected(nodeDatum) ? 'yellow' : 'pink'} width="40" height="40" y="-20" strokeWidth={(shouldHighlight(nodeDatum)) ? "5" : "1"}
        x="-10" onMouseOut={()=>setHighlightedNode("")}
        onMouseOver={()=>highLightNode(nodeDatum)} onClick={()=>selectNode(nodeDatum)}></rect>
        <text fontFamily="Arial, Helvetica, sans-serif"
          strokeWidth="1" y="-20" x="45" fill="blue" onClick={()=>Router.push(`/filelog/${nodeDatum.uuid}`)}>
            Curated data '{nodeDatum.curatedSets[0].title}'
          </text>
          </g>
        }
        {
          (selectedLabeledSubgraph) &&
          (nodeDatum.longName === selectedLabeledSubgraph.fullRootFileName) &&
          <g>
          <text fontFamily="Arial, Helvetica, sans-serif"
            strokeWidth="1" y="-60" x="-20" fill="black">
              Subgraph End File with Operator: {selectedLabeledSubgraph.label}
          </text>
          <text fontFamily="Arial, Helvetica, sans-serif"
            strokeWidth="1" y="-40" x="-20" fill="black" fontSize='smaller'>
              Labeled By: {selectedLabeledSubgraph.ownerEmail}
          </text>
          </g>
        }

        {(nodeDatum.curatedSets.length === 0) &&
          (!nodeDatum.rootNode) &&
        <g>
        { partOfSubgraph(nodeDatum) &&
        <rect fill="cyan" width="60" height="60" y="-30" x="-20" strokeWidth="2"></rect>
        }
        <rect fill={isSelected(nodeDatum) ? 'yellow' : 'blue'} width="40" height="40" y="-20" strokeWidth={(shouldHighlight(nodeDatum)) ? "5" : "1"}
        x="-10" onMouseOut={()=>setHighlightedNode("")}
        onMouseOver={()=>highLightNode(nodeDatum)} onClick={()=>selectNode(nodeDatum)}></rect>
        </g>
        }

        {(nodeDatum.curatedSets.length > 0) &&
          (nodeDatum.rootNode == "False") &&
        <g>
        { partOfSubgraph(nodeDatum) &&
          <rect fill="cyan" width="60" height="60" y="-30" x="-20" strokeWidth="2"></rect>
        }
        <rect fill={isSelected(nodeDatum) ? 'yellow' :
        'lightgreen'} width="40" height="40" y="-20" strokeWidth={(shouldHighlight(nodeDatum)) ? "5" : "1"}
        x="-10" onMouseOut={()=>setHighlightedNode("")}
        onMouseOver={()=>highLightNode(nodeDatum)} onClick={()=>selectNode(nodeDatum)}></rect>
        <text fontFamily="Arial, Helvetica, sans-serif"
          strokeWidth="1" y="-20" x="45" fill="blue" onClick={()=>Router.push(`/filelog/${nodeDatum.uuid}`)}>
            Curated data '{nodeDatum.curatedSets[0].title}'
          </text>
          </g>
        }

        <g onClick={()=>Router.push(`/filelog/${nodeDatum.uuid}`)}>
          <text fontFamily="Times New Roman, serif" fill="blue" strokeWidth="0.5" fontSize="smaller" x="40" dy="-20">
            <tspan x="45" dy="-0.5em">Filename: {nodeDatum.shortName} </tspan>
            <tspan x="45" dy="1.6em">Owner: {nodeDatum.owner}</tspan>
            {/* <tspan x="45" dy="1.2em">{nodeDatum.cloneCount} known {nodeDatum.cloneCount == 1 ? 'copy' : 'copies' }</tspan> */}
            {/* <tspan x="40" dy="1.2em">Depth: {nodeDatum.depth}</tspan>           */}
          </text>
          </g>
      </g>
      }
    </g>
  );


  return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >

            {dobj.latest == 1 &&
            <Heading size={800}>File {dobj.filename}
            </Heading>
            }

            {dobj.latest == 0 &&
            <Heading size={800}>File {dobj.filename} (Obsolete)
            </Heading>
            }

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
                Owner: {dobj.owner}
            </Paragraph>

            <Paragraph size={300} color="muted">
                Last modified on: {new Date(dobj.modified * 1000).toLocaleString()}
            </Paragraph>

            <Paragraph size={300} color="muted">
                Version identifier: {dobj.id}
            </Paragraph>
            <Paragraph size={300} color="muted">
                Content hashcode: {dobj.md5hash}
            </Paragraph>

            <Paragraph size={300} color="muted">
                This file contains {dobj.datasets.length > 0 &&
                  <a href={datasetLink}>Dataset '{dobj.datasets[0].title}'</a>
                }
                {dobj.datasets.length == 0 && <a href={bytesetLink}>Raw Content {dobj.md5hash}</a>
                }
            </Paragraph>

            </Pane>
          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Provenance</Heading>
            <Popover display="flex" alignItems="center" justifyContent="center" flexDirection="column"
            shouldCloseOnExternalClick='True' content={({close}) => (
            <Pane width="100%" elevation={4} height="40em" display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>

            {(selectedNode && selectedNode.kind != 'ProcessObservation') &&
            <Pane>

            <Pane flex={1} border>
            <Pane margin={majorScale(1)}>
            <Heading>File {selectedNode.shortName}</Heading>
            <Pane marginLeft={majorScale(1)} marginRight={majorScale(1)}>
            <Paragraph size={300} color="muted">
                Full path: {selectedNode.longName}
            </Paragraph>
            <Paragraph size={300} color="muted">
                Owner: {selectedNode.owner}
            </Paragraph>
            <Paragraph size={300} color="muted">
                Version identifier: {selectedNode.uuid}
            </Paragraph>
            <Paragraph size={300} color="muted">
                Content hashcode: {selectedNode.md5hash}
            </Paragraph>
            <Paragraph size={300}>
              <a href={"/filelog/" + selectedNode.uuid}>Click for more details</a>
            </Paragraph>
            </Pane>
            </Pane>
            </Pane>


            <Pane flex={1} border>
            <Pane margin={majorScale(1)}>

            {((! selectedNode.curatedSets) || selectedNode.curatedSets.length === 0) &&
            <Heading>
              This is a Raw (Uncurated) data file.
            </Heading>
            }

            {(selectedNode.curatedSets && selectedNode.curatedSets.length > 0) &&
            <Pane>
            <Heading>
              This is a copy of a Curated Dataset.
            </Heading>
            <Pane marginLeft={majorScale(1)} marginRight={majorScale(1)}>
              {selectedNode.curatedSets.map(x => (
                <Pane>
                <Paragraph size={300} color="muted">
                  Curated set: {x.title}
                </Paragraph>
                <Paragraph size={300} color="muted">
                  (<a href={"/dataset/" + x.uuid}>Click for more details</a>)
                </Paragraph>
                </Pane>
              ))}
            </Pane>
            </Pane>
            }
            </Pane>
            </Pane>


            <Pane width={800} border>
            <Pane width={800} margin={majorScale(1)}>
            <Heading>Usage</Heading>
            <Pane width={800} marginLeft={majorScale(1)}>
              <Paragraph size={300} color="muted"> Known uses anywhere on Earth:
               {selectedNode.fileInputCount} (<a href="/uses">Click for more details</a>)</Paragraph>
              <Paragraph size={300} color="muted"> Known copies
              anywhere on Earth: {selectedNode.cloneCount} (<a href="/uses">Click for more details</a>)</Paragraph>
            </Pane>
            </Pane>
            </Pane>

            <Pane width={800} border>

            <Pane margin={majorScale(1)}>
            <Heading>
              Content {selectedNode.filetype }
            </Heading>

            <Pane marginLeft={majorScale(1)} overflowY="scroll" height={340}>
            { ! selectedNode.content.hasContent &&
              <Paragraph size={300} color="muted">
                You do not have access to this content.
              </Paragraph>

            }
            { selectedNode.content.hasContent &&
              <Pane>
              <Paragraph size={300} color="muted">
                A copy of this content has been cached.
              </Paragraph>

              { selectedNode.filetype == "text/plain" &&
              <Pane display="flex" border>
              <Pre>
                {Buffer.from(selectedNode.content.content).toString()}
              </Pre>
              </Pane>
              }

              { selectedNode.filetype == "image/png" &&
              <Pane display="flex" border>
                <img height="300" src={"data:image/png;base64," + selectedNode.content.content}/>
              </Pane>

              }

              { selectedNode.filetype == "application/pdf" &&
                 <Pane>
                 <embed src={"https://drive.google.com/viewerng/viewer?embedded=true&url="+selectedNode.longName} width="600" height="0" id="pdfDiv" onLoad={function () {document.getElementById('pdfSpinner').style.display='none'; document.getElementById('pdfDiv').style.height='300px'}}/>
                 <br />
                 <div id="pdfSpinner" display="block" clear="both">
                 <Spinner/>
                 </div>
                 </Pane>
              }

              { selectedNode.filetype == "text/csv" &&
             <Pane display="flex" border>
               <Table border background="tint1">
                   <Table.Body>
                       {readString(Buffer.from(selectedNode.content.content).toString().trim(), {preview: 10}).data.map((row, idx) => (
                           <Table.Row key={row + idx}>
                               {row.map((cell, cellidx) => (
                                   <Table.TextCell key={cell + cellidx}>{cell}</Table.TextCell>
                               ))}
                           </Table.Row>
                       ))}
                   </Table.Body>
               </Table>
             </Pane>
             }

              </Pane>

             }


            </Pane>

            </Pane>
            </Pane>

            </Pane>
            }

            {((!selectedNode) || (selectedNode.kind == 'ProcessObservation')) &&
            <Heading>
              No node is selected
            </Heading>
            }

            </Pane>
            </Pane>
            )}
            shouldCloseOnExternalClick={true}>
            <Button disabled={subgraphSelection}>Current Selected Node details</Button>
            </Popover>

          <Pane>
          {(hasForwardData) &&
            <div v-if={hasForwardData} align="right">
              <div>
              <Button onClick={()=>Router.push(`${nextLink}`)}>Forward -> ({nextAction})</Button>
              </div>
            </div>
          }
          </Pane>

           <div style={{ width: '100%', height:'40em' }} ref={containerRef}>

         <Tree
          data={dobj.descendentData}
          separation={{nonSiblings: 0.5, siblings: 0.5}}
          orientation="horizontal"
          translate={dobj.reverseDirection ? translateRev : translate}
          depthFactor={dobj.reverseDirection ? 400 : -400}
          zoom="1"
          scaleExtent={{max:5,min:0.1}}
          renderCustomNodeElement={(rd3tProps) =>renderForeignObjectNode({ ...rd3tProps })}
        />
        </div>

          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Pane marginLeft={majorScale(1)}>
                {dobj.prevId.length > 0 &&
                <Paragraph size={300} >
                   <a href={previousLink}>See the previous version</a>
                </Paragraph>
                 }
                {dobj.prevId.length == 0 &&
                <Paragraph size={300} >
                 This is the first observed version of the file.
                </Paragraph>
                 }
            </Pane>
          </Pane>
        </Pane>

        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Pane marginLeft={majorScale(1)}>
                {dobj.nextId.length > 0 &&
                <Paragraph size={300} >
                   <a href={nextLink}>See the next version</a>
                </Paragraph>
                 }
                {dobj.nextId.length == 0 &&
                <Paragraph size={300} >
                 This is the latest observed version of the file.
                </Paragraph>
                 }
            </Pane>
          </Pane>
        </Pane>


      </Pane>
     )
  }

  export default FileLog
