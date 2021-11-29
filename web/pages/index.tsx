import React from 'react'
import { GetServerSideProps } from 'next'
import Layout from '../components/Layout'
import Router from 'next/router'
import Feed, { FeedProps } from '../components/Feed'
import useSWR, { useSWRConfig } from 'swr'
import { majorScale, Table, Paragraph, Heading, Card, Pane, Text } from 'evergreen-ui'
import { useSession } from 'next-auth/client'

type UserProps = {

}

// <Card margin={32}>
//   <Text>Recent activity</Text>
//     <Card margin={8}>
//       <Feed props={props}/>
//     </Card>
// </Card>

const Blog : React.FC<{dobj: UserProps}> = ({dobj}) => {
  const [session, loading] = useSession();
  const fetcher = url => fetch(url).then(r => r.json())

  if (loading) return <div>loading...</div>
  
  if (session === undefined || session === null) {
    var userUrl = '/api/users/' + "nologin"
  } else {
    var userUrl = '/api/users/' + session.user.email
  }
  const {data, error, isValidating, mutate} = useSWR(userUrl, fetcher)

  if (!data) return <div>loading...</div>

  return (
    <Layout>
      <div className="page">
        {(! session || ! session.user) &&
        <Heading size={800}>Please log in.</Heading>
        }

        {session && session.user &&
        <Pane>
        <Heading size={800}>Welcome, {session.user.name}</Heading>

         <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={600}>Known Collaborations</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                You have  {data.collabs.length} Known Collaborations.
                
                {data.collabs.length > 0 &&
                <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Local File
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Share
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Remote File
                  </Table.TextHeaderCell>
                  <Table.TextHeaderCell>
                    Curation status
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>
                {data.collabs.map(c => (
                  <Table.Row key={c.userfile.uuid} isSelectable
                  onSelect={() => Router.push(c.ds ? `/dataset/${c.ds.uuid}` : `/byteset/${c.bs.md5hash}`)}>
                    <Table.TextCell>{c.userfile.filename} {c.userfile.latest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{(c.userfile.modified <
                    c.remotefile.modified) ? 'Sent to ' +
                    c.remotefile.username + ' on or before ' +
                    c.remotefile.modified : 'Received from ' +
                    c.remotefile.username + ' on or before ' +
                    c.userfile.modified}</Table.TextCell>
                    <Table.TextCell> {c.remotefile.filename} {c.remotefile.latest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    {c.ds && 
                      <Table.TextCell> <Text color="blue">{c.ds.title}</Text></Table.TextCell>}
                    {! c.ds && 
                      <Table.TextCell><Text color="red">Uncurated content {c.bs.md5hash}</Text></Table.TextCell>
                    }
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
            <Heading size={600}>Datasets</Heading>
            
            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">            
                You are maintaining {data.ds.length} Datasets.
                
                {data.ds.length > 0 &&
                <Table>
                <Table.Head>
                  <Table.TextHeaderCell>
                    Dataset Title
                  </Table.TextHeaderCell>                    
                  <Table.TextHeaderCell>
                    Description
                  </Table.TextHeaderCell>
                  <Table.TextHeaderCell>
                    Modified
                  </Table.TextHeaderCell>                    
                </Table.Head>
                <Table.Body>                
                {data.ds.map(ds => (
                  <Table.Row key={ds.uuid} isSelectable onSelect={() => Router.push(`/dataset/${ds.uuid}`)}>
                    <Table.TextCell>{ds.title} {ds.latest==1 ? '' :
                    '(Obsolete)'} </Table.TextCell>
                    <Table.TextCell>{ds.desc}</Table.TextCell>
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
                You have  {data.of.length} Known Location(s) in KNPS.

                {data.of.length > 0 &&
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
                {data.of.map(nd => (
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
        }

        <main>
        </main>
      </div>
    </Layout>
  )
}

export const getServerSideProps: GetServerSideProps = async () => {
  return {
    props: { },
  }
}

export default Blog
