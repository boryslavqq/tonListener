import asyncio
from base64 import b64encode

import aiohttp
from tonsdk.contract.wallet import WalletVersionEnum, WalletV2ContractR1, WalletV2ContractR2, WalletV3ContractR1, \
    WalletV3ContractR2, WalletV4ContractR1, WalletV4ContractR2, HighloadWalletV2Contract, WalletContract


class TonApi:
    """
    Ton Listener of transactions
    """

    default_version = WalletVersionEnum.v3r2
    ALL = {
        WalletVersionEnum.v2r1: WalletV2ContractR1,
        WalletVersionEnum.v2r2: WalletV2ContractR2,
        WalletVersionEnum.v3r1: WalletV3ContractR1,
        WalletVersionEnum.v3r2: WalletV3ContractR2,
        WalletVersionEnum.v4r1: WalletV4ContractR1,
        WalletVersionEnum.v4r2: WalletV4ContractR2,
        WalletVersionEnum.hv2: HighloadWalletV2Contract
    }

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

    async def get_wallet_by_keys(self, pub_key: str, priv_key: str, version: WalletVersionEnum, workchain: int = 0,
                                 **kwargs) -> WalletContract:

        """
        Get wallet using pub_key and private key
        """

        wallet = self.ALL[version](
            public_key=pub_key, private_key=priv_key, wc=workchain, **kwargs)

        return wallet

    async def get_wallet_info(self, addr: str):
        return await self._do_request(
            '/api/v2/getWalletInformation?address=' + addr,
            "get",
        )

    async def send_boc(self, src: bytes):
        return await self._do_request(
            "/api/v2/sendBoc",
            'post',
            body={
                'boc': b64encode(src).decode(),
            }
        )

    async def get_seqno(self, addr: str):
        try:
            res = await self.get_wallet_info(addr)
            if res['account_state'] == 'uninitialized':
                return 0

            return res.get('seqno', 0)
        except KeyError:
            return 0

    async def send_tons(self, wallet, dest: str, amount: int, payload=None):
        seqno = await self.get_seqno(wallet.address.to_string(1, 1, 1))

        query = wallet.create_transfer_message(
            dest, amount, seqno, payload=payload
        )
        return await self.send_boc(query['message'].to_boc(False))
