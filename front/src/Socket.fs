module Socket

open Browser

let socket =
    WebSocket.Create("wss://www.example.com/socketserver")

let sendJson (json: string) = ()
