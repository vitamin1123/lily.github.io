from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager_text:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class ConnectionManager:
    def __init__(self):
        # 存放**的链接
        self.active_connections: list[dict[str, WebSocket]] = []

    async def connect(self, user: str, ws: WebSocket):
        # 链接
        await ws.accept()
        self.active_connections.append({"user": user, "ws": ws})

    def disconnect(self, user: str, ws: WebSocket):
        # 关闭时 移除ws对象
        self.active_connections.remove({"user": user, "ws": ws})


    async def send_other_message_json(self, message: dict, user: str):
        # 发送个人消息
        for connection in self.active_connections:
            if connection["user"] == user:
                await connection['ws'].send_json(message)

    async def broadcast_json(self, data: dict):
        # 广播消息
        for connection in self.active_connections:
            await connection['ws'].send_json(data)

manager = ConnectionManager()

@app.websocket("/ws/{user}")
async def websocket_many_point(websocket: WebSocket, user:str):
    print(user)
    #await manager.connect(websocket)
    await manager.connect(user, websocket)
    #await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            print("data",data)
            senduser=data['username']
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
            # if senduser:
                # await manager.send_other_message_json(data,senduser)
            # else:
            await manager.broadcast_json(data)
            #await websocket.send_text(f"收到的啥玩意儿:{data}")
    except WebSocketDisconnect:
        manager.disconnect(user,websocket)
        await manager.broadcast_json({"离开":senduser})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='websocket_demo0:app', host="127.0.0.1", port=8010, reload=True)