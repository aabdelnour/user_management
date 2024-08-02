import pytest
from uuid import uuid4
from datetime import datetime, timezone
from app.services.user_service import UserService
from app.models.user_model import User, UserRole

@pytest.mark.asyncio
async def test_update_professional_status(async_session):
    # Create a test user
    user = User(
        id=uuid4(),
        email="test@example.com",
        nickname="testuser",
        hashed_password="hashed_password",
        role=UserRole.AUTHENTICATED,
        is_professional=False
    )
    async_session.add(user)
    await async_session.commit()

    # Update professional status
    updated_user = await UserService.update_professional_status(async_session, user.id, True)

    # Assert the update was successful
    assert updated_user is not None
    assert updated_user.is_professional is True
    assert updated_user.professional_status_updated_at is not None
    assert (datetime.now(timezone.utc) - updated_user.professional_status_updated_at).total_seconds() < 5

    # Fetch the user from the database to ensure changes were persisted
    await async_session.refresh(updated_user)
    fetched_user = await UserService.get_by_id(async_session, user.id)
    assert fetched_user.is_professional is True

    # Try to update a non-existent user
    non_existent_user = await UserService.update_professional_status(async_session, uuid4(), True)
    assert non_existent_user is None

@pytest.mark.asyncio
async def test_update_professional_status_toggle(async_session):
    # Create a test user
    user = User(
        id=uuid4(),
        email="test_toggle@example.com",
        nickname="testtoggle",
        hashed_password="hashed_password",
        role=UserRole.AUTHENTICATED,
        is_professional=False
    )
    async_session.add(user)
    await async_session.commit()

    # Update professional status to True
    updated_user = await UserService.update_professional_status(async_session, user.id, True)
    assert updated_user.is_professional is True

    # Update professional status back to False
    updated_user = await UserService.update_professional_status(async_session, user.id, False)
    assert updated_user.is_professional is False

    # Verify the changes in the database
    await async_session.refresh(updated_user)
    fetched_user = await UserService.get_by_id(async_session, user.id)
    assert fetched_user.is_professional is False