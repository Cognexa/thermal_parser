import numpy as np
from fastapi import FastAPI
from fastapi import File, UploadFile, Response

from thermal_parser import Thermal

app = FastAPI()

@app.post('/')
async def extract_temperatures(photo: UploadFile = File(...)):
    content = await photo.read()

    thermal = Thermal(dtype=np.float32)
    with open(f'/tmp/{photo.filename}', 'wb') as f:
        f.write(content)

    temperature = thermal.parse(filepath_image=f'/tmp/{photo.filename}')
    print(temperature.shape)
    return Response(
        temperature.tobytes(),
        media_type="application/octet-stream",
    )
