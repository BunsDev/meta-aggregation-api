import ssl

import aiohttp
from aiohttp import ClientResponseError
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT
from starlette.requests import Request

from meta_aggregation_api.rest_api import dependencies
from meta_aggregation_api.rest_api.dependencies import aiohttp_session
from meta_aggregation_api.utils.common import get_web3_url
from meta_aggregation_api.utils.logger import get_logger

v1_rpc = APIRouter()
logger = get_logger(__name__)


@v1_rpc.post('/rpc/{chain_id}', dependencies=[Depends(HTTPBearer())])
async def send_rpc(
    request: Request,
    authorize: AuthJWT = Depends(),
    chain_id: int = Path(..., description="Chain ID"),
    session: aiohttp.ClientSession = Depends(aiohttp_session),
    config: dependencies.Config = Depends(dependencies.config),
):
    """
    The send_rpc function is an endpoint that makes an HTTP request to the node
    that is currently synced with the most other nodes. It takes in a JSON-RPC 2.0 compliant
    request and returns a JSON-RPC 2.0 compliant response.
    """
    authorize.jwt_required()
    node = get_web3_url(chain_id, config)
    try:
        async with session.post(
            node, proxy=None, json=await request.json(), ssl=ssl.SSLContext()
        ) as response:
            return await response.json()
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
