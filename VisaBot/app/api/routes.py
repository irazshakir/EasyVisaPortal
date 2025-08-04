"""
Main API router
"""
from fastapi import APIRouter

from app.api.v1 import api_router

# Use the v1 API router
api_router = api_router 