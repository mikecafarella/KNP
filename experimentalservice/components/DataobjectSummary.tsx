import React, { useState} from 'react'
import Router from 'next/router'
import DataContent from './DataContent'
import DataobjProps from './DataObject'

import Dependencies from './Dependencies'
import ReactMarkdown from 'react-markdown'
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'


const DataobjectSummary: React.FC<{dobj: DataobjProps}> = ({dobj}) => {
  let label = null
  const [tabIndex, setTabIndex] = useState(0)
  let objLink = ""
  let obj = ""
  if (dobj) {
    obj = dobj.dobj ? dobj.dobj : dobj
    label = dobj.label ? dobj.label : dobj.NameAssignment[0].objname
    objLink = "http://localhost:3000/dobj/" + "X" + label.id + (label.iscurrent ? "" : "/v" + dobj.id)
  }
  // <Strong size={500}>{label.iscurrent ? label.name : "Anonymous object:" + obj.id}</Strong> <Text size={300}></Text>
  return (
    <Pane width="100%">
    { dobj &&
        <Pane border>
        <Paragraph>
       <Strong size={500}>{label.name}</Strong> <Text size={300}></Text>
       </Paragraph>

        <Pane marginLeft={majorScale(1)}>
          <Paragraph>
            <Link size={300} href={objLink}> {objLink}</Link>
          </Paragraph>
          <Paragraph color="muted">
              <Text size={300}>Object {obj.id} from {obj.owner.name} ({obj.owner.email})</Text><br></br>
          </Paragraph>
        </Pane>
        <DataContent datacontent={obj}/>
        </Pane>
    }
    </Pane>

    )
  }

  export default DataobjectSummary
