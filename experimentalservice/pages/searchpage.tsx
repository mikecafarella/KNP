import React, {useState} from 'react'
import Router from 'next/router'
import Layout from '../components/Layout'

const SearchPage: React.FC = () => {
  const [searchText, setSearchText] = useState('')

  const submitData = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    try {
      // const body = {searchText}
      const body = {
        "query": {
          "match": {
            "_all": {
              "query": {searchText},
              "fuzziness": "AUTO"
            }
          }
        }
      }
      const res = await fetch(`http://localhost:9200/kgpl/_doc/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      console.log(data)
      Router.push('/listsearchrst')
    } catch (error) {
      console.error(error)
    }
  }

  return (
  <Layout>
    <div className="page">
      <form
        onSubmit={submitData}>
        <h1>Search</h1>
        <input
          autoFocus
          onChange={e => setSearchText(e.target.value)}
          placeholder="Search Object"
          type="text"
          value={searchText}
        />
        <input
          disabled={!searchText}
          type="submit"
          value="Search"
        />
        <a className="back" href="#" onClick={() => Router.push('/')}>
          or Cancel
        </a>
      </form>
    </div>
    <style jsx>{`
      .page {
        background: white;
        padding: 3rem;
        display: flex;
        justify-content: center;
      }

      input[type='text'] {
        width: 100%;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
        border: 0.125rem solid rgba(0, 0, 0, 0.2);
      }

      input[type='submit'] {
        background: #ececec;
        border: 0;
        padding: 1rem 2rem;
      }

      .back {
        margin-left: 1rem;
      }
    `}</style>
  </Layout>
  )
}

export default SearchPage