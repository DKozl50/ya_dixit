module Render

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private renderConnecting dispatch = Bulma.title.h1 "Connecting"

let private renderRoom dispatch = Bulma.title.h1 "Not implemented"

let render model dispatch =
    match model with
    | ModelState.Lobby -> Render.Lobby.renderLobby dispatch
    | ModelState.Connecting -> renderConnecting dispatch
    | ModelState.Room _ -> renderRoom dispatch
