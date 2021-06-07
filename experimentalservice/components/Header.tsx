import React from 'react'
import { useRouter } from 'next/router'
import { Pane, Heading, Button, Link } from 'evergreen-ui'
import { signIn, signOut, useSession } from 'next-auth/client'


const Header: React.FC = () => {
  const router = useRouter()
  const isActive: (pathname: string) => boolean =
    pathname => router.pathname === pathname

  const [session, loading] = useSession();

  var button;
  var addObjButton;

  if (session) {
    button = <Button marginRight={16} onClick={() => signOut({callbackUrl: '/'})}>Logout user {session.user.name} (ID {session.userid}) </Button>
    addObjButton = <Button appearance="primary" onClick={() => router.push('/newobj')}>Create data object</Button>
  } else {
    button = <Button marginRight={16} onClick={signIn}>Login</Button>
  }

  return(
    <nav>
      <Pane display="flex" width="100%" padding={8} background="redtint" borderRadius={3}>
        <Pane flex={1} alignItems="center" display="flex">
          <Link href="/" marginLeft={12} color={isActive('/') ? "neutral" : "blue"}>
              Home
          </Link>
          <Link href="/listdataobjects" marginLeft={12} color={isActive('/listdataobjects') ? "neutral" : "blue"}>
              Data Objects
          </Link>
          <Link href="/listfunctions" marginLeft={12} color={isActive('/listfunctions') ? "neutral" : "blue"}>
              Functions
          </Link>
          <Link href="/listusers" marginLeft={12} color={isActive('/listusers') ? "neutral" : "blue"}>
              Users
          </Link>
          <Link href="/searchpage" marginLeft={12} color={isActive('/searchpage') ? "neutral" : "blue"}>
              Search Page
          </Link>
        </Pane>
        <Pane>
          {/* Below you can see the marginRight property on a Button. */}
          {/*<Button marginRight={16} onClick={() => router.push('/signup')}>*/}
          {/* Login */}
          {/*</Button>*/}

          {button}
          {addObjButton}           
 
        </Pane>
      </Pane>

    </nav>
  )
}

export default Header
