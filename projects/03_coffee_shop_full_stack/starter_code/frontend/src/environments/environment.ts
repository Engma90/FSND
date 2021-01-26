/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'auth-server477.us', // the auth0 domain prefix
    audience: 'dev', // the audience set for the auth0 app
    clientId: 'D6b3pv9fTlno8pNZvltSG8hyzDujX2re', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application. 
  }
};
