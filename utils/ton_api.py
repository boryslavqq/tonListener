import asyncio

import aiohttp


class TonApi:
    """
    Ton Listener of transactions
    """

    def __init__(self, url, api_token: str = None):

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.host_url = url

        if api_token is not None:
            self.headers["X-API-KEY"] = api_token

    async def get_last_block(self) -> dict:
        """
        Get last masterchain block
        """

        return await self._do_request("/api/v2/getMasterchainInfo", "get")

    async def get_transactions_by_seqno(self, seqNo: str) -> dict:

        if not isinstance(seqNo, str):
            raise Exception("Param seqNo must be str")

        return await self._do_request("/api/index/getTransactionsByMasterchainSeqno?seqno=" + seqNo, "get")

    async def _do_request(self, api_method: str, method: str, body: dict = None) -> dict:
        """
        Internal method to do request to Ton jrpc
        """

        if "X-API-KEY" not in self.headers:
            raise Exception("You must authentificate first")

        await asyncio.sleep(1)

        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.host_url + api_method, json=body) as resp:
                return await resp.json()


