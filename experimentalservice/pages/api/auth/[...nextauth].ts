import NextAuth from 'next-auth'
import Providers from 'next-auth/providers'


const callbacks = {}

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
