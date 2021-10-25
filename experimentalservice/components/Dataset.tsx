import React, { useState} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import useSWR, { useSWRConfig } from 'swr'
import { majorScale, IconButton, TextareaField, TextInputField,
Popover, Icon, AddIcon, EditIcon, InfoSignIcon, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

export type DatasetProps = {
  id: string;
  datasetid: string;
  title: string;
  desc: string;
  owner: string;  
  modified: string;  
  latest: number;
  md5hash: string;
  prevId: string;
  nextId: string;
}


const Dataset: React.FC<{dobj: DatasetProps}> = ({dobj}) => {
  const [titleVal, setTitleVal] = useState("")
  const [descVal, setDescVal] = useState("")
  const [detailVal, setDetailVal] = useState("")
  const [commentVal, setCommentVal] = useState("")
  const [schemaVal, setSchemaVal] = useState("")
  
  
  const bytesetLink = "/byteset/" + dobj.md5hash
  const previousLink = "/dataset/" + dobj.prevId
  const nextLink = "/dataset/" + dobj.nextId

  const fetcher = url => fetch(url).then(r => r.json())

  const nodeUrl = '/api/nodes/' + dobj.id
  const commentsUrl = '/api/comments/' + dobj.id
  const contentUrl = '/api/bytesetdata/' + dobj.md5hash
  const schemasUrl = '/api/schemas/' + dobj.id
  const allSchemasUrl = '/api/allschemas'
  const qualityTestsUrl = '/api/qualitytests/' + dobj.id
  const allQualityTestsUrl = '/api/allqualitytests'
  
  const {data, error, isValidating, mutate} = useSWR(nodeUrl, fetcher)
  const {data: contentData, error: contentErro, isValidating: contentIsValidating, mutate: contentMutate} = useSWR(contentUrl, fetcher)  
  const {data: commentData, error: commentError, isValidating: commentIsValidating, mutate: commentMutate} = useSWR(commentsUrl, fetcher)
  const {data: schemasData, error: schemasError, isValidating: schemasIsValidating, mutate: schemasMutate} = useSWR(schemasUrl,
  fetcher)
  const {data: allSchemasData, error: allSchemasError, isValidating: allSchemasIsValidating, mutate: allSchemasMutate} = useSWR(allSchemasUrl, fetcher)      
  const {data: qualityTestsData, error: qualityTestsError, isValidating: qualityTestsIsValidating, mutate: qualityTestsMutate} = useSWR(qualityTestsUrl,
  fetcher)
  const {data: allQualityTestsData, error: allQualityTestsError, isValidating: allQualityTestsIsValidating, mutate: allQualityTestsMutate} = useSWR(allQualityTestsUrl, fetcher)



  if (!data || !commentData || !schemasData || !allSchemasData || !qualityTestsData || !allQualityTestsData ) return <div>loading...</div>
  
  return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >

            <Heading size={800}>Dataset '{data.title}'
            <Popover display="flex"
            alignItems="center" justifyContent="center"
            flexDirection="column" 
            onOpen={() => setTitleVal(data.title)}
            content={({close}) => (
            <Pane display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>
            <TextInputField
            label="Dataset Title"
            inputWidth="500px"
            description="Provide the Dataset's title."
            value={titleVal}
            onChange={e => setTitleVal(e.target.value)}/>
            <Pane >

            <Button appearance="primary" type="submit"
            onClick={async() => {
            data.title = titleVal
            mutate(data, false)
            close()

            await fetch(nodeUrl, {
              method: "POST",
              body: JSON.stringify({"uuid": data.uuid,
                    "field": "title",
                    "value": data.title})
            })

            }}>
            Accept
            </Button>

            <Button intent="danger" onClick={close}>
            Cancel
            </Button>
            </Pane>
            
            </Pane>
            </Pane>
            )}>
             <Button
            appearance="minimal" >
            <Icon icon={EditIcon} size={12} /></Button>
            </Popover>
            </Heading>


            <Pane marginLeft={majorScale(1)}>
            {data.latest == 0 &&
              <Heading size={600} color="red">This version is obsolete</Heading>

            }
            
            <Heading size={600}>{data.desc}
            <Popover display="flex"
            alignItems="center" justifyContent="center"
            flexDirection="column" 
            onOpen={() => setDescVal(data.desc)}
            content={({close}) => (
            <Pane display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>
            <TextInputField
            label="Dataset Description"
            inputWidth="500px"
            description="Provide an extended explanation of the
            Dataset here."
            value={descVal}
            onChange={e => setDescVal(e.target.value)}/>
            <Pane >

            <Button appearance="primary" type="submit"
            onClick={async() => {
            data.desc = descVal
            mutate(data, false)
            close()

            await fetch(nodeUrl, {
              method: "POST",
              body: JSON.stringify({"uuid": data.uuid,
                    "field": "desc",
                    "value": data.desc})
            })

            }}>
            Accept
            </Button>

            <Button intent="danger" onClick={close}>
            Cancel
            </Button>
            </Pane>
            
            </Pane>
            </Pane>
            )}>
             <Button
            appearance="minimal" >
            <Icon icon={EditIcon} size={12} /></Button>
            </Popover>
            </Heading>
            </Pane>




            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
                Owner: {dobj.owner}
            </Paragraph>

            <Paragraph size={300} color="muted">
                Last modified on: {dobj.modified}
            </Paragraph>

            <Paragraph size={300} color="muted">
                Version identifier: {dobj.id}
            </Paragraph>


            <Paragraph>{data.details}
            <Popover display="flex"
            width="2000"
            alignItems="center" justifyContent="center"
            flexDirection="column" 
            onOpen={() => setDetailVal(data.details)}
            content={({close}) => (
            <Pane display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>
            <TextareaField
            label="Dataset Details"
            inputWidth="1000px"
            inputHeight="500px"            
            description="Provide a detailed description here"
            value={detailVal}
            onChange={e => setDetailVal(e.target.value)}/>
            <Pane >

            <Button appearance="primary" type="submit"
            onClick={async() => {
            data.details = detailVal
            mutate(data, false)
            close()

            await fetch(nodeUrl, {
              method: "POST",
              body: JSON.stringify({"uuid": data.uuid,
                    "field": "details",
                    "value": data.details})
            })

            }}>
            Accept
            </Button>

            <Button intent="danger" onClick={close}>
            Cancel
            </Button>
            </Pane>
            
            </Pane>
            </Pane>
            )}>
             <Button
            appearance="minimal" >
            <Icon icon={EditIcon} size={12} /></Button>
            </Popover>
            </Paragraph>


            </Pane>
          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Content</Heading>
            <Paragraph size={300} color="muted">
                This Dataset contains Content <a href={bytesetLink}>{dobj.md5hash}</a> 
                <Popover width={240} height={240} display="flex"
                alignItems="center" justifyContent="center"
                flexDirection="column" content={
                <Text>Created by user on October 1</Text>
                }>
                <Button appearance="minimal" > <Icon icon={InfoSignIcon} color="info" size={12} /></Button>
                </Popover>
            </Paragraph>

            <Pane>
            </Pane>
          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Comments</Heading>
               {! commentData.comments &&
               <Paragraph size={300} color="muted">
                This Dataset has no comments.
               </Paragraph>
               }

               {commentData.comments &&
              <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Comment
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Date Posted
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Author
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>
                {commentData.comments.map(c => (
                  <Table.Row>
                    <Table.TextCell>{c.comment}</Table.TextCell>
                    <Table.TextCell>{c.modified}</Table.TextCell>
                  <Table.TextCell>{c.author}</Table.TextCell>              
                </Table.Row>
                ))}
                </Table.Body>
                </Table>
               }

            <Popover display="flex"
            width="2000"
            alignItems="center" justifyContent="center"
            flexDirection="column" 
            content={({close}) => (
            <Pane display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>
            <TextareaField
            label="New Comment"
            inputWidth="800px"
            inputHeight="100px"
            description="Add a new comment about the Dataset"
            value={commentVal}
            onChange={e => setCommentVal(e.target.value)}/>
            <Pane >

            <Button appearance="primary" type="submit"
            onClick={async() => {
            commentMutate(commentData, false)
            close()

            await fetch(commentsUrl, {
              method: "POST",
              body: JSON.stringify({"uuid": data.uuid,
                    "property": "HasComment",
                    "value": commentVal})
            })
            setCommentVal("")
            commentMutate(commentData)            

            }}>
            Accept
            </Button>

            <Button intent="danger" onClick={close}>
            Cancel
            </Button>
            </Pane>
            
            </Pane>
            </Pane>
            )}>
             <Button
            appearance="minimal" >
            <Icon icon={AddIcon} size={12} /></Button>
            </Popover>
            
          </Pane>
        </Pane>




        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Schemas</Heading>

               {(! schemasData.schemas || schemasData.schemas.length == 0) &&
               <Paragraph size={300} color="muted">
                This Dataset has no Schemas.
               </Paragraph>
               }

               {schemasData.schemas && schemasData.schemas.length > 0 &&
              <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Schema
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Description
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Status
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>
                {schemasData.schemas.map(s => (
                  <Table.Row>
                    <Table.TextCell>{s.title}</Table.TextCell>
                    <Table.TextCell>{s.desc}</Table.TextCell>
                    <Table.TextCell><Text color="orange">Evaluating</Text></Table.TextCell>              
                </Table.Row>
                ))}
                </Table.Body>
                </Table>
               }


            <Popover display="flex"
            width="2000"
            alignItems="center" justifyContent="center"
            flexDirection="column" 
            content={({close}) => (
            <Pane display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>

            <Table>
            <Table.Head>
            <Table.TextHeaderCell>
              Schema
            </Table.TextHeaderCell>              
            <Table.TextHeaderCell>
              Description
            </Table.TextHeaderCell>              
            <Table.TextHeaderCell>
            </Table.TextHeaderCell>              
            </Table.Head>
            <Table.Body>
            {allSchemasData.schemas.map(s => (
              <Table.Row>
                <Table.TextCell>{s.title}</Table.TextCell>
                <Table.TextCell>{s.desc}</Table.TextCell>
                <Table.TextCell>
                <Button appearance="primary"
                type="submit"
                onClick={async() => {
                  schemasMutate(schemasData, false)
                  close()

                  await fetch(schemasUrl, {
                    method: "POST",
                    body: JSON.stringify({"targetSchema": s.uuid})
                  })
                  schemasMutate(schemasData)
                }}>
                Add Schema
                </Button>
                </Table.TextCell>
             </Table.Row>
             ))}
            </Table.Body>
            </Table>
                
            <Pane >
            <Button intent="danger" onClick={close}>
            Cancel
            </Button>
            </Pane>
            
            </Pane>
            </Pane>
            )}>
             <Button
            appearance="minimal" >
            <Icon icon={AddIcon} size={12} /></Button>
            </Popover>
          </Pane>
        </Pane>



        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Quality Tests</Heading>

               {(! qualityTestsData.qualitytests || qualityTestsData.qualitytests.length == 0) &&
               <Paragraph size={300} color="muted">
                This Dataset has no Quality Tests.
               </Paragraph>
               }

               {qualityTestsData.qualitytests && qualityTestsData.qualitytests.length > 0 &&
              <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Quality Test
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Description
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Status
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>
                {qualityTestsData.qualitytests.map(s => (
                  <Table.Row>
                    <Table.TextCell>{s.title}</Table.TextCell>
                    <Table.TextCell>{s.desc}</Table.TextCell>
                    <Table.TextCell><Text color="orange">Evaluating</Text></Table.TextCell>              
                </Table.Row>
                ))}
                </Table.Body>
                </Table>
               }


            <Popover display="flex"
            width="2000"
            alignItems="center" justifyContent="center"
            flexDirection="column" 
            content={({close}) => (
            <Pane display="flex" padding={majorScale(1)} border>
            <Pane flex={1}>

            <Table>
            <Table.Head>
            <Table.TextHeaderCell>
              Quality Test
            </Table.TextHeaderCell>              
            <Table.TextHeaderCell>
              Description
            </Table.TextHeaderCell>              
            <Table.TextHeaderCell>
            </Table.TextHeaderCell>              
            </Table.Head>
            <Table.Body>
            {allQualityTestsData.qualitytests.map(s => (
              <Table.Row>
                <Table.TextCell>{s.title}</Table.TextCell>
                <Table.TextCell>{s.desc}</Table.TextCell>
                <Table.TextCell>
                <Button appearance="primary"
                type="submit"
                onClick={async() => {
                  qualityTestsMutate(qualityTestsData, false)
                  close()

                  await fetch(qualityTestsUrl, {
                    method: "POST",
                    body: JSON.stringify({"targetQualityTest": s.uuid})
                  })
                  qualityTestsMutate(qualityTestsData)
                }}>
                Add Quality Test
                </Button>
                </Table.TextCell>
             </Table.Row>
             ))}
            </Table.Body>
            </Table>
                
            <Pane >
            <Button intent="danger" onClick={close}>
            Cancel
            </Button>
            </Pane>
            
            </Pane>
            </Pane>
            )}>
             <Button
            appearance="minimal" >
            <Icon icon={AddIcon} size={12} /></Button>
            </Popover>
          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Usage</Heading>
            <Paragraph size={300} color="muted">            
                This Dataset has been used 9,485 times by 254 distinct
                users and 134 distinct programs.
            </Paragraph>
            <Table>
              <Table.Head>
                <Table.TextHeaderCell>
                  Program Title
                </Table.TextHeaderCell>                    
                <Table.TextHeaderCell>
                  Program Description
                </Table.TextHeaderCell>                    
                <Table.TextHeaderCell>
                  Execution Count
                </Table.TextHeaderCell>                    
              </Table.Head>
            <Table.Body>
            <Table.Row>
              <Table.TextCell>ComputeGDP</Table.TextCell>
              <Table.TextCell>Computes real GDP over time.</Table.TextCell>
              <Table.TextCell>231</Table.TextCell>              
            </Table.Row>
            <Table.Row>
              <Table.TextCell>...</Table.TextCell>
              <Table.TextCell>...</Table.TextCell>
              <Table.TextCell>...</Table.TextCell>              
            </Table.Row>
            </Table.Body>
            </Table>

          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Embeddings and Featurization</Heading>
            <Paragraph size={300} color="muted">            
                This Dataset has 2 available embedding(s).
            </Paragraph>
            <Table>
              <Table.Head>
                <Table.TextHeaderCell>
                  Embedding Result
                </Table.TextHeaderCell>                    
                <Table.TextHeaderCell>
                  Last Modified
                </Table.TextHeaderCell>                    
              </Table.Head>
            <Table.Body>
            <Table.Row>
              <Table.TextCell>Allen Institute for AI Scientific Paper
              Embedding Effort</Table.TextCell>
              <Table.TextCell>May 7, 2020</Table.TextCell>              
            </Table.Row>
            <Table.Row>
              <Table.TextCell>GPT-3 Paper Embeddings</Table.TextCell>
              <Table.TextCell>July 23, 2018</Table.TextCell>              
            </Table.Row>
            </Table.Body>
            </Table>

          </Pane>
        </Pane>


        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Publication History</Heading>
            <Paragraph size={300}>            
                The best version of this Dataset was published on
                {dobj.modified}, X days ago.
            </Paragraph>
            <Paragraph size={300}>
                There have been 2 versions of this Dataset. The first was published on
                {dobj.modified}, X days ago.
            </Paragraph>
          </Pane>
        </Pane>



        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Version History</Heading>
            
            <Pane marginLeft={majorScale(1)}>
                {dobj.prevId.length > 0 &&
                <Paragraph size={300} >
                   <a href={previousLink}>See the previous version</a>
                </Paragraph>   
                 }
                {dobj.prevId.length == 0 &&
                <Paragraph size={300} >
                 This is the first observed version of the Dataset.
                </Paragraph>                    
                 }
                {dobj.nextId.length > 0 &&
                <Paragraph size={300} >
                   <a href={nextLink}>See the next version</a>
                </Paragraph>   
                 }
                {dobj.nextId.length == 0 &&
                <Paragraph size={300} >
                 This is the latest observed version of the Dataset.
                </Paragraph>                    
                 }
            </Pane>
          </Pane>
        </Pane>      



      </Pane>
     )
  }

  export default Dataset

