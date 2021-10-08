import React, { useState} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown';
import { readString } from 'react-papaparse';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import Post, {PostProps} from "./Post"
import { majorScale, Text, Code, Pre, Pane, Heading, Button, Popover, TextInput, Textarea, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

import Prism from "prismjs";

import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
// import 'prismjs/components/prism-clike';
// import 'prismjs/components/prism-javascript';

export type DataContentProps = {
    dobj: {
        optionalName: string;
        id: number;
        timestamp: string;
        datatype: string;
        comment: string;
        owner: {
            id: number;
            name: string
            email: string
        }
    }
}

function htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


async function toCVSTable(contents) {

}

async function testFunction() {
  const testId = document.getElementById('testId').value
  const testParams = document.getElementById('testParams').value
  const saveButtonDisplay = document.getElementById('saveButtonDisplay')
  const dataobjId = document.getElementById('dataobjId').value
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

const DataContent: React.FC<{datacontent: DataContentProps}> = ({datacontent}) => {
    let imgstr = ""
    let csvData = ""
    let csvTable = [[]]

    let editMode = false

    const handleEditButton = () => {
      const area = document.getElementById('codeEditor')
      const display = document.getElementById('functionDisplay')
      const editButton = document.getElementById('editFunction')
      const saveButton = document.getElementById('saveEditFunction')

      area.style.display = ''
      display.style.display = 'none'
      editButton.style.display = 'none'
      saveButton.style.display = 'inline'
      editMode = true
    }

    const handleSaveEditButton = () => {
      const area = document.getElementById('codeEditor')
      const display = document.getElementById('functionDisplay')
      const editButton = document.getElementById('editFunction')
      const saveButton = document.getElementById('saveEditFunction')

      area.style.display = 'none'
      display.style.display = ''
      editButton.style.display = 'inline'
      saveButton.style.display = 'none'
      editMode = false
    }

    if (datacontent.datatype == "/datatypes/img" || datacontent.datatype == "/datatypes/pdf") {
        imgstr = "data:" + datacontent.contents.mimetype + ";base64, " + datacontent.contents.contents
    }
    else if (datacontent.datatype == '/datatypes/csv') {
      csvData = Buffer.from(datacontent.contents.contents, 'base64').toString().trim()
      csvTable = readString(csvData, {preview: 100}).data;
    }
    return (
        <Pane padding={majorScale(1)}>
        { datacontent.datatype == "/datatypes/json" &&
          <Pane display="flex" >
            <Pre>
            {JSON.stringify(JSON.parse(Buffer.from(datacontent.contents.contents, 'base64').toString()), null, 4)}
            </Pre>
          </Pane>
        }
        { datacontent.datatype == "/datatypes/xml" &&
          <Pane background="tint1" display="flex" >
            <Pre>
            {Buffer.from(datacontent.contents.contents, 'base64').toString()}
            </Pre>
          </Pane>
        }
        { datacontent.datatype == "/datatypes/csv" &&
          <Pane display="flex">
            <Table border background="tint1">
                <Table.Body>
                    {csvTable.map((row, idx) => (
                        <Table.Row key={row + idx}>
                            {row.map((cell, cellidx) => (
                                <Table.TextCell maxWidth={'400px'} key={cell + cellidx}>{cell}</Table.TextCell>
                            ))}
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
          </Pane>
        }

        { datacontent.datatype == "/datatypes/img" &&
            <Pane display="flex" >
                <Pre>
                <img src={imgstr}/>
                </Pre>
            </Pane>
        }

        { datacontent.datatype == "/datatypes/pdf" &&
            <Pane display="flex" >
                <embed src={imgstr} width="1200" height="800"/>
            </Pane>
        }

        { datacontent.datatype == "/datatypes/datacolumn" &&
          <Pane background="tint1" display="flex" >
            <Paragraph>

              <Text>
                Column Header: </Text> <Strong> {datacontent.ColumnData[0].headerlabel}
              </Strong>
              </Paragraph>
            <br></br>
            <Pre>     </Pre>
            <p></p>

              <Paragraph>
            <Text>
                Column Basic Type: </Text>
            <Strong>
                {datacontent.ColumnData[0].typedesc}
            </Strong>
            </Paragraph>
          </Pane>
        }


        { datacontent.datatype == "/datatypes/schema" &&
          <Pane background="tint1" >
            <Table>
              <Table.Head>
              <Table.TextHeaderCell>
                  Column Name
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                  Column Description
              </Table.TextHeaderCell>
              </Table.Head>
            <Table.Body>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].colname1}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].coldesc1}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].colname2}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].coldesc2}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].colname3}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].coldesc3}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].colname4}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].coldesc4}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].colname5}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.SchemaData[0].coldesc5}
                 </Table.TextCell>
                </Table.Row>
            </Table.Body>
            </Table>
          </Pane>
        }
        { datacontent.datatype == "/datatypes/function" &&
        <div>
          <Button appearance="primary" id="editFunction" style={{float: 'right',  marginRight: '-80px'}} onClick={handleEditButton}>
            Edit
          </Button>
          <Button appearance="primary" id="saveEditFunction" style={{float: 'right',  marginRight: '-80px', display: 'none'}} onClick={handleSaveEditButton}>
            Save
          </Button>
          <Textarea id='codeEditor' value={JSON.parse(Buffer.from(datacontent.contents.contents, 'base64').toString())} style={{height: '800px', width: '1200px', fontFamily: "Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace", display: 'none'}}>
          </Textarea>
          <SyntaxHighlighter language="python" id="functionDisplay">
          {JSON.parse(Buffer.from(datacontent.contents.contents, 'base64').toString())}
          </SyntaxHighlighter>
        <div>
        <br />
        <table>
        <tr><td>
        Test on data object ID:
        </td><td>
        <TextInput id='testId' />
        </td></tr>
        <tr><td>
        Parameters (comma-separated):
        </td><td>
        <TextInput id='testParams' size="50" />
        </td></tr>
        <tr><td colSpan="2">
        <input type="hidden" id="dataobjId" value={datacontent.dataobject.id} />
        <Button appearance="primary" id="testFunctionButton" onClick={testFunction}>Apply Function</Button>
        </td></tr>
        </table>
        </div>

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
        <Pre id="testResults"></Pre>

        </div>
        }

        </Pane>
    )
}

export default DataContent
