import json
import logging
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..config import settings

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_campaign_plan(self, business_goal: str) -> dict:
        system_prompt = """You are an expert marketing campaign planner for a retail/e-commerce platform.
Convert business goals into structured campaign plans.
You MUST respond with valid JSON only. No markdown, no explanations outside JSON.

Available customer profile fields for filtering:
- total_orders (integer)
- total_spend (decimal)
- average_order_value (decimal)
- days_since_last_purchase (integer)
- purchase_frequency (decimal)
- customer_segment (string: vip, dormant, frequent, new, at_risk, regular)
- city (string, on customers table)

Available channels: whatsapp, sms, email, rcs

Generate a campaign plan. Respond in this EXACT JSON structure:
{
  "audience_name": "string - descriptive name",
  "filters": [{"field": "string", "operator": ">|<|>=|<=|=|!=", "value": number_or_string}],
  "channel": "whatsapp|sms|email|rcs",
  "strategy": "string - brief description of marketing approach",
  "reasoning": "string - why this plan matches the business goal"
}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Business Goal: {business_goal}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        result = json.loads(content)
        logger.info(f"Groq campaign plan generated for goal: {business_goal[:50]}")
        return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_message(self, channel: str, strategy: str, audience_name: str) -> dict:
        system_prompt = """You are a marketing copywriter expert. Generate personalized marketing messages.
You MUST respond with valid JSON only. No markdown, no explanations outside JSON.

Use these exact placeholder tokens in the message:
- {name} for customer name
- {days_since_last_purchase} for days since their last purchase
- {city} for customer city

Respond in this EXACT JSON structure:
{
  "message": "string - the marketing message with placeholders",
  "subject": "string - email subject line (always include even for non-email channels, set to empty string if not applicable)"
}"""

        user_prompt = f"""Generate a personalized marketing message for:
- Channel: {channel}
- Strategy: {strategy}
- Target Audience: {audience_name}

Requirements:
- Use placeholder {{name}} for customer name
- Use placeholder {{days_since_last_purchase}} for inactivity reference (only if relevant)
- Use placeholder {{city}} for geographic personalization (only if relevant)
- Include the offer/strategy clearly
- Add a clear call-to-action
- Tone should match the channel (professional for email, concise for SMS/WhatsApp)
- For SMS/WhatsApp: keep under 160 characters if possible
- For email: can be longer with proper greeting"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=800,
        )

        content = response.choices[0].message.content
        result = json.loads(content)
        logger.info(f"Groq message generated for channel: {channel}, audience: {audience_name[:30]}")
        return result


groq_service = GroqService()
