---
type: email
source: gmail
message_id: 1993b82ae809a70e
from: Kazuhiro Sera <notifications@github.com>
subject: Re: [openai/openai-agents-python] Fix/consistent generic type handling (PR #1714)
received: Thu, 11 Sep 2025 18:20:43 -0700
category: general
priority: normal
status: pending
---

# Email: Re: [openai/openai-agents-python] Fix/consistent generic type handling (PR #1714)

## From
Kazuhiro Sera <notifications@github.com>

## Preview
seratch left a comment (openai/openai-agents-python#1714) I don&#39;t think this change is necessary. The following code works without any issues: import asyncio from pydantic import BaseModel from

## Full Content
seratch left a comment (openai/openai-agents-python#1714)

I don't think this change is necessary. The following code works without any issues:
```python
import asyncio
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, Runner, function_tool

class MyContext(BaseModel):
    foo: str

@function_tool
def get_weather(cxt: RunContextWrapper[MyContext], city: str) -> str:
    print(cxt.context.foo)
    return "Sunny with wind."

agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent. You must call the tools.",
    tools=[get_weather],
)

async def main():
    result = await Runner.run(
        agent, input="What's the weather in Tokyo?", context=MyContext(foo="FOO")
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-agents-python/pull/1714#issuecomment-3283272963
You are receiv

---

## Suggested Actions

- [ ] Read full email
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes

Add any notes here after processing.

---
*Created by Gmail Watcher*
