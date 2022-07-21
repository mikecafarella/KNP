import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import FileLog, { FileLogProps } from "../../components/FileLog"
import { Console } from "console"
import { useRouter } from 'next/router'


  const FileLogObj: React.FC<FileLogProps> = (props) => {
    return (
      <Layout>
        <Pane>
          <FileLog dobj={props} />
        </Pane>
      </Layout>
    )
  }

export const getServerSideProps: GetServerSideProps = async (context) => {
    const res = await fetch(`http://localhost:5000/filelogdata/${context.query.id}`)
    const data = await res.json()

    return {props: {...data, ...context.query}}
  }

export default FileLogObj
