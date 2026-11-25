"""Entrypoint for Railway deployments that target the main module."""

from app import app as app
from app import main


if __name__ == "__main__":
    main()
