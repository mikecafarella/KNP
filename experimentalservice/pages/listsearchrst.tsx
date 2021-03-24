import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../components/Layout"
import SearchRst, { SearchRstProps } from "../components/SearchRst"
// import { UserSelect } from "@prisma/client"
import { Heading } from 'evergreen-ui'


type Props = {
  searchrsts: SearchRstProps[]
}

const SearchRsts: React.FC<Props> = (props) => {
  return (
    <Layout>
      <div className="page">
        <Heading size={800}>Search Results</Heading>
        <main>
          {/* console.log(props.searchrsts)
          {props.searchrsts.map((SearchRst) => (
            <div key={SearchRst._id} className="SearchRst">
              <SearchRst SearchRst={SearchRst} />
            </div>
          ))} */}
          {props.searchrsts.map((s)=>(console.log(s)))}
          {props.searchrsts.map((s)=>(
            <div key={s._id} className="SearchRst">
              <SearchRst searchrst={s} />
            </div>
          ))}
        </main>
      </div>
    </Layout>
  )
}

export const getServerSideProps: GetServerSideProps = async () => {
  const res = await fetch("http://localhost:9200/kgpl/_search")
  const hits = await res.json()
  console.log(hits.hits.hits)
  const searchrsts = hits.hits.hits
  return {
    props: {searchrsts},
  }
}

export default SearchRsts
