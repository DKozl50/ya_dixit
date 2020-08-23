module Render.Lobby

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model
open Components.LobbyInput

let private lobbyTitle =
    Bulma.title.h1 [ prop.text "Imaginarium v2.0"
                     prop.style [ style.textAlign.center ]
                     spacing.my5
                     title.is3 ]

let renderLobby dispatch =
    Bulma.card
        [ Bulma.cardContent [ spacing.px0
                              spacing.py0
                              prop.children [ lobbyTitle
                                              lobbyInputCompoment {| dispatch = dispatch |} ] ] ]
