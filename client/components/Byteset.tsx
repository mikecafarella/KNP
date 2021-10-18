import React, { useState} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

export type FileProps = {
  fileid: string;
  filename: string;
  modified: string;
  owner: string;
  isLatest: number;
}

export type DatasetProps = {
  id: string;
  uuid: string;
  title: string;
  desc: string;
  modified: string;
  isLatest: number;
  owner: string;
}

export type BytesetProps = {
  id: string;
  created: string;
  format: string;

  files: FileProps[];
  nearDuplicates: FileProps[];  
  datasets: DatasetProps[];
}

const Byteset: React.FC<{dobj: BytesetProps}> = ({dobj}) => {

  const ownerid = 1

  return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={800}>Byteset {dobj.id}
            </Heading>

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
                First seen on {dobj.created}
            </Paragraph>

            <Paragraph size={300} color="muted">
                This data has type {dobj.format}
            </Paragraph>
            </Pane>

          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Content</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                This data cannot be examined.
            </Paragraph>
            </Pane>
          </Pane>
        </Pane>      


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Curated Datasets</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                This data is currently part of {dobj.datasets.length} Curated Dataset(s).

                {dobj.datasets.length > 0 &&
                <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Title
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Description
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Owner
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Modified
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>
                {dobj.datasets.map(ds => (
                  <Table.Row key={ds.fileid} isSelectable onSelect={() => Router.push(`/dataset/${ds.uuid}`)}>
                    <Table.TextCell>{ds.title} {ds.isLatest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{ds.desc}</Table.TextCell>
                    <Table.TextCell>{ds.owner}</Table.TextCell>                                        
                    <Table.TextCell>{ds.modified}</Table.TextCell>                    
                  </Table.Row>
                ))}
                </Table.Body>
                </Table>
                }

            </Paragraph>
            </Pane>
          </Pane>
        </Pane>      


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Known Locations</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                This data currently appears in {dobj.files.length} Known
                Location(s).

                {dobj.files.length > 0 &&
                <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Filename
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Owner
                  </Table.TextHeaderCell>
                  <Table.TextHeaderCell>
                    Modified
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>                
                {dobj.files.map(nd => (
                  <Table.Row key={nd.fileid} isSelectable onSelect={() => Router.push(`/knownlocation/${nd.fileid}`)}>
                    <Table.TextCell>{nd.filename} {nd.isLatest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{nd.owner}</Table.TextCell>
                    <Table.TextCell>{nd.modified}</Table.TextCell>                                        
                  </Table.Row>

                ))}
                </Table.Body>
                </Table>
                }

            </Paragraph>
            </Pane>
          </Pane>
        </Pane>      


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Similar Data</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                Near duplicates of this data can be found in {dobj.nearDuplicates.length} Known Location(s).

                {dobj.nearDuplicates.length > 0 &&
                <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Filename
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Owner
                  </Table.TextHeaderCell>
                  <Table.TextHeaderCell>
                    Modified
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>                
                {dobj.nearDuplicates.map(nd => (
                  <Table.Row key={nd.fileid} isSelectable onSelect={() => Router.push(`/knownlocation/${nd.fileid}`)}>
                    <Table.TextCell>{nd.filename} {nd.isLatest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{nd.owner}</Table.TextCell>
                    <Table.TextCell>{nd.modified}</Table.TextCell>                                        
                  </Table.Row>

                ))}
                </Table.Body>
                </Table>
                }
                
             </Paragraph>
            </Pane>
          </Pane>
        </Pane>      



      </Pane>
     )
  }

  export default Byteset
