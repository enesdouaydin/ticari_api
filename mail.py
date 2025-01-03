# from fastapi import FastAPI, WebSocket
# from fastapi.responses import HTMLResponse
# app = FastAPI()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()    
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Mesaj alindi: {data}")

# html= """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>WebSocket Test</title>
#     </head>
#     <body>
#         <h1>WebSocket Test</h1>
#         <input type="text" id="messageText" />
#         <button onclick="sendMessage()">Send Message</button>
#         <ul id="messages"></ul>

#         <script>
    
#             var ws = new WebSocket("ws://localhost:8000/ws");
#             ws.onopen = function(event) {
#                 console.log("WebSocket opened.");
#             };
                
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById("messages");
#                 var message = document.createElement("li");
#                 var content = document.createTextNode(event.data);
#                 message.appendChild(content);
#                 messages.appendChild(message);
#          };
        
#             function SenMessage(event) {
#                 var input = document.getElementById("messageText");
#                 ws.send(input.value);
#                 input.value = "";
#                 event.preventDefault();
#             }

#         </script>
#     </body>
# </html>
        
        
        
        
        
# """