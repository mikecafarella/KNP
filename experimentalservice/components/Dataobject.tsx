import React, { useState} from 'react'
import Router from 'next/router'
import DataContent from './DataContent'
import Dependencies from './Dependencies'
import ReactMarkdown from 'react-markdown'
import Post, {PostProps} from "./Post"
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

export type UserProps = {
  id: number;
  name: string;
  email: string;
}

export type RawDataObjectProps = {
  id: number;
  timestamp: string;
  datatype: string;
  comment: string;
  isdeleted: number;
  owner: UserProps;
}

export type DataObjLabelProps = {
  name: string;
  id: number;
  desc: string;
  owner: UserProps;
  isdeleted: number;
  timestamp: string;
  iscurrent: boolean;
}

export type DataobjProps = {
  dobj: RawDataObjectProps;
  label: DataObjLabelProps;
  versions: array;
}

const Dataobject: React.FC<{dobj: DataobjProps}> = ({dobj}) => {
  const [tabIndex, setTabIndex] = useState(0)
  const [deleteId, setDeleteId] = useState(dobj.id)



  const ownerid = 1

  const submitData = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    try {
      var fd = new FormData()
      const metadata = {deleteId,
                  ownerid,
                  }
      const s = JSON.stringify(metadata)
      fd.append("metadata", s)

      const res = await fetch(`http://localhost:3000/api/deletedataobj`, {
        method: 'POST',
        body: fd
      })
      const result = await res.json()
      if (result.resultcode == "success") {
          await Router.push('/')
      }
    } catch (error) {
      console.error(error)
    }
  }

  var tabLabels = ['Overview', 'Dependencies', 'Versions', 'Related Objects', 'Suggestions', 'Delete']

  const overviewIndex = tabLabels.findIndex( (elt) => elt == 'Overview')
  const dependencyIndex = tabLabels.findIndex( (elt) => elt == 'Dependencies')
  const versionIndex = tabLabels.findIndex( (elt) => elt == 'Versions')
  const relatedObjectIndex = tabLabels.findIndex( (elt) => elt == 'Related Objects')
  const suggestionIndex = tabLabels.findIndex( (elt) => elt == 'Suggestions')
  const deleteIndex = tabLabels.findIndex( (elt) => elt == 'Delete')

  const dobjId = dobj.id[0] == 'X' ? dobj.id : 'X' + dobj.id
  const objLink = "http://localhost:3000/dobj/" + dobjId

  return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>

          <Pane flex={1} >
            <Heading size={800}>{dobj.name}

            {"(" + dobjId + ")"}
            </Heading>

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
              <Link size={300} color="muted" href={objLink}>{objLink}</Link>

            </Paragraph>
            <Paragraph size={300} color="muted">
                Created by user {dobj.owner.name} ({dobj.owner.email}) on {dobj.created}
            </Paragraph>

            <Paragraph size={300} color="muted">
                This object has type {dobj.displayVersion.datatype}
            </Paragraph>

              <Paragraph size={500}>
                    {dobj.desc}
              </Paragraph>

              <Paragraph size={500}>
                    Current Version (v{dobj.displayVersion.id}): {dobj.displayVersion.created} {dobj.displayVersion.comment ? " - " + dobj.displayVersion.comment : ""}
                    {dobj.displayVersion.id != dobj.versions[0].id &&
                    <div style={{color:'red'}}>
                      <b>Displayed Version</b> (v{dobj.versions[0].id}): {dobj.displayVersion.created} {dobj.displayVersion.comment ? " - " + dobj.displayVersion.comment : ""}
                    </div>
                   }
              </Paragraph>
            </Pane>
          </Pane>

        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Tablist>
                   {tabLabels.map(
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

      { tabIndex == overviewIndex &&
              <Card
              backgroundColor="white"
              elevation={0}
              display="flex"
              alignItems="center"
              justifyContent="center"
            >

        <DataContent datacontent={dobj.displayVersion}></DataContent>
        </Card>

      }

      { tabIndex == dependencyIndex &&
        <Dependencies dobj={dobj}></Dependencies>
      }

      { tabIndex == versionIndex &&
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Pane width="100%" overflowY="scroll" background="tint1" padding={majorScale(1)}>
        <Table>
          <Table.Head>
            <Table.TextHeaderCell>
                 Timestamp
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
                 Comment
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
                 Datatype
            </Table.TextHeaderCell>
            </Table.Head>
            <Table.Body>
            {dobj.versions.map(
               (version) => (
                 <Table.Row key="0" isSelectable onSelect={() => Router.push("/dobj/" + dobjId + "/?v=" + version.id)}>
                   <Table.TextCell>{version.readableDate}</Table.TextCell>
                   <Table.TextCell>{version.comment}</Table.TextCell>
                   <Table.TextCell>{version.datatype}</Table.TextCell>
                 </Table.Row>
               )
             )}
               </Table.Body>
            </Table>
        </Pane>

      </Card>}

      { tabIndex == relatedObjectIndex &&
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>Related Objects</Text>

      </Card>}

      { tabIndex == suggestionIndex &&
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
        alignItems="center"
        justifyContent="left"
        padding={8}
      >
        <Text>Suggestions</Text>

      </Card>}

      { tabIndex == deleteIndex &&
        <Card
        backgroundColor="white"
        elevation={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <form
          onSubmit={submitData}>
        <Card margin={8}
              alignItems="center"
              justifyContent="center">
        <Text>Do you want to delete this object? This operation cannot be undone</Text>
        </Card>
        <Button type="submit" appearance="primary" intent="danger">Delete</Button>
        </form>

      </Card>}


      </Pane>
     )
  }

  export default Dataobject
