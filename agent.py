from pydantic_ai import Agent, RunContext
import os
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider 
from dataclasses import dataclass
from pydantic import BaseModel, Field
import asyncio 
import logfire

logfire.configure()  
logfire.instrument_asyncpg() 

model = OpenAIModel(
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    provider=OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key='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'
    ),
)

@dataclass
class SupportDeps:
    customer_id: int
    #connect to an external database (e.g. PostgreSQL) to get information.
    #db: DatabaseConn

class SupportResult(BaseModel):  
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description="Whether to block the customer's card")
    risk: int = Field(description='Risk level of query', ge=0, le=10)

support_agent = Agent(  
    model,  
    deps_type=SupportDeps,
    result_type=SupportResult,  
    system_prompt=(  
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query.'
    ),
     instrument=True,
)

@support_agent.system_prompt  
async def add_customer_name(ctx: RunContext[SupportDeps]) -> str:
    customer_name = "liam"
    return f"The customer's name is {customer_name!r}"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDeps]
) -> float:
    """Returns a hardcoded customer account balance."""
    # Return a fixed balance value
    return 100.0
    

async def main():
    print("Running...")
    deps = SupportDeps(customer_id=123)
    result = await support_agent.run('waht is my balance?', deps=deps)  
    print(result.data)  
    """
    support_advice='Hello John, your current account balance, including pending transactions, is $123.45.' block_card=False risk=1
    """


if __name__ == "__main__":
    asyncio.run(main())