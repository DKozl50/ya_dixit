module Render

open Feliz
open Feliz.Bulma
open Model

let private renderConnecting = Bulma.title.h1 "Connecting"

let render model dispatch =
    match model with
    | ModelState.Lobby -> Render.Lobby.renderLobby dispatch
    | ModelState.Connecting -> renderConnecting
    | ModelState.Room (id, state) -> Render.Room.renderRoom id state dispatch
