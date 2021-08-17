import React, { useState} from 'react'
import { Graph } from "react-d3-graph";
import Router from 'next/router'
import DataContent from './DataContent'
import ReactMarkdown from 'react-markdown'
import DataobjectSummary from "./DataobjectSummary"
import DataContentProps from "./DataContent.tsx"
import DataobjProps from "./Dataobject.tsx"
import { readString } from 'react-papaparse';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import Post, {PostProps} from "./Post"
import { majorScale, Text, Code, Pre, Pane, Heading, Button, Popover, TextInput, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'
import { callbackify } from 'util';


async function function30() {

  // const testId = document.getElementById('testId').value
  const testId = "30" // hardcoded

  // const testParams = document.getElementById('testParams').value
  const testParams = "fips_code,case_duration" // hardcoded

  // const dataobjId = document.getElementById('dataobjId').value
  const dataobjId = "40" // hardcoded

  const saveButtonDisplay = document.getElementById('saveButtonDisplay')
  const outputDiv = document.getElementById('testResults')

  outputDiv.innerHTML = "<div><br /><b>Output</b></div>"
  outputDiv.innerHTML += "<div>Running....</div>"

  const res = await fetch('http://localhost:5000/function/'+testId+'/'+dataobjId+'?params='+encodeURIComponent(testParams))
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
  outputDiv.innerHTML = "<div><br /><b>Output</b></div>"
  outputDiv.innerHTML += "<div>"+output+"</div>"
}

async function function32() {

  // const testId = document.getElementById('testId').value
  const testId = "32" // hardcoded

  // const testParams = document.getElementById('testParams').value
  const testParams = "County,Niagara County" // hardcoded

  // const dataobjId = document.getElementById('dataobjId').value
  const dataobjId = "40" // hardcoded

  const saveButtonDisplay = document.getElementById('saveButtonDisplay')
  const outputDiv = document.getElementById('testResults2')

  outputDiv.innerHTML = "<div><br /><b>Output</b></div>"
  outputDiv.innerHTML += "<div>Running....</div>"

  const res = await fetch('http://localhost:5000/function/'+testId+'/'+dataobjId+'?params='+encodeURIComponent(testParams))
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
  outputDiv.innerHTML = "<div><br /><b>Output</b></div>"
  outputDiv.innerHTML += "<div>"+output+"</div>"
}

async function function33() {

  // const testId = document.getElementById('testId').value
  const testId = "33" // hardcoded

  // const testParams = document.getElementById('testParams').value
  const testParams = "State,case_duration" // hardcoded

  // const dataobjId = document.getElementById('dataobjId').value
  const dataobjId = "40" // hardcoded

  const saveButtonDisplay = document.getElementById('saveButtonDisplay')
  const outputDiv = document.getElementById('testResults3')

  outputDiv.innerHTML = "<div><br /><b>Output</b></div>"
  outputDiv.innerHTML += "<div>Running....</div>"

  const res = await fetch('http://localhost:5000/function/'+testId+'/'+dataobjId+'?params='+encodeURIComponent(testParams))
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
  outputDiv.innerHTML = "<div><br /><b>Output</b></div>"
  outputDiv.innerHTML += "<div>"+output+"</div>"
}


const saveObject = async (e: React.SyntheticEvent) => {
  e.preventDefault()
  try {
    const ownerid = 1
    const dataobject_id = document.getElementById('testId').value
    const function_id = document.getElementById('dataobjId').value
    const params = document.getElementById('testParams').value
    const description = document.getElementById('saveObjDescription').value
    const comment = document.getElementById('saveObjComment').value
    const name = document.getElementById('saveObjName').value

    var fd = new FormData()

    const metadata = {
      'name': name,
      'owner_id': ownerid,
      'dobj_id': dataobject_id,
      'func_id': function_id,
      'params': params,
      'description': description,
      'comment': comment,
      'datatype': '/datatypes/json',
      'mimetype': 'application/json',
      'predecessors': []
    }

    const url = `http://localhost:5000/function/${function_id}/${dataobject_id}`

    console.log(url)
    console.log(metadata)

    const blob = new Blob([JSON.stringify(metadata, null, 2)], {type : 'application/json'});
    fd.append("metadata", blob, "metadata")

    const res = await fetch(url, {
      method: 'POST',
      body: fd
    })
    const result = await res.json()
    if (result.id) {
        await Router.push(`/dobj/X${result.id}`)
    }
  } catch (error) {
    console.error(error)
  }
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

      <div>

        <Card
        backgroundColor="white"
        elevation={0}
        display="flex">

        <Card
        marginLeft={10}
        borderStyle={'solid'}
        borderColor={'#e5e7eb'}
        backgroundColor={'#f9f9fb'}
        padding={10}>

          <DataContent datacontent={dobj.displayVersion}></DataContent>

        </Card>
        
        <Card>

          <Card
          marginLeft={10}
          borderStyle={'solid'}
          borderColor={'#e5e7eb'}
          backgroundColor={'#f9f9fb'}
          padding={10}>

            <Button appearance="primary" id="function30button" onClick={function30}>1. Function X30: Chloropleth Map from FIPS Codes</Button>
            <Pre id="testResults"></Pre>

          </Card>

          <Card
          marginTop={10}
          marginLeft={10}
          borderStyle={'solid'}
          borderColor={'#e5e7eb'}
          backgroundColor={'#f9f9fb'}
          padding={10}>

            <Button appearance="primary" id="function32button" onClick={function32}>2. Function X32: Filter CSV by Text</Button>
            <Pre id="testResults2"></Pre>

          </Card>

          <Card
          marginTop={10}
          marginLeft={10}
          borderStyle={'solid'}
          borderColor={'#e5e7eb'}
          backgroundColor={'#f9f9fb'}
          padding={10}>
          
            <Button appearance="primary" id="function33button" onClick={function33}>3. Function X33: Aggregate CSV Mean</Button>
            <Pre id="testResults3"></Pre>

          </Card>

        </Card>

        </Card>

        <div style={{marginTop: '10px', paddingTop: '10px', borderTop: "1px solid gray", display: "none"}} id="saveButtonDisplay">
        <Popover
            bringFocusInside
            content={
            <Pane
              width={800}
              height={400}
              paddingX={40}
              display="flex"
              alignItems="left"
              justifyContent="center"
              flexDirection="column"
            >

              Name: <TextInput width="60" id="saveObjName" /> <br />
              Description: <TextInput width="60" id="saveObjDescription"/> <br />
              Comment: <TextInput width="60" id="saveObjComment"/> <br />

              <Button appearance="primary" id="saveObjectButton" style={{width: "75px"}} onClick={saveObject}>Submit</Button>
            </Pane>
            }
            >
            <Button appearance="primary" id="saveObjectButton">Save Data Object</Button>
            </Popover>

        </div>

      </div>
    )
}

export default Suggestions
