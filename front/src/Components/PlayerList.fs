module Components.PlayerList

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

type PlayerListArgs =
    { Players: ReactElement list }

let private playerListComponent' (a: PlayerListArgs) =
    Bulma.card [ prop.className "player-list"
                 prop.children
                     [ Bulma.cardContent [ prop.className "d-flex flex-column"
                                           spacing.py3
                                           prop.children a.Players ] ] ]

let playerListComponent =
    React.functionComponent playerListComponent'