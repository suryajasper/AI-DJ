from typing import Union
from pydantic import BaseModel
from openai import OpenAI
from .utils import retrieve_key

class GPT:
    def __init__(self, model_id='gpt-4o-mini'):
        self.model_id = model_id
        self.client = OpenAI(api_key=retrieve_key('gpt'))
    
    def request(self, role : str, prompt : str, output_schema: BaseModel = None) -> Union[str, dict]:
        response_format = output_schema if output_schema else {"type": "text"}

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt},
            ],
            temperature=1,
            max_tokens=10000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format=response_format
        )

        if output_schema:
            return dict(response.choices[0].message.parsed)
        else:
            return response.choices[0].message.content