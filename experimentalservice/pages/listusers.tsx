import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../components/Layout"
import User, { UserProps } from "../components/User"
import { UserSelect } from "@prisma/client"
import { Heading } from 'evergreen-ui'


type Props = {
  users: UserProps[]
}

const Users: React.FC<Props> = (props) => {
  return (
    <Layout>
      <div className="page">
        <Heading size={800}>Users</Heading>
        <main>
          {props.users.map((user) => (
            <div key={user.id} className="user">
              <User user={user} />
            </div>
          ))}
        </main>
      </div>
    </Layout>
  )
}

export const getServerSideProps: GetServerSideProps = async () => {
  const res = await fetch("http://localhost:3000/api/listusers")
  const users = await res.json()
  return {
    props: { users },
  }
}

export default Users
