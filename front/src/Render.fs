module Render

open Feliz
open Feliz.Bulma
open Model

let private renderConnecting = Bulma.title.h1 "Connecting"

let render model _ =
    match model.Page with
    | Page.Lobby -> Lobby.renderLobby
    | Page.Connecting -> renderConnecting
    | Page.GameRoom state -> Room.renderRoom state
