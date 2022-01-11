import React, { useState} from 'react'
import { Graph } from "react-d3-graph";

import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import DataobjectSummary from "./DataobjectSummary"
import DataContentProps from "./DataContent"
import DataobjProps from "./Dataobject"
import { Badge, majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table, Tooltip, IconButton } from 'evergreen-ui'
import { callbackify } from 'util';
// import { flex } from 'ui-box';
import { isValidSubgraph } from './Utils'
import SubgraphLabel from './SubgraphLabel';


const Dependencies: React.FC<{dobj: DataobjProps}> = ({dobj}) => {

    const [mouseIndex, setMouseIndex] = useState(-1)
    const [selectedNodes, setSelectedNodes] = useState([])
    const [label, setLabel] = useState('');
    const predecessors = dobj.displayVersion.predecessors
    // const successors = dobj.successors

    const toggleNode = function(nodeId) {
        // deselect
        if (selectedNodes.includes(nodeId)) {
            setSelectedNodes(
                selectedNodes.filter(id => id !== nodeId)
            );
            setLabel('');
        } else {
            setSelectedNodes(
                [...selectedNodes, nodeId]
            );
        }  
    }

    // const deselect
    const resetSelections = function() {
        setSelectedNodes([]);
        setLabel('')
    }

    const onClickNodeFn = function(nodeId) {
        setMouseIndex(nodeId)
        toggleNode(nodeId)
    }
    const onMouseOverNodeFn = function(nodeId) {
        console.log(nodeId)
        setMouseIndex(nodeId)
    };
    const onMouseOutNodeFn = function(nodeId) {
        setMouseIndex(-1)
    };

    const onMouseOverLinkFn = function(linkId) {
        console.log('------',linkId)
        setMouseIndex(linkId)
    };
    const onMouseOutLinkFn = function(linkId) {
        setMouseIndex(-1)
    };

    const labelMap = {}
    const idToNodeMap = {}
    let links = []
    const labelFn = function(node) {
        return labelMap[node.id]
    }
    idToNodeMap[dobj.displayVersion.dataobject.id] = dobj.displayVersion
    const color = (selectedNodes.includes(dobj.displayVersion.dataobject.id.toString())) ? "purple" : "red"
    let rootId = dobj.displayVersion.dataobject.id;
    let nodes = [{ id: dobj.displayVersion.dataobject.id,
                   color: color,
                   x: 300,
                   y: 500,
                    labelPosition: "bottom",
                }]
    labelMap[dobj.displayVersion.dataobject.id] = dobj.name
    // console.log(dobj.displayVersion.dataobject.id)

    let px = (600 - ((predecessors.length-1) * 150))/2
    let py = 350
    let maxy = 500
    let miny = 500
    for (var p of predecessors) {
        if (py > maxy) maxy = py
        if (py < miny) miny = py
        const color = (selectedNodes.includes(p.dataobject.id.toString())) ? "purple" : "green"
        nodes.push({id: p.dataobject.id,
                        color: color,
                        x: px,
                        y: py
                    });

        labelMap[p.dataobject.id] = p.dataobject.name
        const generator = dobj.displayVersion.generators.length ? dobj.displayVersion.generators[0] : null
        const linkLabel = generator ? generator.dataobject.name : null
        const linkColor = linkLabel ? 'blue' : 'lightgray'
        links.push({source: p.dataobject.id ,
                    target: dobj.displayVersion.dataobject.id,
                    label: linkLabel,
                    color: linkColor,
                    id: generator ? generator.dataobject.id : null
                  })
        idToNodeMap[p.dataobject.id] = p
        // idToNodeMap[generator.dataobject.id] = generator
        // console.log(links)
        let qx = (px - 75 * (p.predecessors.length - 1))
        let qy = 200
        for (var q of p.predecessors) {
          if (qy > maxy) maxy = qy
          if (qy < miny) miny = qy
          const generator = p.generators.length ? p.generators[0] : null
          const linkLabel = generator ? generator.dataobject.name : null
          const linkColor = linkLabel ? 'blue' : 'lightgray'
          const color = (selectedNodes.includes(q.dataobject.id.toString())) ? "purple" : "green"
          nodes.push({id: q.dataobject.id,
                          color: color,
                          x: qx,
                          y: qy
                      });

          labelMap[q.dataobject.id] = q.dataobject.name
          links.push({source: q.dataobject.id ,
                      target: p.dataobject.id,
                      label: linkLabel,
                      color: linkColor,
                      id: generator ? generator.dataobject.id : null})
          idToNodeMap[q.dataobject.id] = q
          let rx = (qx - 75 * (q.predecessors.length - 1))
          let ry = 50
          for (var r of q.predecessors) {
            if (ry > maxy) maxy = ry
            if (ry < miny) miny = ry
            const generator = q.generators.length ? q.generators[0] : null
            const linkLabel = generator ? generator.dataobject.name : null
            const linkColor = linkLabel ? 'blue' : 'lightgray'
            const color = (selectedNodes.includes(r.dataobject.id.toString())) ? "purple" : "green"
            nodes.push({id: r.dataobject.id,
                            color: color,
                            x: rx,
                            y: ry
                        });
            labelMap[r.dataobject.id] = r.dataobject.name
            links.push({source: r.dataobject.id ,
                        target: q.dataobject.id,
                        label: linkLabel,
                        color: linkColor,
                        id: generator ? generator.dataobject.id : null})
            idToNodeMap[r.dataobject.id] = r

            rx += 150
            ry += 30
          }
          qx += 150
          qy += 30
        }
        px += 150
        py += 30
    }

    let adjust = (600 - (maxy-miny))/2 - 80

    for (const n in nodes) {
      nodes[n].y -= adjust
    }

    // console.log('idToNodeMap', idToNodeMap)

    // for (var q of successors) {
    //   let objname = q.NameAssignment[0].objname
    //   nodes.push({id: q.id,
    //                   color: "blue",
    //               })
    //   labelMap[q.id] = objname.name
    //   links.push({source: q.id , target:p.id})
    //   idToNodeMap[q.id] = q
    // }

    // console.log(links);

    const graph = {}
    

    for (let edge of links) {
        let src = edge.source.toString();
        let dest = edge.target.toString();
        if (!graph.hasOwnProperty(dest)) {
            graph[dest] = [src];
        } else {
            graph[dest] = [...graph[dest], src];
        }
    }
    
    const data = {
        nodes: nodes,
        links: links,
    };

    const myConfig = {
        directed: true,
        nodeHighlightBehavior: false,
        highlightDegree: 0,
        maxZoom: 2,
        minZoom: 1,
        width: 600,
        height: 600,
        "d3": {
          "alphaTarget": 0.05,
          "gravity": -400,
          "linkLength": 120,
          "linkStrength": 0,
          "disableLinkForce": true
        },
        node: {
            color: "lightgreen",
            size: 500,
            highlightStrokeColor: "blue",
            labelProperty: labelFn,
            fontSize: 12
        },
        link: {
            renderLabel: true,
            fontSize: 12,

        },
    };
    // a little confusing, should change this so more readable, but valid subgraph returns true if the button should be
    // disabled, ie not a valid subgraph
    let inValidSubgraph = isValidSubgraph(graph, nodes, rootId, selectedNodes);
    let subgraphLabelChooser = inValidSubgraph ? 
        <></> : 
        <SubgraphLabel 
            subgraphNodeIds={selectedNodes} 
            label={label} 
            setLabel={setLabel}
        />;
    let labelBadge = (label) ? <Badge color='blue'>{label}</Badge> : '';
    
    let subgraphLabel = (!inValidSubgraph) 
        ? 
        <Pane>
            <Paragraph>
                Subgraph Label for your selected subgraph: {labelBadge}
            </Paragraph>
        </Pane>: 
        <></>


    return (
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
      >
        <Pane background="tint1" display='flex' flexDirection='column'>
            <Button 
                disabled={selectedNodes.length === 0}
                onClick={resetSelections}
            >Reset Subgraph Selection
            </Button>
            {subgraphLabelChooser}
            
        </Pane>
        
        <Pane flex={1} background="tint1" padding={majorScale(1)} display='flex' flexDirection='column'>
            {subgraphLabel}
            <Graph
                id="graph-id" // id is mandatory, if no id is defined rd3g will throw an error
                data={data}
                onClickNode={onClickNodeFn}
                // onMouseOutNode={onMouseOutNodeFn}
                onMouseOverNode={onMouseOverNodeFn}
                // onMouseOverLink={onMouseOverLinkFn}
                // onMouseOutLink={onMouseOverLinkFn}
                config={myConfig}/>
        </Pane>

        <Pane padding={majorScale(1)} flex={2}>
          <DataobjectSummary dobj={mouseIndex >= 0 ? idToNodeMap[mouseIndex] : null}/>
        </Pane>
      </Card>
    )
}

export default Dependencies
