import api
from fastapi import Body, UploadFile
from config import api_init, Tags
from examples import ex
from fastapi.responses import FileResponse

# pre-config #
app = api_init()


#|=============================[User routes]=============================|
# 1. /apps/upload
@app.post("/apps/upload", tags=[Tags.apps], summary="Register user")
async def user_create(data = Body(example=ex.user_create)):
    print(data)
    # r = await api.user_create(data)
    # return r
#--------------------------------------------------------------------------