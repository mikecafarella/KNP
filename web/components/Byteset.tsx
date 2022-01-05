import React, { useState} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import { useSession } from 'next-auth/client'
import { readString } from 'react-papaparse';
import { majorScale, Pre, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

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

export type ContentProps = {
  hasContent: boolean;

}

export type BytesetProps = {
  id: string;
  created: string;
  format: string;
  content: ContentProps;

  files: FileProps[];
  nearDuplicates: FileProps[];  
  datasets: DatasetProps[];
}

const Byteset: React.FC<{dobj: BytesetProps}> = ({dobj}) => {
  const ownerid = 1
  const [session, loading] = useSession();  
  const createDatasetUrl = '/api/datasets/' + dobj.id

  return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={800}>Content {dobj.id}
            </Heading>

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
                First seen on {new Date(dobj.created * 1000).toLocaleString()}
            </Paragraph>

            <Paragraph size={300} color="muted">
                This data has type {dobj.filetype}
            </Paragraph>
            </Pane>

          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Content</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            { ! dobj.content.hasContent &&
              <Paragraph size={300} color="muted">            
                You do not have access to this content.
              </Paragraph>
            }

            { dobj.content.hasContent &&
              <Pane>
              <Paragraph size={300} color="muted">            
                A copy of this content has been cached.
              </Paragraph>

              { dobj.filetype == "text/plain" &&
              <Pane display="flex" border>
              <Pre>
                {Buffer.from(dobj.content.content).toString()}
              </Pre>
              </Pane>
              }


              { dobj.filetype == "image/png" &&
              <Pane display="flex" border>
                <img width="600px" src={"data:image/png;base64," + dobj.content.content}/>
              </Pane>
              }


              { dobj.filetype == "application/pdf" &&
                 <Pane display="flex" >
                     <embed src={"data:application/pdf;base64," + dobj.content.content} width="600" height="300"/>
                 </Pane>
              }


              { dobj.filetype == "text/csv" &&
             <Pane display="flex" border>
               <Table border background="tint1">
                   <Table.Body>
                       {readString(Buffer.from(dobj.content.content).toString().trim(), {preview: 10}).data.map((row, idx) => (
                           <Table.Row key={row + idx}>
                               {row.map((cell, cellidx) => (
                                   <Table.TextCell key={cell + cellidx}>{cell}</Table.TextCell>
                               ))}
                           </Table.Row>
                       ))}
                   </Table.Body>
               </Table>
             </Pane>
             }

              </Pane>              
              }
            </Pane>
          </Pane>
        </Pane>      


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Curated Datasets</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
            
            {dobj.datasets.length == 0 &&
            <Pane>
             <Text color="red">This Content is currently uncurated</Text>
            <Pane>             
            <Button appearance="primary" onClick={async() =>{
              await fetch(createDatasetUrl, {
                method: "POST",
                body: JSON.stringify({"user": session.user.email})
                })
              Router.push(`/byteset/${dobj.id}`)
            }}>Curate this Content</Button>
            </Pane>             
            </Pane>
             }

             {dobj.datasets.length > 0 &&
               <Paragraph size={300} color="muted">This Content is currently part of {dobj.datasets.length} Curated Dataset(s).</Paragraph>
             }

                {dobj.datasets.length > 0 &&
                <Table>
                <Table.Body>
                {dobj.datasets.map(ds => (
                  <Table.Row key={ds.fileid} isSelectable onSelect={() => Router.push(`/dataset/${ds.uuid}`)}>
                    <Table.TextCell>{ds.title} {ds.latest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{ds.desc}</Table.TextCell>
                    <Table.TextCell>{ds.owner}</Table.TextCell>                                        
                    <Table.TextCell>{new Date(ds.modified * 1000).toLocaleString()}</Table.TextCell>                    
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
            <Heading size={600}>Known Collaborations</Heading>

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
                This Content is currently part of {dobj.likelyCollaborations.length} Known Collaboration(s).

                {dobj.likelyCollaborations.length > 0 &&
                <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    User 1
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    File 1
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    User 2
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    File 2
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>
                  {dobj.likelyCollaborations.map(c => (
                  <Table.Row>
                    <Table.TextCell>{c.user1.username}</Table.TextCell>
                    <Table.TextCell>{c.user1.filename}</Table.TextCell>
                    <Table.TextCell>{c.user2.username}</Table.TextCell>
                    <Table.TextCell>{c.user2.filename}</Table.TextCell>
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
                This Content currently appears in {dobj.files.length} Known
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
                  <Table.Row key={nd.fileid} isSelectable onSelect={() => Router.push(`/knownlocation/${nd.uuid}`)}>
                    <Table.TextCell>{nd.filename} {nd.latest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{nd.username}</Table.TextCell>
                    <Table.TextCell>{new Date(nd.modified * 1000).toLocaleString()}</Table.TextCell>                                        
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
            <Heading size={600}>Known Locations for Similar Data</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                Near duplicates of this Content can be found in {dobj.nearDuplicates.length} Known Location(s).

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
                  <Table.Row key={nd.fileid} isSelectable onSelect={() => Router.push(`/knownlocation/${nd.uuid}`)}>
                    <Table.TextCell>{nd.filename} {nd.latest==1 ? '' :
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
