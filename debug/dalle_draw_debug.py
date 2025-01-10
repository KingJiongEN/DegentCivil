import asyncio
import functools
import os
import re
from openai import OpenAI
from typing import Union, Optional, Dict, List
import autogen
from autogen import ConversableAgent, Agent
import requests

config_list_dalle = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.bk",
    file_location="config",
    filter_dict={
        "model": ["dalle"],
    },
)

class DALLEAgent(ConversableAgent):
    def __init__(self, name, llm_config: dict, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)

        try:
            config_list = llm_config["config_list"]
            api_key = config_list[0]["api_key"]
            base_url = config_list[0]['base_url']
        except Exception as e:
            print("Unable to fetch API Key, because", e)
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key,base_url =base_url)
        self.register_reply([Agent, None], DALLEAgent.generate_dalle_reply)

    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        # override and always "silent" the send out message;
        # otherwise, the print log would be super long!
        super().send(message, recipient, request_reply, silent=True)

    def generate_dalle_reply(self, messages: Optional[List[Dict]], sender: "Agent", config):
        """Generate a reply using OpenAI DALLE call."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]

        prompt = messages[-1]["content"]
        # TODO: integrate with autogen.oai. For instance, with caching for the API call
        img_data = dalle_call(
            client=self.client,
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",  # TODO: the size should be flexible, deciding landscape, square, or portrait mode.
            quality="standard",
            n=1,
        )
        out_message = f"<img {img_data}>"
        return True, out_message
    
    async def a_generate_dalle_reply(self, messages: Optional[List[Dict]], sender: "Agent", config):
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self.generate_dalle_reply, messages=messages, sender=sender, config=config)
        )
    
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
        size (str): The size specification of the image. TODO: This should allow specifying landscape, square, or portrait modes.
        quality (str): The quality setting for the image generation.
        n (int): The number of images to generate.

    Returns:
    str: The image data as a string, either retrieved from the cache or newly generated.

    Note:
    - The cache is stored in a directory named '.cache/'.
    - The function uses a tuple of (model, prompt, size, quality, n) as the key for caching.
    - The image data is obtained by making a secondary request to the URL provided by the DALL-E API response.
    """
    # # Function implementation...
    # cache = Cache(".cache/")  # Create a cache directory
    # key = (model, prompt, size, quality, n)
    # if key in cache:
    #     return cache[key]
    
    # If not in cache, compute and store the result
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=n,
    )
    image_url = response.data[0].url
    # img_data = get_image_data(image_url)
    # cache[key] = img_data

    return image_url

async def main():
    dalle = DALLEAgent(name="Dalle", llm_config={"config_list": config_list_dalle})
    # message = await dalle.generate_dalle_reply([{'content': "hello world",'role': 'user'}], dalle, config=None)
    _, message = await dalle.a_generate_dalle_reply([{'content': "hello world",'role': 'user'}], dalle, config=None)

    print(message)

if __name__ == '__main__':
    # dalle = DALLEAgent(name="Dalle", llm_config={"config_list": config_list_dalle})
    # response = dalle.client.images.generate(
    #     model="dall-e-3",
    #     prompt="A vibrant cityscape at dusk, with the setting sun casting a warm glow over the buildings. The streets are alive with people, indicating a sense of community and joy. The art style leans towards impressionism, capturing the fleeting beauty of the moment rather than intricate details. This piece aims to evoke feelings of warmth, belonging, and the serene joy of everyday life.",
    #     size="1024x1024",
    #     quality="standard",
    #     n=1,
    #     )
    # image_url = response.data[0].url
    # print(image_url)
    
    asyncio.run(main())
    # dalle.generate_dalle_reply([{'content': "A vibrant cityscape at dusk, with the setting sun casting a warm glow over the buildings. The streets are alive with people, indicating a sense of community and joy. The art style leans towards impressionism, capturing the fleeting beauty of the moment rather than intricate details. This piece aims to evoke feelings of warmth, belonging, and the serene joy of everyday life.",'role': 'user'}], dalle, config=None) 