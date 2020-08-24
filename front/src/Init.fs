module Init

open Elmish
open Model

let initState =
    let x =
        Browser.Dom.document.getElementById("initialState").innerText
        |> Thoth.Json.Decode.Auto.fromString<ModelState>

    match x with
    | Ok state -> state
    | Error e ->
        eprintfn "Error parsing initial state:\n%A" e
        ModelState.Lobby

let initMessage =
    let x =
        Browser.Dom.document.getElementById("initialMessage").innerText
        |> Thoth.Json.Decode.Auto.fromString<Msg>

    match x with
    | Ok msg -> Cmd.ofMsg msg
    | Error e ->
        eprintfn "Error parsing initial message:\n%A" e
        Cmd.none

let initModel () = initState, initMessage
