import numpy as np
from fastapi import FastAPI
from fastapi import File, UploadFile, Response, HTTPException
import logging
import subprocess

log = logging.getLogger("uvicorn")
app = FastAPI()

PATH_TO_BINARY = "lib/dji_thermal_sdk_v1.7_lean/dji_irp"


@app.post("/")
async def extract_temperatures(photo: UploadFile = File(...)):
    content = await photo.read()

    with open(f"/tmp/{photo.filename}", "wb") as f:
        f.write(content)

    raw_filename = f"/tmp/{photo.filename}.raw"
    try:
        # run binary in subprocess, communicate output:
        p = subprocess.Popen(
            [
                PATH_TO_BINARY,
                "-s",
                f"/tmp/{photo.filename}",
                "-a",
                "measure",
                "-o",
                raw_filename,
                "--measurefmt",
                "float32",
            ],
            stdout=subprocess.PIPE,
        )
        out, err = p.communicate()
        out = out.decode("utf-8")
        log.info(out)
        log.error(err)

        # read the output file
        temperature = np.fromfile(raw_filename, dtype=np.float32)
    except Exception as e:
        log.error(f"Error running thermal parser binary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running thermal parser binary\n{e}",
        )

    try:
        # parse output for width and height so we can reshape the temperature data
        width = out.split("image  width : ")[1].split("\n")[0]
        height = out.split("image height : ")[1].split("\n")[0]

        temperature = temperature.reshape((int(height), int(width)))

        log.info(f"Read temperature data shape: {temperature.shape}")
    except Exception as e:
        log.error(f"Error parsing output and reshaping temperature data: {e}")

    return Response(
        temperature.tobytes(),
        media_type="application/octet-stream",
        headers={"image_width": width, "image_height": height} if width and height else {},
    )
