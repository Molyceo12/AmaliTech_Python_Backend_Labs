"""Tests for the custom ``User`` model and its admin."""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client

from accounts.models import User


def _user(email: str = "ana@example.com", **fields: object) -> User:
    """Save a user with a username derived from the email."""
    return User.objects.create_user(
        email=email, username=email.split("@")[0], password=None, **fields
    )


def test_project_uses_the_custom_user() -> None:
    """``AUTH_USER_MODEL`` points Django at ``accounts.User``."""
    assert get_user_model() is User


@pytest.mark.django_db
def test_new_user_is_free_and_not_premium() -> None:
    """Defaults: tier ``free``, ``is_premium`` False."""
    user = _user()
    assert (user.tier, user.is_premium) == (User.Tier.FREE, False)


@pytest.mark.django_db
def test_email_is_saved_lowercase_and_unique() -> None:
    """``Ana@Example.com`` is saved lowercase, so the same email can't come back."""
    assert _user("Ana@Example.com").email == "ana@example.com"
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="ANA@example.com", username="other")


@pytest.mark.django_db
def test_is_premium_follows_the_tier() -> None:
    """``premium`` turns ``is_premium`` on; back to ``free`` turns it off."""
    user = _user(tier=User.Tier.PREMIUM)
    assert user.is_premium is True
    user.tier = User.Tier.FREE
    user.save()
    assert user.is_premium is False


@pytest.mark.django_db
def test_admin_tier_gives_no_admin_rights() -> None:
    """``tier=admin`` is a business tier; ``is_staff`` stays False."""
    user = _user(tier=User.Tier.ADMIN)
    assert (user.is_staff, user.is_superuser, user.is_premium) == (False, False, False)


@pytest.mark.django_db
def test_superuser_logs_in_with_email(client: Client) -> None:
    """A superuser made with an email logs in with that email."""
    User.objects.create_superuser(
        email="boss@example.com", username="boss", password="test-only-pass"
    )
    assert client.login(email="boss@example.com", password="test-only-pass")
