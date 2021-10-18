import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import Byteset, { BytesetProps } from "../../components/Byteset"
import { Console } from "console"
import { useRouter } from 'next/router'


  const BytesetObj: React.FC<BytesetProps> = (props) => {
    console.log(props)
    return (
      <Layout>
        <Pane>
          <Byteset dobj={props} />
        </Pane>
      </Layout>
    )
  }

export const getServerSideProps: GetServerSideProps = async (context) => {
    console.log(Byteset, context.query)

    const res = await fetch(`http://localhost:5000/bytesetdata/${context.query.id}`)
    const data = await res.json()

    return {props: {...data, ...context.query}}
  }

export default BytesetObj
