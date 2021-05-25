import React from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import Post, {PostProps} from "./Post"
import { Pane, Heading, Button, Link, Strong } from 'evergreen-ui'
import { Table } from 'evergreen-ui'

export type SearchRstProps = {
  _index: string;
  _type: string;
  _id: string;
  _score: string;
  _source:{
    url: string;
    owner: string;
    comment: string;
    pytype: string;
  }
}

const SearchRst: React.FC<{searchrst: SearchRstProps}> = ({ searchrst }) => {
  console.log(searchrst)
  // <Pane border display="flex" width="100%" padding={16} background="greenTint" borderRadius={3}>
  //   <Heading flex={1}><Link href={"/dobj/"+searchrst._id}>{searchrst._source.url}</Link></Heading>
  //   <Heading flex={1}>{searchrst._source.comment}</Heading>
  //   <Heading flex={1}>{searchrst._source.owner}</Heading>
  //   <Heading flex={1}>{searchrst._source.pytype}</Heading>
  // </Pane>
  return (
    <Table.Row>
      <Table.TextCell><Link href={"/dobj/"+searchrst._id}>{searchrst._source.url}</Link></Table.TextCell>
      <Table.TextCell>{searchrst._source.name}<br /><i>{searchrst._source.description}</i></Table.TextCell>
      <Table.TextCell>{searchrst._source.owner}</Table.TextCell>
      <Table.TextCell>{searchrst._source.pytype}</Table.TextCell>
    </Table.Row>
  )
}

export default SearchRst
