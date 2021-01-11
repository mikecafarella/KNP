import React, { useState} from 'react'
import { Graph } from "react-d3-graph";

import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import DataobjectSummary from "./DataobjectSummary"
import DataContentProps from "./DataContent.tsx"
import DataobjProps from "./Dataobject.tsx"
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'
import { callbackify } from 'util';


const Dependencies: React.FC<{dobj: DataobjProps}> = ({dobj}) => {
    const [mouseIndex, setMouseIndex] = useState(-1)

    const predecessors = dobj.dobj.predecessors.map( async (x) => {
        const res = await fetch("http://localhost:3000/api/dobj/{x.id}")
        return await res.json()
    })

    const onClickNodeFn = function(nodeId) {
        setMouseIndex(nodeId)
    }
    const onMouseOverNodeFn = function(nodeId) {
        setMouseIndex(nodeId)
    };
    const onMouseOutNodeFn = function(nodeId) {
        setMouseIndex(-1)
    };
        
    const labelMap = {}
    const idToNodeMap = {}
    const links = []
    const labelFn = function(node) {
        return labelMap[node.id]
    }
    idToNodeMap[dobj.dobj.id] = dobj
    const nodes = [{ id: dobj.dobj.id, 
                   color: "red", 
                   x: 400,
                   y: 200,
                    labelPosition: "bottom",
                }]
    labelMap[dobj.dobj.id] = dobj.label.iscurrent ? dobj.label.name : dobj.dobj.id

    for (var p of predecessors) {
        nodes.append({id: p.dobj.id,
                        color: "green",
                    })
        labelMap[p.dobj.id] = p.label.iscurrent ? p.label.name : p.dobj.id;
        links.append({source: dobj.dobj.id, target: p.dobj.id})
        idToNodeMap[p.dobj.id] = p
    }


    const data = {
        nodes: nodes,
        links: links,
    };

    const myConfig = {
        directed: true,
        nodeHighlightBehavior: true,
        highlightDegree: 0,
        maxZoom: 1,
        minZoom: 1,
        node: {
            color: "lightgreen",
            size: 500,
            highlightStrokeColor: "blue",
            labelProperty: labelFn,
        },
        link: {
            highlightColor: "lightblue",
        },
    };
    

    return (
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
      >
        <Pane flex={1} background="tint1" padding={majorScale(1)}>
            <Graph
                id="graph-id" // id is mandatory, if no id is defined rd3g will throw an error
                data={data}
                onClickNode={onClickNodeFn}
                onMouseOutNode={onMouseOutNodeFn}
                onMouseOverNode={onMouseOverNodeFn}
                config={myConfig}/>
        </Pane>
        <Pane padding={majorScale(1)} flex={2}>
            <DataobjectSummary dobj={mouseIndex >= 0 ? idToNodeMap[mouseIndex] : null}/>
        </Pane>
      </Card>
    )
}  

export default Dependencies
