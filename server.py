import logging
import subprocess
import tempfile

import numpy as np
from fastapi import FastAPI
from fastapi import File, UploadFile, Response, HTTPException

log = logging.getLogger("uvicorn")
app = FastAPI()

PATH_TO_BINARY = "lib/dji_thermal_sdk_v1.7_lean/dji_irp"


@app.post("/")
async def extract_temperatures(photo: UploadFile = File(...)):
    content = await photo.read()

    width = None
    height = None

    with tempfile.NamedTemporaryFile() as input_file, tempfile.NamedTemporaryFile(suffix='.raw') as output_file:

        # Write the uploaded content to the temporary input file
        input_file.write(content)
        input_file.flush()

        # Get the file paths for subprocess
        input_path = input_file.name
        output_path = output_file.name

        try:
            # Run binary in subprocess, communicate output
            p = subprocess.Popen(
                [
                    PATH_TO_BINARY,
                    "-s",
                    input_path,
                    "-a",
                    "measure",
                    "-o",
                    output_path,
                    "--measurefmt",
                    "float32",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = p.communicate()
            out = out.decode("utf-8")
            log.info(out)
            if err:
                log.error(err.decode("utf-8"))

            # Read the output file
            temperature = np.fromfile(output_path, dtype=np.float32)
        except Exception as e:
            log.error(f"Error running thermal parser binary: {e}")

            raise HTTPException(
                status_code=500,
                detail=f"Error running thermal parser binary\n{e}",
            )

        try:
            # Parse output for width and height so we can reshape the temperature data
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
