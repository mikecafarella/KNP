import React, { useState} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import Post, {PostProps} from "./Post"
import { majorScale, Text, Code, Pre, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

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

async function testFunction() {
  const testId = document.getElementById('testId').value
  const dataobjId = document.getElementById('dataobjId').value
  const outputDiv = document.getElementById('testResults')

  outputDiv.innerHTML = "<div><br /><b>Test Results</b></div>"
  outputDiv.innerHTML += "<div>Running....</div>"

  const res = await fetch('http://localhost:5000/function/'+dataobjId+'/'+testId)
  const data = await res.json()

  let output = ""
  if (typeof(data) === 'object') {
    output = [JSON.stringify(data, null, 2)]
  }
  else {
    output = htmlEntities(data)
  }

  outputDiv.innerHTML = "<div><br /><b>Test Results</b></div>"
  outputDiv.innerHTML += "<div>"+output+"</div>"

}

const DataContent: React.FC<{datacontent: DataContentProps}> = ({datacontent}) => {
    var imgstr = ""
    if (datacontent.datatype == "/datatypes/img" || datacontent.datatype == "/datatypes/pdf") {
        imgstr = "data:" + datacontent.contents.mimetype + ";base64, " + datacontent.contents.contents
    }
    return (
        <Pane overflowY="scroll" background="tint1" padding={majorScale(1)}>
        { datacontent.datatype == "/datatypes/json" &&
          <Pane display="flex" >
            <Pre>
            {JSON.stringify(JSON.parse(Buffer.from(datacontent.contents.contents, 'base64').toString()), null, 4)}
            </Pre>
          </Pane>
        }

        { datacontent.datatype == "/datatypes/csv" &&
          <Pane display="flex" >
            <Pre>
            {String.fromCharCode.apply(null, JSON.parse(datacontent.CsvData[0].csvdata).contents.data)}
            </Pre>
            {/**
            <Table>
                <Table.Body>
                    {JSON.parse(datacontent.CsvData[0].csvdata).contents.data.map(row => (
                        <Table.row>
                            {row.map(cell => (
                                <Table.TextCell>cell</Table.TextCell>
                            ))}
                        </Table.row>
                    ))}
                </Table.Body>
            </Table>
             */}
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
          <Pane display="flex" >
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
          <Pane>
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
        <Pane display="flex" >
          <Pre>
          {JSON.parse(Buffer.from(datacontent.contents.contents, 'base64').toString())}
          </Pre>
        </Pane>
        <div>
        <br />
        Test on data object ID: <input id='testId' />
        <input type="hidden" id="dataobjId" value={datacontent.dataobject.id} />
        <input type="button" id="testFunctionButton" value="Run Test" onClick={testFunction}/>
        </div>

        <Pre id="testResults"></Pre>

        </div>
        }

        </Pane>
    )
}

export default DataContent
