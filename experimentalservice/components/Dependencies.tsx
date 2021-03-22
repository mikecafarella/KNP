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

    console.log(dobj.dobj)

    const predecessors = dobj.dobj.predecessors
    // const successors = dobj.dobj.successors

    // .map( async (x) => {
    //     const objnameid = x.NameAssignment[0].objnameid
    //     const data = fetch("http://localhost:3000/api/dobj/X" + objnameid)
    //       .then((response) => response.json())
    //       .then((obj) => {
    //         return obj;
    //       });
    //
    //       const d = await data
    //       return d
    // })

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
    let links = []
    const labelFn = function(node) {
        return labelMap[node.id]
    }
    idToNodeMap[dobj.dobj.id] = dobj
    let nodes = [{ id: dobj.dobj.id,
                   color: "red",
                   x: 400,
                   y: 200,
                    labelPosition: "bottom",
                }]
    labelMap[dobj.dobj.id] = dobj.label.iscurrent ? dobj.label.name : dobj.dobj.id



    for (var p of predecessors) {
        let objname = p.NameAssignment[0].objname
        nodes.push({id: p.id,
                        color: "green",
                    })
        labelMap[p.id] = objname.name
        links.push({source: p.id , target:dobj.dobj.id})
        idToNodeMap[p.id] = p
        for (var q of p.predecessors) {
          let objname = q.NameAssignment[0].objname
          nodes.push({id: q.id,
                          color: "green",
                      })
          labelMap[q.id] = objname.name
          links.push({source: q.id , target:p.id})
          idToNodeMap[q.id] = q
        }
    }

    // for (var q of successors) {
    //   let objname = q.NameAssignment[0].objname
    //   nodes.push({id: q.id,
    //                   color: "blue",
    //               })
    //   labelMap[q.id] = objname.name
    //   links.push({source: q.id , target:p.id})
    //   idToNodeMap[q.id] = q
    // }


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
