import asyncio
import functools
import uuid
from autogen import ConversableAgent, Agent
import os
from typing import Union, Optional
import re

from diskcache import Cache
from openai import OpenAI
from .drawing import Drawing, DrawingList
from typing import Dict, List, Literal
from ..llm.llm_expends.dalle3 import DALLE3Caller



class DALLEAgent(ConversableAgent):
    def __init__(self, name, owner: "Character", llm_config: dict, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)

        try:
            config_list = llm_config["config_list"]
            for cfg in config_list:
                if 'api_key' in cfg and 'base_url' in cfg :
                    api_key = cfg["api_key"]
                    base_url = cfg['base_url']
                    break
        except Exception as e:
            api_key = os.getenv("OPENAI_API_KEY")
        self.api_key = api_key
        self.owner = owner
        self.client = OpenAI(api_key=api_key,base_url =base_url)
        self.register_reply([Agent, None], DALLEAgent.generate_dalle_reply)
        self.register_reply([Agent, None], DALLEAgent.a_generate_dalle_reply)
        
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = True,
    ):
        # override and always "silent" the send out message;
        # otherwise, the print log would be super long!
        super().send(message, recipient, request_reply, silent=silent)

    def generate_dalle_reply(self, messages: Optional[List[Dict]], sender: Agent, config):
        """
        Generate a reply using OpenAI DALLE call.
        Add artwork to the DrawingList of the owner happens in __init__ of drawing
        """
        if messages is None:
            messages = self._oai_messages[sender]

        prompt = messages[-1]["content"]
        drawing = self.draw(prompt, api_key=self.api_key)
        out_message = {'img_url': drawing.image_url,
                       'img_id': drawing.id}
        return True, out_message
    
    async def a_generate_dalle_reply(self,messages: Optional[List[Dict]], sender: Agent, config):
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self.generate_dalle_reply, messages=messages, sender=sender, config=config)
        )
        
    async def a_process_then_reply(self, message, sender: Agent, restart=True, silent=True):
    # modified from ConversableAgent.a_receive()
        self._prepare_chat(self,clear_history=restart)
        self._process_received_message(message, sender, silent)
        reply = await self.a_generate_reply(sender=sender)
        return reply
    
    def draw(self, prompt: str, api_key:str=None) -> 'Drawing':
        # caller = DALLE3Caller(api_key=api_key)
        # llm_task = asyncio.create_task(caller.ask(prompt))
        # image_url = await llm_task
        image_url = dalle_call(client=self.client,
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024", 
            quality="standard",
            n=1,
        )
        _id = str(uuid.uuid4())
        print(f"Drawing id: {_id}")
        
        try:
            return Drawing(image_url= image_url, id= _id, description= prompt, owner= self.owner)
        except Exception as e:
            print(f"Error creating Drawing: {e}")
            return self.draw(prompt, api_key) 
    
    
    def sanity_check(self, id, image_url, description) -> bool:
        assert type(id) == str,f' the type of id should be str, your type of {self.id} is {type(self.id)}  '
        assert type(image_url) == str and image_url.startswith('http'),f' the type of image_url should be str and start with http, your type of url is {type(image_url)}, and url is {image_url[:10]}  ' 
        assert type(description) == str,f' the type of description should be str, your type of {self.description} is {type(self.description)}  '
         
         
         
def dalle_call(client: OpenAI, model: str, prompt: str, size: str, quality: str, n: int) -> str:
    """
    Generate an image using OpenAI's DALL-E model and cache the result.

    This function takes a prompt and other parameters to generate an image using OpenAI's DALL-E model.
    It checks if the result is already cached; if so, it returns the cached image data. Otherwise,
    it calls the DALL-E API to generate the image, stores the result in the cache, and then returns it.

    Args:
        client (OpenAI): The OpenAI client instance for making API calls.
        model (str): The specific DALL-E model to use for image generation.
        prompt (str): The text prompt based on which the image is generated.
        size (str): The size specification of the image. 
        quality (str): The quality setting for the image generation.
        n (int): The number of images to generate.

    Returns:
    str: The image data as a string, either retrieved from the cache or newly generated.

    Note:
    - The cache is stored in a directory named '.cache/'.
    - The function uses a tuple of (model, prompt, size, quality, n) as the key for caching.
    - The image data is obtained by making a secondary request to the URL provided by the DALL-E API response.
    """
    # Function implementation...
    cache = Cache(".cache/")  # Create a cache directory
    key = (model, prompt, size, quality, n)
    if key in cache:
        return cache[key]
    
    # If not in cache, compute and store the result
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=n,
    )
    image_url = response.data[0].url
    cache[key] = image_url
    
    return image_url