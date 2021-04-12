import React from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import Post, {PostProps} from "./Post"
import { Pane, Heading, Button, Link, Strong } from 'evergreen-ui'

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
  return (
    <Pane border display="flex" width="100%" padding={16} background="greenTint" borderRadius={3}>
      <Heading flex={1}>{searchrst._source.url}</Heading>
      <Heading flex={1}>{searchrst._source.comment}</Heading>
      <Heading flex={1}>{searchrst._source.owner}</Heading>
      <Heading flex={1}>{searchrst._source.pytype}</Heading>
    </Pane>
  )
}

export default SearchRst