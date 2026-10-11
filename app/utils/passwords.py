import logging

from werkzeug.security import check_password_hash


logger = logging.getLogger(__name__)


def verify_password(password_hash, password):
    """Verify a password without allowing a malformed stored hash to crash login."""
    if not isinstance(password_hash, str) or not password_hash.strip():
        logger.warning('Password verification skipped because the stored hash is empty.')
        return False

    try:
        return check_password_hash(password_hash, password)
    except (TypeError, ValueError):
        logger.warning('Password verification failed because the stored hash is invalid.')
        return False
