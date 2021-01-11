import React, { useState } from 'react'
import { GetServerSideProps } from "next"
import Layout from '../components/Layout'
import Router from 'next/router'
import { Button, FilePicker, SelectField, Textarea } from 'evergreen-ui'
import { TextInput, TextInputField, Combobox, TextareaField, Pane, Heading, majorScale, Text } from 'evergreen-ui'


const NewObj: React.FC = (props) => {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [comment, setComment] = useState('')
  const [datatype, setDataType] = useState('')
  const [imgpath, setImagePath] = useState('')
  const [csvpath, setCSVPath] = useState()
  const [jsonpath, setJSONPath] = useState()
  const [pynumber, setPyNumber] = useState(0)
  const [pystring, setPyString] = useState('')
  const [datacolumnheader, setDataColumnHeaderString] = useState('')
  const [datacolumntype, setDataColumnTypeString] = useState('')

  const [schemaLabel1, setSchemaLabel1] = useState('')
  const [schemaLabel2, setSchemaLabel2] = useState('')
  const [schemaLabel3, setSchemaLabel3] = useState('')
  const [schemaLabel4, setSchemaLabel4] = useState('')
  const [schemaLabel5, setSchemaLabel5] = useState('')
  const [schemaType1, setSchemaType1] = useState('')
  const [schemaType2, setSchemaType2] = useState('')
  const [schemaType3, setSchemaType3] = useState('')
  const [schemaType4, setSchemaType4] = useState('')
  const [schemaType5, setSchemaType5] = useState('')

  const ownerid = 1

  const submitData = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    try {
      var fd = new FormData()
      switch (datatype) {
        case "/datatypes/json": {
          fd.append("jsonpath", jsonpath, "filecontents")
          break
        }
        case "/datatypes/csv": {
          fd.append("csvpath", csvpath, "filecontents")
          break
        }
        case "/datatypes/img": {
          fd.append("imgpath", imgpath, "filecontents")
          break
        }
        default: {
          break
        }
      }

      const metadata = {name, 
                      description, 
                      comment, 
                      datatype, 
                      pystring, 
                      pynumber, 
                      ownerid, 
                      datacolumnheader, 
                      datacolumntype,
                      schemaLabel1,
                      schemaType1,
                      schemaLabel2,
                      schemaType2,
                      schemaLabel3,
                      schemaType3,
                      schemaLabel4,
                      schemaType4,
                      schemaLabel5,
                      schemaType5,
                  }
      const s = JSON.stringify(metadata)
      fd.append("metadata", s)

      const res = await fetch(`http://localhost:3000/api/createdataobj`, {
        method: 'POST',
        body: fd
      })
      const result = await res.json()
      if (result.resultcode == "success") {  
          await Router.push('/')
      }
    } catch (error) {
      console.error(error)
    }
  }

  let schemaElts = []
  for (var x of props.dataColumns) {
    schemaElts.push({label: x.name + " (X" + x.id + ")",
      id: x.id})
  }

  return (
    <Layout>
      <Heading size={800}>Create</Heading>
      <div>
        <form
          onSubmit={submitData}>
          <TextInputField
            autoFocus
            label="Data Title"
            required
            onChange={e => setName(e.target.value)}
            placeholder="Maybe 'Daily COVID Cases', or 'US GDP 1945-2020'"
            type="text"
            value={name}
          />
          <TextInputField
            onChange={e => setDescription(e.target.value)}
            label="Data Description"
            required
            placeholder="Maybe 'Daily COVID Cases, downloaded daily from covidtrackingproject'"
            type="text"
            value={description}
          />
          <SelectField
            label="Data Type"
            description="What kind of data are you providing?"
            required
            onChange={e => setDataType(e.target.value)}
            >

                <option value="" selected>[Choose One]</option> 
                <option value="/datatypes/json">JSON</option> 
                <option value="/datatypes/csv">CSV</option> 
                <option value="/datatypes/img">Image</option> 
                <option value="/datatypes/pynum">Python Number</option> 
                <option value="/datatypes/pystring">Python String</option> 
                <option value="/datatypes/datacolumn">Data Column</option> 
                <option value="/datatypes/schema">Schema</option> 
            </SelectField>


          <Pane background="greenTint" border padding={16} borderRadius={4} display={datatype == "/datatypes/json" ? "flex" : "none"}>
             <Pane flex={1} alignItems="center" display="flex">
                <Heading is="h3"> JSON Upload </Heading>
             </Pane>   
             <FilePicker
                width={majorScale(50)}
                onChange={e => setJSONPath(e[0])}
                name="jsonfile"
                multiple={false}
                placeholder="Choose the JSON file here"/>
           </Pane>  

           <Pane background="blueTint" border padding={16} borderRadius={4} display={datatype == "/datatypes/csv" ? "flex" : "none"}>
             <Pane flex={1} alignItems="center" display="flex">
                <Heading is="h3"> CSV Upload </Heading>
             </Pane>   
             <FilePicker
                width={majorScale(50)}
                onChange={e => setCSVPath(e[0])}
                multiple={false}
                name="csvfile"
                placeholder="Choose the CSV file here"/>
           </Pane>  

           <Pane background="yellowTint" border padding={16} borderRadius={4} display={datatype == "/datatypes/img" ? "flex" : "none"}>
             <Pane flex={1} alignItems="center" display="flex">
                <Heading is="h3"> Image Upload </Heading>
             </Pane>   
             <FilePicker
                width={majorScale(50)}
                onChange={e => setImagePath(e[0])}
                name="imgfile"
                placeholder="Choose the image file here"/>
           </Pane>  

           <Pane background="orangeTint" border padding={16} borderRadius={4} display={datatype == "/datatypes/pynum" ? "flex" : "none"}>
             <Pane flex={1} alignItems="center" display="flex">
                <Heading is="h3"> Python Number </Heading>
             </Pane>   
             <TextInput
               onChange={e => setPyNumber(e.target.value)}
               name="pynumfield"
               value={pynumber}
               placeholder="Enter the number here"
               />
           </Pane>  

           <Pane background="blueTint" border padding={16} borderRadius={4} display={datatype == "/datatypes/pystring" ? "flex" : "none"}>
             <Pane flex={1} alignItems="center" display="flex">
                <Heading is="h3"> Python String </Heading>
             </Pane>   
             <TextInput
               onChange={e => setPyString(e.target.value)}
               name="pystringfield"
               value={pystring}
               placeholder="Enter the string here"
               />
           </Pane>  

           <Pane background="greenTint" border padding={16} borderRadius={4} display={datatype == "/datatypes/datacolumn" ? "flex" : "none"}>
             <Pane flex={1} alignItems="center" display="flex">
                <Heading is="h3"> Data Column </Heading>
             </Pane>   
             <TextInput
               onChange={e => setDataColumnHeaderString(e.target.value)}
               name="datacolumnheaderfield"
               value={datacolumnheader}
               placeholder="Enter the column header here"
               />
             <TextInput
               onChange={e => setDataColumnTypeString(e.target.value)}
               name="datacolumntypefield"
               value={datacolumntype}
               placeholder="Enter the column type here"
               />
           </Pane>  

           <Pane background="purpleTint" border flexDirection="column" padding={16} borderRadius={4} display={datatype == "/datatypes/schema" ? "flex" : "none"}>
             <Heading flex={1} is="h3"> Schema </Heading>
               <Pane flex={1} alignItems="center" display="flex" padding={8}>
                  <Pane flex={1}>
                    <TextInput 
                        name='collabel' 
                        placeholder='e.g., Employee Name'
                        onChange={e => setSchemaLabel1(e.target.value)}>
                        </TextInput>
                  </Pane>
                  <Pane flex={2}>
                    <Combobox openOnFocus 
                              items={schemaElts} 
                              itemToString={item => item ? item.label : ''} 
                              placeholder='Choose a column type'
                              onChange={e => setSchemaType1(e.id)}/>
                  </Pane>
               </Pane>   
               <Pane flex={1} alignItems="center" display="flex" padding={8}>
                  <Pane flex={1}>
                    <TextInput 
                        name='collabel' 
                        placeholder='e.g., Annual Salary'
                        onChange={e => setSchemaLabel2(e.target.value)}>
                        </TextInput>
                  </Pane>
                  <Pane flex={2}>
                    <Combobox openOnFocus 
                              items={schemaElts} 
                              itemToString={item => item ? item.label : ''} 
                              placeholder='Choose a column type'
                              onChange={e => setSchemaType2(e.id)}/>
                  </Pane>
               </Pane>   
               <Pane flex={1} alignItems="center" display="flex" padding={8}>
                  <Pane flex={1}>
                    <TextInput 
                        name='collabel' 
                        placeholder='e.g., Start date'
                        onChange={e => setSchemaLabel3(e.target.value)}>
                        </TextInput>
                  </Pane>
                  <Pane flex={2}>
                    <Combobox openOnFocus 
                              items={schemaElts} 
                              itemToString={item => item ? item.label : ''} 
                              placeholder='Choose a column type'
                              onChange={e => setSchemaType3(e.id)}/>
                  </Pane>
               </Pane>   
               <Pane flex={1} alignItems="center" display="flex" padding={8}>
                  <Pane flex={1}>
                    <TextInput 
                        name='collabel' 
                        placeholder='e.g., End date'
                        onChange={e => setSchemaLabel4(e.target.value)}>
                        </TextInput>
                  </Pane>
                  <Pane flex={2}>
                    <Combobox openOnFocus 
                              items={schemaElts} 
                              itemToString={item => item ? item.label : ''} 
                              placeholder='Choose a column type'
                              onChange={e => setSchemaType4(e.id)}/>
                  </Pane>
               </Pane>   
           </Pane>
           
         <TextareaField
            cols={50}
            onChange={e => setComment(e.target.value)}
            label="Extended Comments"
            placeholder="Optional comments"
            value={comment}
            rows={6}
          />

          <Pane padding={16}>  
            <Button type="submit" 
                disabled={!name ||!description || !datatype || 
                  (datatype=="/datatypes/json" && !jsonpath) || 
                  (datatype=="/datatypes/img" && !imgpath) || 
                  (datatype=="/datatypes/csv" && !csvpath) || 
                  (datatype=="/datatypes/pynum" && !pynumber) || 
                  (datatype=="/datatypes/datacolumn" && !datacolumnheader && !datacolumntype) || 
                  (datatype=="/datatypes/pystring" && !pystring) ||
                  (datatype=="/datatypes/schema" && !schemaLabel1 && !schemaType1)} 
                  appearance="primary">Create</Button>
            <Button intent="danger" onClick={() => Router.push('/')}>or Cancel</Button>
          </Pane>  
        </form>
      </div>
      <style jsx>{`
        .page {
          background: white;
          padding: 3rem;
          display: flex;
          justify-content: center;
          align-items: center;
        }

        input[type='text'],
        textarea {
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



export const getServerSideProps: GetServerSideProps = async () => {
  const res = await fetch("http://localhost:3000/api/listdataobjects")
  const dobjs = await res.json()
  {/**
    Grab the options for the datatype dropdown 
    */
  }
  const dataColumns = dobjs.filter(x => x.version.dobj.datatype == '/datatypes/datacolumn')
  console.log(dataColumns)
  return {
    props: {dataColumns},
  }
}


export default NewObj;
