# -*- coding: utf-8 -*-
__author__ = 'ninad'

from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect
import simplejson as json

# from web.instance.default import OAUTH
# from .providers import FacebookSignIn as facebook

from requests.exceptions import ConnectionError
import contextlib
from functools import wraps
import pdb


# TODO: Add parameters to exception list by providing parameters to decorator
def silence_exception(f):
    @wraps(f)
    def inner(*args, **kwargs):
        with contextlib.suppress(ConnectionError):
            return f(*args, **kwargs)

    return inner


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        conf = current_app.config['OAUTH'][provider_name.upper()]
        urls = conf['urls']

        self.consumer_id = conf['id']
        self.consumer_secret = conf['secret']
        self.authorize_url = urls['authorize']
        self.base_url = urls['base']
        self.access_token_url = urls['token']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('auth.oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('facebook')

        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        me = oauth_session.get('me?fields=id,email,first_name,last_name').json()

        """
        {   'email': 'n.mhatre@hotmail.com',
            'first_name': 'Ninad',
            'id': '10154024652361834',
            'last_name': 'Mhatre'}
        """
        # import pprint
        # pprint.pprint(me, indent=4)
        return (
            'facebook$' + me['id'],
            (me['first_name'], me['last_name']),
            me['email'],
            me
        )


class GithubSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('github')
        self.service = OAuth2Service(
            name='github',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='user:email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        me = oauth_session.get('user').json()
        # import pprint
        # pprint.pprint(me, indent=4)

        """ information got from github
        'avatar_url': 'https://avatars.githubusercontent.com/u/2124949?v=3',
        'bio': None,
        'blog': 'https://www.ninadmhatre.com',
        'company': None,
        'created_at': '2012-08-09T18:03:37Z',
        'email': 'ninad.mhatre@gmail.com',
        'events_url': 'https://api.github.com/users/ninadmhatre/events{/privacy}',
        'followers': 1,
        'followers_url': 'https://api.github.com/users/ninadmhatre/followers',
        'following': 2,
        'following_url': 'https://api.github.com/users/ninadmhatre/following{/other_user}',
        'gists_url': 'https://api.github.com/users/ninadmhatre/gists{/gist_id}',
        'gravatar_id': '',
        'hireable': True,
        'html_url': 'https://github.com/ninadmhatre',
        'id': 2124949,
        'location': 'Mumbai, India',
        'login': 'ninadmhatre',
        'name': 'Ninad Mhatre',
        'organizations_url': 'https://api.github.com/users/ninadmhatre/orgs',
        'public_gists': 0,
        'public_repos': 8,
        'received_events_url': 'https://api.github.com/users/ninadmhatre/received_events',
        'repos_url': 'https://api.github.com/users/ninadmhatre/repos',
        'site_admin': False,
        'starred_url': 'https://api.github.com/users/ninadmhatre/starred{/owner}{/repo}',
        'subscriptions_url': 'https://api.github.com/users/ninadmhatre/subscriptions',
        'type': 'User',
        'updated_at': '2016-12-14T02:33:48Z',
        'url': 'https://api.github.com/users/ninadmhatre'}

        """
        return (
            'github$%d' % me['id'],
            me['name'].split(' '),
            me['email'],
            me
        )


class AzureSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('azure')
        self.service = OAuth2Service(
            name='azure',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='User.Read',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        me = oauth_session.get('v1.0/me').json()
        # import pprint
        # pprint.pprint(me, indent=4)

        """ information got from azure
        {   '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users/$entity',
            'businessPhones': [],
            'displayName': 'ninad mhatre',
            'givenName': 'ninad',
            'id': '99e469de0693e0e8',
            'jobTitle': None,
            'mail': None,
            'mobilePhone': None,
            'officeLocation': None,
            'preferredLanguage': None,
            'surname': 'mhatre',
            'userPrincipalName': 'ninad.mhatre@outlook.com'}
        """
        return (
            'azure$%s' % me['id'],
            (me['givenName'], me['surname']),
            me['userPrincipalName'],
            me
        )


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='profile email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        # me = oauth_session.get('v1/userinfo').json()
        me = oauth_session.get('plus/v1/people/me').json()

        # import pprint
        # pprint.pprint(me, indent=4)

        """ information got from google
    {   'circledByCount': 119,
        'cover': {   'coverInfo': {'leftImageOffset': 0, 'topImageOffset': 0},
                     'coverPhoto': {   'height': 705,
                                       'url': 'https://lh3.googleusercontent.com/3CVEjMO1hZavxmCev7tCC5b2TO6EnPPbctSxqutdJ7AqYJykQJUOxR2kR2DYtqUKD3UR7_Itbg=s630-fcrop64=1,00003ecaffffffff',
                                       'width': 940},
                     'layout': 'banner'},
        'displayName': 'Ninad Mhatre',
        'emails': [{'type': 'account', 'value': 'ninad.mhatre@gmail.com'}],
        'etag': '"FT7X6cYw9BSnPtIywEFNNGVVdio/Wvo2HkBp1vXZxz3KPP23NWodfnU"',
        'gender': 'male',
        'id': '100200154771991934741',
        'image': {   'isDefault': False,
                     'url': 'https://lh4.googleusercontent.com/-pfYzneaTJUk/AAAAAAAAAAI/AAAAAAAAlPQ/pClXN6t0T40/photo.jpg?sz=50'},
        'isPlusUser': True,
        'kind': 'plus#person',
        'language': 'en',
        'name': {'familyName': 'Mhatre', 'givenName': 'Ninad'},
        'objectType': 'person',
        'occupation': 'Software Developer',
        'organizations': [   {   'endDate': '2006',
                                 'name': 'University of mumbai',
                                 'primary': False,
                                 'startDate': '2003',
                                 'title': 'Electronics & Telecom',
                                 'type': 'school'}],
        'placesLived': [{'primary': True, 'value': 'Mumbai'}],
        'skills': 'Perl, Python, C#, Bash, Unix/Linux',
        'tagline': 'Whatever happens, happens for a reason',
        'url': 'https://plus.google.com/+ninadmhatre',
        'urls': [   {   'label': 'Blogger (Blogspot) - unix-systems-basic',
                        'type': 'otherProfile',
                        'value': 'http://unix-systems-basic.blogspot.com/'},
                    {   'label': 'Picasa Web Albums',
                        'type': 'otherProfile',
                        'value': 'http://picasaweb.google.com/ninad.mhatre'}],
        'verified': False}
        """
        return (
            'google$%s' % me['id'],
            (me['name']['givenName'], me['name']['familyName']),
            me['emails'][0]['value'],
            me
        )


class LinkedinSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('linkedin')
        self.service = OAuth2Service(
            name='linkedin',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            # scope='r_emailaddress',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    @silence_exception
    def callback(self):
        if 'code' not in request.args:
            return None, None, None

        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        # pdb.set_trace()
        me = oauth_session.get('v1/people/~:(id,first-name,last-name,maiden-name,email-address)?format=json').json()
        # import pprint
        # pprint.pprint(me, indent=4)

        """ information got from linkedin
        'firstName': 'Ninad',
        'headline': 'Software Developer',
        'id': '4Cv8toPQvT',
        'lastName': 'Mhatre',
        """
        return (
            'linkedin$%s' % me['id'],
            (me['firstName'], me['lastName']),
            me['emailAddress'],
            me
        )
