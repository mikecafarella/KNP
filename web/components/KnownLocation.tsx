import React, { useState} from 'react'
import Router from 'next/router'
import ReactMarkdown from 'react-markdown'
import { majorScale, Text, Code, Pane, Heading, Button, Link, Strong, Paragraph, Tablist, Tab, Card, Table } from 'evergreen-ui'

export type FileProps = {
  fileid: string;
  filename: string;
  modified: string;
  owner: string;
  isLatest: number;
}

export type KnownLocationProps = {
  id: string;
  owner: string;
  filename: string;
  modified: string;
  synctime: string;
  prevId: string;
  nextId: string;
  isLatest: number;
  md5hash: string;
  nearDuplicates: FileProps[];
}

const KnownLocation: React.FC<{dobj: KnownLocationProps}> = ({dobj}) => {
  const ownerid = 1

  const bytesetLink = "/byteset/" + dobj.md5hash
  const previousLink = "/knownlocation/" + dobj.prevId
  const nextLink = "/knownlocation/" + dobj.nextId

  return (
      <Pane width="100%">
        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Heading size={800}>Known Location {dobj.filename}
            </Heading>

            <Pane marginLeft={majorScale(1)}>
            <Paragraph size={300} color="muted">
                Owner: {dobj.owner}
            </Paragraph>

            <Paragraph size={300} color="muted">
                Last modified on: {dobj.modified}
            </Paragraph>

            <Paragraph size={300} color="muted">
                Version identifier: {dobj.id}
            </Paragraph>

            <Paragraph size={300} color="muted">            
                This file contains <a href={bytesetLink}>Byteset {dobj.md5hash}</a>
            </Paragraph>

            </Pane>
          </Pane>
        </Pane>

        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Pane marginLeft={majorScale(1)}>
                {dobj.prevId.length > 0 &&
                <Paragraph size={300} >
                   <a href={previousLink}>See the previous version</a>
                </Paragraph>   
                 }
                {dobj.prevId.length == 0 &&
                <Paragraph size={300} >
                 This is the first observed version of the file.
                </Paragraph>                    
                 }
            </Pane>
          </Pane>
        </Pane>      

        <Pane display="flex" padding={majorScale(1)} border>
          <Pane flex={1} >
            <Pane marginLeft={majorScale(1)}>
                {dobj.nextId.length > 0 &&
                <Paragraph size={300} >
                   <a href={nextLink}>See the next version</a>
                </Paragraph>   
                 }
                {dobj.nextId.length == 0 &&
                <Paragraph size={300} >
                 This is the latest observed version of the file.
                </Paragraph>                    
                 }
            </Pane>
          </Pane>
        </Pane>      


      </Pane>
     )
  }

  export default KnownLocation

