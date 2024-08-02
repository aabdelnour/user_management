import pytest
from httpx import AsyncClient
from app.models.user_model import User, UserRole
from uuid import uuid4
from app.services.jwt_service import create_access_token
from app.dependencies import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_update_professional_status_api(async_client: AsyncClient, async_session):
    # Create a test user
    user = User(
        id=uuid4(),
        email="testuser@example.com",
        nickname="testuser",
        hashed_password="hashed_password",
        role=UserRole.AUTHENTICATED,
        is_professional=False
    )
    async_session.add(user)
    await async_session.commit()

    # Create an admin user
    admin_user = User(
        id=uuid4(),
        email="admin@example.com",
        nickname="adminuser",
        hashed_password="hashed_password",
        role=UserRole.ADMIN,
        is_professional=False
    )
    async_session.add(admin_user)
    await async_session.commit()

    # Generate admin token
    admin_token = create_access_token(data={"sub": str(admin_user.id), "role": UserRole.ADMIN.value})

    # Update professional status
    response = await async_client.patch(
        f"/users/{user.id}/professional-status",
        params={"is_professional": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Print response content if the status code is not 200
    if response.status_code != 200:
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.content}"
    data = response.json()
    assert data["is_professional"] is True

    # Generate non-admin token
    non_admin_token = create_access_token(data={"sub": str(user.id), "role": UserRole.AUTHENTICATED.value})

    # Try to update with non-admin token
    response = await async_client.patch(
        f"/users/{user.id}/professional-status",
        params={"is_professional": False},
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )

    assert response.status_code == 403, f"Expected 403, got {response.status_code}. Response: {response.content}"  # Forbidden

    # Try to update non-existent user
    non_existent_user_id = uuid4()
    response = await async_client.patch(
        f"/users/{non_existent_user_id}/professional-status",
        params={"is_professional": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.content}"  # Not Found

@pytest.mark.asyncio
async def test_update_professional_status_api_validation(async_client: AsyncClient, async_session):
    # Create an admin user
    admin_user = User(
        id=uuid4(),
        email="admin2@example.com",
        nickname="adminuser2",
        hashed_password="hashed_password",
        role=UserRole.ADMIN,
        is_professional=False
    )
    async_session.add(admin_user)
    await async_session.commit()

    # Generate admin token
    admin_token = create_access_token(data={"sub": str(admin_user.id), "role": UserRole.ADMIN.value})

    # Create a test user
    user = User(
        id=uuid4(),
        email="testuser2@example.com",
        nickname="testuser2",
        hashed_password="hashed_password",
        role=UserRole.AUTHENTICATED,
        is_professional=False
    )
    async_session.add(user)
    await async_session.commit()

    # Test with invalid data type
    response = await async_client.patch(
        f"/users/{user.id}/professional-status",
        params={"is_professional": "not a boolean"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}. Response: {response.content}"  # Unprocessable Entity

    # Test with missing data
    response = await async_client.patch(
        f"/users/{user.id}/professional-status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}. Response: {response.content}"  # Unprocessable Entity