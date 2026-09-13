import asyncio
import os

import openai
from dotenv import load_dotenv
from langfuse import observe
from openai import AsyncOpenAI

from backend.llmprompts import GENERATION_PROMPT, QUERY_REWRITE

load_dotenv()
llm_client=AsyncOpenAI(api_key=os.environ.get("GROQ_API_KEY"),
                       base_url="https://api.groq.com/openai/v1")
@observe
async def reqwritequery(query):
    """Used to rewrite query via llm"""
    try:
        response= await llm_client.chat.completions.create(
            model="meta-llama/llama-prompt-guard-2-22m",
            messages=[
                {"role": "system", "content": QUERY_REWRITE},
                {"role": "user", "content": f"User Query: {query}"} # type: ignore
        ],
            temperature=0.0,
            max_tokens=60
            )
        rewritten = response.choices[0].message.content.strip()
        rewritten=rewritten.strip('"\'')
        return rewritten if rewritten else query
    except (openai.OpenAIError, asyncio.TimeoutError) as e:
        print(f"Query rewriting failed ({e}), falling back to raw query.")
        return query
@observe
async def llm_answer(optim_query,chunks):
    try:
        formatted_chunks = ""
        for chunk in chunks:
            formatted_chunks += f"[ID: {chunk['id']}] (Score: {chunk['score']:.4f})\n{chunk['text']}\n\n"
        prompt_content = GENERATION_PROMPT.format(
            context_chunks=formatted_chunks,
            optimized_query=optim_query
        )
        generated_answer=await llm_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a precise technical documentation assistant."},
                {"role": "user", "content": prompt_content} # type: ignore   
            ],
            temperature=0.1,
            max_tokens=500
        )
        return generated_answer.choices[0].message.content.strip()
    except (openai.OpenAIError, asyncio.TimeoutError) as e:
        print(f"Answer generation failed ({e}), falling back to default message.")
        return "I apologize, but I am currently unable to generate a synthesized answer due to a model service error. Please review the retrieved context chunks directly."