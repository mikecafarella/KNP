import NextAuth from 'next-auth'
import Providers from 'next-auth/providers'


const callbacks = {}

callbacks.signIn = async function signIn(user, account, metadata) {
  if (account.provider === 'okta') {
    const oktaUser = {
      id: user.id,
      email: user.email,
      name: user.name
    }

    const res = await fetch(`http://localhost:5000/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(oktaUser),
    })
    const data = await res.json()
    user.accessToken = data.id
    return true;
  }
  return false
}


callbacks.jwt = async function jwt(token, user) {
  if (user) {
    token = { accessToken: user.accessToken, userinfo: user }
  }
  return token
}

callbacks.session = async function session(session, token) {
  session.userid = token.accessToken
  session.user = token.userinfo
  return session
}


const options = {
  // Configure one or more authentication providers
  providers: [
    Providers.Okta({
      clientId: process.env.OKTA_CLIENTID,
      clientSecret: process.env.OKTA_CLIENTSECRET,
      domain: process.env.OKTA_DOMAIN
    })
  ],
  callbacks
}

export default (req, res) => NextAuth(req, res, options)
