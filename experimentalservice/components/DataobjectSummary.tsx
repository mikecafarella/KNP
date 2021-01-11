import React, { useState} from 'react'
import Router from 'next/router'
import DataContent from './DataContent'
import DataobjProps from './DataObject'

import Dependencies from './Dependencies'
import ReactMarkdown from 'react-markdown'
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'


const DataobjectSummary: React.FC<{dobj: DataobjProps}> = ({dobj}) => {
  const [tabIndex, setTabIndex] = useState(0)
  var objLink = ""
  if (dobj) {
    objLink = "http://localhost:3000/dobj/" + (dobj.label.iscurrent ? "X" + dobj.label.id : dobj.dobj.id)
  }

  return (
    <Pane width="100%">
    { dobj &&    
        <Pane border>
        <Paragraph>
       <Strong size={500}>{dobj.label.iscurrent ? dobj.label.name : "Anonymous object:" + dobj.dobj.id}</Strong> <Text size={300}></Text>
       </Paragraph>

        <Pane marginLeft={majorScale(1)}>
          <Paragraph>  
            <Link size={300} href={objLink}> {objLink}</Link>
          </Paragraph>  
          <Paragraph color="muted">  
              <Text size={300}>Object {dobj.dobj.id} from {dobj.dobj.owner.name} ({dobj.dobj.owner.email})</Text><br></br>
          </Paragraph>
        </Pane>
        <DataContent datacontent={dobj.dobj}/> 
        </Pane>
    }
    </Pane>

    )
  }
  
  export default DataobjectSummary
