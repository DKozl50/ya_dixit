module Socket

open Browser
open Thoth.Json

let private socket =
    WebSocket.Create("ws://localhost:5000/socket")

let mutable private messageQueue : string list = []

let private processQueue _ =
    for msg in messageQueue do socket.send msg
    messageQueue <- []

socket.onopen <- processQueue

let sendJson (json: string) = 
    if socket.readyState = Types.WebSocketState.OPEN then
        socket.send json
    else
        messageQueue <- messageQueue @ [json]

let inline sendObject (x: 'T) = Encode.Auto.toString (4, x) |> sendJson
let inline sendObjectCmd (x: 'T) = Elmish.Cmd.OfFunc.attempt sendObject x raise

let private parseServerMessage (json: string): Result<Model.ServerMessage, string> = Decode.Auto.fromString (json)

let serverMessageSubscription (_: Model.ModelState) =
    let sub dispatch =
        let f (s: Types.MessageEvent) =
            printfn "Message recieved:\n%A" (s.data.ToString())
            match s.data.ToString() |> parseServerMessage with
            | Ok msg ->
                printfn "Message successfully parsed:\n%A" msg
                Model.Msg.ServerMsg msg |> dispatch
            | Error s -> eprintfn "Error when parsing the message:\n%A" s

        socket.onmessage <- f

    Elmish.Cmd.ofSub sub
