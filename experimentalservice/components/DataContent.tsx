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

const DataContent: React.FC<{datacontent: DataContentProps}> = ({datacontent}) => {
    var imgstr = ""
    if (datacontent.datatype == "/datatypes/img") {
        const imgBytes = JSON.parse(datacontent.ImgData[0].img).contents.data
        console.log(imgBytes)
        imgstr = "data:image/png;base64, " + new Buffer(imgBytes).toString('base64')
    }
    return (
        <Pane overflowY="scroll" background="tint1" padding={majorScale(1)}>
        { datacontent.datatype == "/datatypes/json" &&
          <Pane display="flex" >
            <Pre>
            {JSON.stringify(JSON.parse(datacontent.JsonData[0].jsondata), null, 4)}
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
          <Pane>
            <Table>
              <Table.Head>
              <Table.TextHeaderCell>
                  Parameter
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                  Data Type
              </Table.TextHeaderCell>
              </Table.Head>
            <Table.Body>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramname1}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramdesc1}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramname2}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramdesc2}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramname3}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramdesc3}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramname4}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramdesc4}
                 </Table.TextCell>
                </Table.Row>
                <Table.Row>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramname5}
                 </Table.TextCell>
                 <Table.TextCell>
                     {datacontent.FunctionData[0].paramdesc5}
                 </Table.TextCell>
                </Table.Row>
            </Table.Body>
            </Table>
          </Pane>
        }

        </Pane>
    )
}

export default DataContent
