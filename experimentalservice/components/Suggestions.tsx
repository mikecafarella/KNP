import React, { useState} from 'react'
import { Graph } from "react-d3-graph";
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import DataobjectSummary from "./DataobjectSummary"
import DataContentProps from "./DataContent.tsx"
import DataobjProps from "./Dataobject.tsx"
import { readString } from 'react-papaparse';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import Post, {PostProps} from "./Post"
import { majorScale, Text, Code, Pre, Pane, Heading, Button, Popover, TextInput, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'
import { callbackify } from 'util';


async function testFunction() {

  // const testId = document.getElementById('testId').value
  const testID = "X30" // hardcoded

  // const testParams = document.getElementById('testParams').value
  const testParams = "fips_code, case_duration" // hardcoded

  const saveButtonDisplay = document.getElementById('saveButtonDisplay')

  // const dataobjId = document.getElementById('dataobjId').value
  const dataobjId = "X40" // hardcoded

  
  const outputDiv = document.getElementById('testResults')

  outputDiv.innerHTML = "<div><br /><b>Test Results</b></div>"
  outputDiv.innerHTML += "<div>Running....</div>"

  const res = await fetch('http://localhost:5000/function/'+dataobjId+'/'+testId+'?params='+encodeURIComponent(testParams))
  const data = await res.json()

  let output = ""
  if (typeof(data) === 'object') {

    if (data.datatype && data.datatype === '/datatypes/img') {
      let imgstr = "data:" + data.mimetype + ";base64, " + data.contents
      output = '<img src="' + imgstr + '"/>'
    }
    else if (data.datatype && data.datatype === '/datatypes/csv') {
      // let csvData = Buffer.from(data.contents, 'base64').toString()
      // let csvTable = readString(csvData, {preview: 50}).data;

      output = Buffer.from(data.contents, 'base64').toString()
    }
    else {
      output = [JSON.stringify(data, null, 2)]
    }
  }
  else {
    output = htmlEntities(data)
  }

  saveButtonDisplay.style.display="block"

  outputDiv.innerHTML = "<div><br /><b>Test Results</b></div>"
  outputDiv.innerHTML += "<div>"+output+"</div>"
}

const Suggestions: React.FC<{dobj: DataobjProps}> = ({dobj}) => {

    const [mouseIndex, setMouseIndex] = useState(-1)

    const predecessors = dobj.displayVersion.predecessors
    // const successors = dobj.successors

    const onClickNodeFn = function(nodeId) {
        setMouseIndex(nodeId)
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
    let nodes = [{ id: dobj.displayVersion.dataobject.id,
                   color: "red",
                   x: 300,
                   y: 500,
                    labelPosition: "bottom",
                }]
    labelMap[dobj.displayVersion.dataobject.id] = dobj.name
    console.log(dobj.displayVersion.dataobject.id)

    let px = (600 - ((predecessors.length-1) * 150))/2
    let py = 350
    let maxy = 500
    let miny = 500
    for (var p of predecessors) {
        if (py > maxy) maxy = py
        if (py < miny) miny = py
        nodes.push({id: p.dataobject.id,
                        color: "green",
                        x: px,
                        y: py
                    })

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
        console.log(links)
        let qx = (px - 75 * (p.predecessors.length - 1))
        let qy = 200
        for (var q of p.predecessors) {
          if (qy > maxy) maxy = qy
          if (qy < miny) miny = qy
          const generator = p.generators.length ? p.generators[0] : null
          const linkLabel = generator ? generator.dataobject.name : null
          const linkColor = linkLabel ? 'blue' : 'lightgray'
          nodes.push({id: q.dataobject.id,
                          color: "green",
                          x: qx,
                          y: qy
                      })

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
            nodes.push({id: r.dataobject.id,
                            color: "green",
                            x: rx,
                            y: ry
                        })
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

    console.log('idToNodeMap', idToNodeMap)

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


    return (
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex">

        <Button appearance="primary" id="testFunctionButton" onClick={testFunction}>Function 1</Button>

      </Card>

      <div>
        <Pre id="testResults"></Pre>
      </div>

    )
}

export default Suggestions
