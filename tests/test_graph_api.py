"""Tests for the ``graph_api`` module."""

import random
import json
from mock import patch, call, Mock as mock
from nose.tools import *

from facepy import GraphAPI

patch = patch('requests.session')

def mock():
    global mock_request

    mock_request = patch.start()().request

def unmock():
    patch.stop()

@with_setup(mock, unmock)
def test_get():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'id': 1,
        'name': 'Thomas \'Herc\' Hauk',
        'first_name': 'Thomas',
        'last_name': 'Hauk',
        'link': 'http://facebook.com/herc',
        'username': 'herc',
    })

    graph.get('me')

    mock_request.assert_called_with('GET', 'https://graph.facebook.com/me',
        allow_redirects = True,
        params = {
          'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_get_with_fields():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'id': 1,
        'first_name': 'Thomas',
        'last_name': 'Hauk'
    })

    graph.get('me', fields=['id', 'first_name', 'last_name'])

    mock_request.assert_called_with('GET', 'https://graph.facebook.com/me',
        allow_redirects = True,
        params = {
            'access_token': '<access token>',
            'fields': 'id,first_name,last_name'
        }
    )

@with_setup(mock, unmock)
def test_forbidden_get():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = 'false'

    assert_raises(GraphAPI.FacebookError, graph.get, 'me')

@with_setup(mock, unmock)
def test_paged_get():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'data': [
            {
                'message': 'He\'s a complicated man. And the only one that understands him is his woman'
            }
        ] * 100,
        'paging': {
            'next': '...'
        }
    })

    pages = graph.get('herc/posts', page=True)

    for index, page in enumerate(pages):
        break

    mock_request.assert_called_with('GET', 'https://graph.facebook.com/herc/posts',
        allow_redirects = True,
        params = {
            'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_get_with_errors():
    graph = GraphAPI('<access token>')

    # Test errors
    mock_request.return_value.content = json.dumps({
        'error': {
            'code': 1,
            'message': 'An unknown error occurred'
        }
    })

    assert_raises(GraphAPI.FacebookError, graph.get, 'me')

    # Test legacy errors
    mock_request.return_value.content = json.dumps({
        'error_code': 1,
        'error_msg': 'An unknown error occurred',
    })

    assert_raises(GraphAPI.FacebookError, graph.get, 'me')

    # Test legacy errors without an error code
    mock_request.return_value.content = json.dumps({
        'error_msg': 'The action you\'re trying to publish is invalid'
    })

    assert_raises(GraphAPI.FacebookError, graph.get, 'me')

@with_setup(mock, unmock)
def test_get_with_retries():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'error': {
            'message': 'An unknown error occurred.',
            'code': 500
        }
    })

    try:
        graph.get('me', retry=3)
    except GraphAPI.FacebookError:
        pass

    assert mock_request.call_args_list == [
        call('GET', 'https://graph.facebook.com/me',
            allow_redirects = True, params = {
                'access_token': '<access token>'
            }
        )
    ] * 3


@with_setup(mock, unmock)
def test_fql():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'id': 1,
        'name': 'Thomas \'Herc\' Hauk',
        'first_name': 'Thomas',
        'last_name': 'Hauk',
        'link': 'http://facebook.com/herc',
        'username': 'herc',
    })

    try:
        graph.fql('SELECT id,name,first_name,last_name,username FROM user WHERE uid=me()')
    except GraphAPI.FacebookError:
        pass

    mock_request.assert_called_with('GET', 'https://graph.facebook.com/fql?q=SELECT+id%2Cname%2Cfirst_name%2Clast_name%2Cusername+FROM+user+WHERE+uid%3Dme%28%29',
        allow_redirects = True,
        params = {
            'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_post():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'id': 1
    })

    graph.post(
        path = 'me/feed',
        message = 'He\'s a complicated man. And the only one that understands him is his woman'
    )

    mock_request.assert_called_with('POST', 'https://graph.facebook.com/me/feed',
        files = {},
        data = {
            'message': 'He\'s a complicated man. And the only one that understands him is his woman',
            'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_forbidden_post():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = 'false'

    assert_raises(GraphAPI.FacebookError, graph.post, 'me')

@with_setup(mock, unmock)
def test_delete():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = 'true'

    graph.delete(1)

    mock_request.assert_called_with('DELETE', 'https://graph.facebook.com/1',
        allow_redirects = True,
        params = {
            'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_search():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps({
        'data': [
            {
                'message': 'I don\'t like your chair.'
            },
            {
                'message': 'Don\'t let your mouth get your ass in trouble.'
            }
        ]
    })

    graph.search(
        term = 'shaft quotes',
        type = 'post'
    )

    mock_request.assert_called_with('GET', 'https://graph.facebook.com/search',
        allow_redirects = True,
        params = {
            'q': 'shaft quotes',
            'type': 'post',
            'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_batch():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps([
        {
            'code': 200,
            'headers': [
                { 'name': 'Content-Type', 'value': 'text/javascript; charset=UTF-8' }
            ],
            'body': '{"foo": "bar"}'
        }
    ])

    requests = [
        { 'method': 'GET', 'relative_url': 'me/friends' },
        { 'method': 'GET', 'relative_url': 'me/photos' }
    ]

    batch = graph.batch(
        requests = requests
    )

    for item in batch:
        pass

    mock_request.assert_called_with('POST', 'https://graph.facebook.com/',
        files = {},
        data = {
            'batch': json.dumps(requests),
            'access_token': '<access token>'
        }
    )

@with_setup(mock, unmock)
def test_batch_with_errors():
    graph = GraphAPI('<access token>')

    mock_request.return_value.content = json.dumps([
        {
            'code': 500,
            'headers': [
                { 'name': 'Content-Type', 'value': 'text/javascript; charset=UTF-8' }
            ],
            'body': '{"error_code": 1, "error_msg": "An unknown error occurred"}'
        }
    ])

    requests = [{ 'method': 'GET', 'relative_url': 'me' }]

    batch = graph.batch(requests)

    for item in batch:
        assert isinstance(item, Exception)
        assert_equal(requests[0], item.request)
