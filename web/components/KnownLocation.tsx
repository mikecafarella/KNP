
import React, { useState, useCallback} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import { majorScale, Popover, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'
import Tree from 'react-d3-tree'


export type FileProps = {
  fileid: string;
  filename: string;
  modified: string;
  owner: string;
  isLatest: number;
}

export type KnownLocationProps = {
  id: string;
  owner: string;
  filename: string;
  modified: string;
  synctime: string;
  prevId: string;
  nextId: string;
  isLatest: number;
  md5hash: string;
  nearDuplicates: FileProps[];
}

const KnownLocation: React.FC<{dobj: KnownLocationProps}> = ({dobj}) => {
  const bytesetLink = "/byteset/" + dobj.md5hash
  const datasetLink = "/dataset/" + (dobj.datasets.length > 0 ? dobj.datasets[0].uuid : "")
  const previousLink = "/knownlocation/" + dobj.prevId
  const nextLink = "/knownlocation/" + dobj.nextId

  const [highlightedNode, setHighlightedNode] = useState("")
  const [selectedNode, setSelectedNode] = useState("")  


const useCenteredTree = (defaultTranslate = { x: 0, y: 0 }) => {
  const [translate, setTranslate] = useState(defaultTranslate);
  const containerRef = useCallback((containerElem) => {
    if (containerElem !== null) {
      const { width, height } = containerElem.getBoundingClientRect();
      setTranslate({ x: width * 0.8, y: height * 0.43 });
    }
  }, []);
  return [translate, containerRef];
};

const [translate, containerRef] = useCenteredTree();


const renderForeignObjectNode = ({
  nodeDatum,
  toggleNode,
  foreignObjectProps
}) => (
      <g>
    {(nodeDatum.kind == 'ProcessObservation') &&
       <g>
       <svg height="50" y="-25" x="-10" width="50">
         <polygon points="0,0 0,50 50,25"
         fill={selectedNode===nodeDatum.uuid ? 'yellow' : 'lightgrey'}
         stroke="black" stroke-width={(highlightedNode
       ===nodeDatum.uuid) ? "4" : "1"}
         onMouseOut={()=>setHighlightedNode("")}
         onMouseOver={()=>setHighlightedNode(nodeDatum.uuid)} onClick={()=>setSelectedNode(nodeDatum)}></polygon>
       </svg>

       <text font-family="Arial, Helvetica, sans-serif" 
        fill="blue" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)} strokeWidth="1" y="-20" x="40">
          Program '{nodeDatum.name}'
        </text>
        <text font-family="Times New Roman, serif" fill="grey" strokeWidth="0.5" font-size="smaller" x="40" dy="-20">        
          <tspan x="40" dy="-1 + .6em">Name: {nodeDatum.name}</tspan>
          <tspan x="40" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
          <tspan x="40" dy="1.2em">Started on: {nodeDatum.startedOn}</tspan>          
        </text>

       </g> 
    }
    
    {(nodeDatum.kind == 'SharingEvent') &&
      <g>
      <svg height="50" width="100" x="-25" y="-25">
         <ellipse cx="50" cy="25" rx="45" ry="20" fill="yellow" stroke="black" stroke-width="1">
         </ellipse>
      </svg>
       <text font-family="Arial, Helvetica, sans-serif" 
        fill="blue" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)} strokeWidth="1" y="-20" x="40">
          Likely sharing event
        </text>
        <text font-family="Times New Roman, serif" fill="grey" strokeWidth="0.5" font-size="smaller" x="-20" dy="60">        
          <tspan x="-20" dy="60+.6em">Received on/before: 13-Dec-2021 10:55:23</tspan>
          <tspan x="-20" dy="1.2em">Receiver: michjc@csail.mit.edu</tspan>
          <tspan x="-20" dy="1.2em">Observed potential sources: 1</tspan>          
          <tspan x="-20" dy="1.2em">Likeliest source: mrander@gmail.com</tspan>          
       </text>
      </g>
    }
    
    {(nodeDatum.kind == 'FileObservation') &&
      <g >
       {(nodeDatum.curatedSets.length === 0) &&
        (nodeDatum.rootNode == "True") &&
       <g>
       <rect fill={selectedNode.uuid===nodeDatum.uuid ? 'yellow' : 'red'}
       width="40" height="40" y="-20" stroke-width={(highlightedNode
       ===nodeDatum.uuid) ? "4" : "1"}
       x="-10" onMouseOut={()=>setHighlightedNode("")}
       onMouseOver={()=>setHighlightedNode(nodeDatum.uuid)} onClick={()=>setSelectedNode(nodeDatum)}></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="-20" x="40" fill="blue" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Raw data file
        </text>
       </g>        
       }
       {(nodeDatum.curatedSets.length > 0) &&
        (nodeDatum.rootNode == "True") &&
       <g>
       <rect fill={selectedNode.uuid===nodeDatum.uuid ? 'yellow' : 'pink'} width="40" height="40" y="-20" stroke-width={(highlightedNode
       ===nodeDatum.uuid) ? "4" : "1"}
       x="-10" onMouseOut={()=>setHighlightedNode("")}
       onMouseOver={()=>setHighlightedNode(nodeDatum.uuid)} onClick={()=>setSelectedNode(nodeDatum)}></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="-20" x="40" fill="blue" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Curated data '{nodeDatum.curatedSets[0].title}'
        </text>
        </g>
       }

       {(nodeDatum.curatedSets.length === 0) &&
        (nodeDatum.rootNode == "False") &&
       <g>
       <rect fill={selectedNode.uuid===nodeDatum.uuid ? 'yellow' : 'green'} width="40" height="40" y="-20" stroke-width={(highlightedNode
       ===nodeDatum.uuid) ? "4" : "1"}
       x="-10" onMouseOut={()=>setHighlightedNode("")}
       onMouseOver={()=>setHighlightedNode(nodeDatum.uuid)} onClick={()=>setSelectedNode(nodeDatum)}></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="-20" x="40" fill="blue" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Raw data file
        </text>
       </g>        
       }
       {(nodeDatum.curatedSets.length > 0) &&
        (nodeDatum.rootNode == "False") &&
       <g>
       <rect fill={selectedNode.uuid===nodeDatum.uuid ? 'yellow' :
       'lightgreen'} width="40" height="40" y="-20" stroke-width={(highlightedNode===nodeDatum.uuid) ? "4" : "1"}
       x="-10" onMouseOut={()=>setHighlightedNode("")}
       onMouseOver={()=>setHighlightedNode(nodeDatum.uuid)} onClick={()=>setSelectedNode(nodeDatum)}></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="-20" x="40" fill="blue" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Curated data '{nodeDatum.curatedSets[0].title}'
        </text>
        </g>
       }

       <g onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
        <text font-family="Times New Roman, serif" fill="blue" strokeWidth="0.5" font-size="smaller" x="40" dy="-20">
          <tspan x="40" dy="-1 + 0.6em">Filename: {nodeDatum.shortName} </tspan>
          <tspan x="40" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
          <tspan x="40" dy="1.2em">{nodeDatum.fileInputCount} known
          use(s), {nodeDatum.cloneCount} known copies</tspan>
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
            content={({close}) => (
            <Pane width="100%" elevation="4" height="40em" display="flex" padding={majorScale(1)} border>
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
              <a href={"/knownlocation/" + selectedNode.uuid}>Click for more details</a>
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
              This is a Curated data file.
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

            <Pane flex={1} border>
            <Pane margin={majorScale(1)}>
            <Heading>
              Content
            </Heading>                
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
            shouldCloseOnExternalClick={false}>
            <Button>Selection details</Button>
            </Popover>
           <div style={{ width: '100%', height:'40em' }} ref={containerRef}>
            
         <Tree
          data={dobj.descendentData}
          separation={{nonSiblings: 0.6, siblings: 0.6}} 
          orientation="horizontal"
          translate={translate}
          depthFactor={-400}
          zoom="0.8"
          zoomable="True"
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

  export default KnownLocation

