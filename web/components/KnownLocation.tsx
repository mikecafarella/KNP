import React, { useState, useCallback} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'
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
         <polygon points="0,0 0,50 50,25" fill="lightgrey" stroke="black" stroke-width="1"></polygon>
       </svg>

       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="40" x="-20" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Program 
        </text>
        <text font-family="Times New Roman, serif" fill="grey" strokeWidth="0.5" font-size="smaller" x="-20" dy="60">        
          <tspan x="-20" dy="60+.6em">Name: {nodeDatum.name}</tspan>
          <tspan x="-20" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
          <tspan x="-20" dy="1.2em">Started on: {nodeDatum.startedOn}</tspan>          
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
        strokeWidth="1" y="40" x="-20" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
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
      <g>
       <rect fill="green" width="40" height="40" y="-20" stroke-width="1"
       x="-10"></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="40" x="-20" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Data file
        </text>
        <text font-family="Times New Roman, serif" fill="grey" strokeWidth="0.5" font-size="smaller" x="-20" dy="60">        
          <tspan x="-20" dy="60+.6em">Filename: {nodeDatum.shortName} </tspan>
          <tspan x="-20" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
        </text>
     </g>
    }
    {(nodeDatum.kind == 'FileObservationWithCuratedContent') &&
      <g>    
       <rect fill="lightgreen" width="40" height="40" y="-20" stroke-width="1"
       x="-10"></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="40" x="-20" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Curated data file
        </text>
        <text font-family="Times New Roman, serif" fill="grey" strokeWidth="0.5" font-size="smaller" x="-20" dy="60">        
          <tspan x="-20" dy="60+.6em">Filename: {nodeDatum.shortName}</tspan>
          <tspan x="-20" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
          <tspan fill="blue" x="-20" dy="1.2em"><a href={nodeDatum.curatedId}>Curated dataset: {nodeDatum.curatedName}</a></tspan>          
       </text>
       
     </g>       
    }
    {(nodeDatum.kind == 'CurFileObservation') &&
      <g>
       <rect fill="red" width="40" height="40" y="-20" stroke="black" stroke-width="7"
       x="-10"></rect>
       <text font-family="Arial, Helvetica, sans-serif" 
        strokeWidth="1" y="40" x="-20" onClick={()=>Router.push(`/knownlocation/${nodeDatum.uuid}`)}>
          Data file
        </text>
        <text font-family="Times New Roman, serif" fill="grey" strokeWidth="0.5" font-size="smaller" x="-20" dy="60">        
          <tspan x="-20" dy="60+.6em">Filename: {nodeDatum.shortName} </tspan>
          <tspan x="-20" dy="1.2em">Owner: {nodeDatum.owner}</tspan>
        </text>
     </g>              
    }
   </g>    
);

const renderRectSvgNode = ({ nodeDatum, toggleNode }) => (
  <g>
    <circle r={25} fill="lightblue" width="20" height="20" onClick={toggleNode} />
    <text font-family="Arial, Helvetica, sans-serif" fill="black" strokeWidth="1" x="20">
      {nodeDatum.name}
    </text>
    {nodeDatum.attributes?.department && (
      <text font-family="Arial, Helvetica, sans-serif" fill="red" x="20" dy="20" strokeWidth="1">
        Department: {nodeDatum.attributes?.department}
      </text>
    )}
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
                This file contains {dobj.datasets.length > 0 &&
                  <a href={datasetLink}>Dataset {dobj.datasets[0].uuid}</a>
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
           <div style={{ width: '100%', height:'40em' }} ref={containerRef}>
            
         <Tree
          data={dobj.descendentData}
          separation={{nonSiblings: 1, siblings: 1.3}} 
          orientation="horizontal"
          translate={translate}
          depthFactor={-250}
          zoom="1"
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

