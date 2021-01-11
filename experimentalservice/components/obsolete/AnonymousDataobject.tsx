import React, { useState} from 'react'
import Router from 'next/router'
import DataContent from './DataContent'
import Dependencies from './Dependencies'
import ReactMarkdown from 'react-markdown'
import Post, {PostProps} from "./Post"
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

export type AnonymousDataobjProps = {
    version: {
        id: number;
        timestamp: string;
        dobj: {
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
}

const AnonymousDataobject: React.FC<{dobj: AnonymousDataobjProps}> = ({dobj}) => {
  const [tabIndex, setTabIndex] = useState(0)
  const objLink = "http://localhost:3000/anonobj/" + dobj.version.dobj.id

    return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>

          <Pane flex={1} > 
            <Heading size={800}>Anonymous object {dobj.version.dobj.id}</Heading>

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
              ({dobj.version.dobj.datatype}) <Link size={300} color="muted" href={objLink}>{objLink}</Link>

            </Paragraph>
            <Paragraph size={300} color="muted">
                Created by user {dobj.version.dobj.owner.name} ({dobj.version.dobj.owner.email}) on {dobj.version.dobj.timestamp}
            </Paragraph>
            </Pane>
          </Pane>

        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
        <Tablist>
             {['Overview', 'Dependencies', 'Related Objects', 'Suggestions'].map(
                (tab, index) => (
                  <Tab
                    key={tab}
                    isSelected={tabIndex === index}
                    onSelect={() => setTabIndex(index)}
                  >
                    {tab}
                  </Tab>
                )
              )}
        </Tablist>
        </Pane>
        { tabIndex == 0 &&
              <Card
              backgroundColor="white"
              elevation={0}
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
      
        <DataContent datacontent={dobj.version.dobj}></DataContent>
        </Card>

      }

      { tabIndex == 1 &&
        <Dependencies dobj={dobj.version.dobj}></Dependencies>
      }   

      { tabIndex == 2 &&
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>Related Objects</Text>

      </Card>}

      { tabIndex == 3 &&
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>Suggestions</Text>

      </Card>}
        </Pane>)
}

export default AnonymousDataobject
