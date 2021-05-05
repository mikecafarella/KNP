import React from 'react'
import { GetServerSideProps } from 'next'
import Layout from '../components/Layout'
import Feed, { FeedProps } from '../components/Feed'
import { Heading, Card, Pane, Text } from 'evergreen-ui'


type Props = {
  feed: FeedProps[]
}

// <Card margin={32}>
//   <Text>Recent activity</Text>
//     <Card margin={8}>
//       <Feed props={props}/>
//     </Card>
// </Card>

const Blog : React.FC<Props> = props => {
  return (
    <Layout>
      <div className="page">
        <Heading size={800}>Welcome to The Knowledge Network</Heading>
        <main>
        </main>
      </div>
    </Layout>
  )
}

export const getServerSideProps: GetServerSideProps = async () => {
  const res = await fetch('http://localhost:3000/api/feed')
  const feed = await res.json()

  return {
    props: { feed },
  }
}

export default Blog
