from fastapi import FastAPI, Response
import qrcode
import io

app = FastAPI()
#
@app.get("/generate")
def generate_qr(data: str):
    buffer = io.BytesIO()
    img = qrcode.make(data)
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return Response(content=buffer.read(), media_type="image/png")