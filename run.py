import asyncio

import httpx
import requests
import numpy as np
from PIL import Image

async def main():

    filename = 'DJI_20240729120840_0001_T_point0.JPG'

    with Image.open(filename) as image:
        width, height = image.size

    with open(filename, 'rb') as f:
        content = f.read()

    async with httpx.AsyncClient() as cl:
        response = await cl.post(
            'http://localhost:8081',
            files={"photo": (filename, content)}
        )

    temperatures_arr = np.frombuffer(response.content, dtype=np.float32)
    temperatures_arr = temperatures_arr.reshape((height, width))

    print(temperatures_arr)

asyncio.run(main())