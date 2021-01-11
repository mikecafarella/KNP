import React from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

export type FeedProps = {
  id: number;
  op: string;
  timestamp: string;
  owner: {
    name: string;
    email: string;
    id: int;
  }
  ref: {
    id: int;
    name: string;
  }
}
type Props = {
    feed: FeedProps[]
  }

const Feed: React.FC<{posts: FeedProps}> = ({ props }) => {
  return (
    <Table>
    <Table.Body height={240}>
       {props.feed.map(obj => (
       <Table.Row key={obj.id} isSelectable onSelect={() => Router.push(`/dobj/${obj.ref.id}`)}>
          <Table.TextCell>On {obj.timestamp}, {obj.owner.name} performed the <b>{obj.op}</b> operation on object {obj.ref.name} ({obj.ref.id})</Table.TextCell>
       </Table.Row>
      ))}
    </Table.Body>
  </Table>
  )
}

export default Feed