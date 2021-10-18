import React from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import Post, {PostProps} from "./Post"
import { Pane, Heading, Button, Link, Strong } from 'evergreen-ui'

export type UserProps = {
  id: number;
  email: string;
  posts: {
    title: string;
    id: number;
  }
  name: string;
}

const User: React.FC<{user: UserProps}> = ({ user }) => {
  return (
    <Pane border display="flex" width="100%" padding={16} background="greenTint" borderRadius={3}>
      <Heading flex={1}>{user.name}</Heading>
      <br></br>
        <Heading flex={2}>{user.email}</Heading>
    </Pane>
  )
}

export default User