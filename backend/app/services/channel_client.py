import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..config import settings

logger = logging.getLogger(__name__)


class ChannelClient:
    def __init__(self):
        self.base_url = settings.CHANNEL_SERVICE_URL
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def send_message(
        self,
        campaign_id: int,
        customer_id: int,
        channel: str,
        message: str,
        phone: str | None = None,
        email: str | None = None,
        subject: str | None = None,
    ) -> dict:
        payload = {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "channel": channel,
            "message": message,
            "phone": phone,
            "email": email,
            "subject": subject,
        }
        response = await self.client.post(f"{self.base_url}/send", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


channel_client = ChannelClient()
