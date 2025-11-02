from http import HTTPStatus

from freezegun import freeze_time

from fast_zero.security import create_access_token


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exist(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired_after_time(client, user):
    with freeze_time('2025-11-1 20:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password}
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-11-1 20:32:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            }
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_inexistent_user(client):
    """Tries to login with a nonexistent user"""
    response = client.post(
        '/auth/token',
        data={'username': 'no_user@no_domain.com', 'password': 'testtest'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client, user, token):
    """Tries to refresh the token at refresh_token endpoint"""
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    """Checks if the token is truly expired"""
    with freeze_time('2025-11-02 20:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password}
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-11-02 20:32:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
