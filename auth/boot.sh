#!/bin/sh

alembic upgrade head
watchmedo auto-restart --recursive --pattern="*.py" --directory="${DEFAULT_SERVICE_DIR}" python -- -m main
