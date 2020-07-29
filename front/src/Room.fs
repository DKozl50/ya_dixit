module Render.Room

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private sendMoveMessage dispatch x =
    UserMessage.MakeMove x |> Msg.UserMsg |> dispatch

let private cellRep =
    function
    | GameCell.Empty -> ""
    | GameCell.Cross -> "X"
    | GameCell.Nought -> "O"

let private progressMessage =
    function
    | GameProgress.Waiting -> "Ожидание второго игрока..."
    | GameProgress.CrossTurn -> "Ходят крестики"
    | GameProgress.NoughtTurn -> "Ходят нолики"
    | GameProgress.CrossWin -> "Победили крестики!"
    | GameProgress.NoughtWin -> "Победили нолики!"
    | GameProgress.Draw -> "Ничья"

let private isPlayerTurn (state: GameState) =
    match state.Side, state.Progress with
    | PlayerSide.Cross, GameProgress.CrossTurn -> true
    | PlayerSide.Nought, GameProgress.NoughtTurn -> true
    | _ -> false

type private CellArgs =
    { Dispatch: Elmish.Dispatch<Msg>
      Number: int
      Clickable: bool
      Content: GameCell }

let private cellComponent =
    React.functionComponent (fun (a: CellArgs) ->
        Bulma.card
            [ prop.className "cell"
              if a.Clickable
              then prop.onClick (fun _ -> sendMoveMessage a.Dispatch a.Number)
              prop.children [ Bulma.title.h1 (cellRep a.Content) ] ])

let private cellArgsOfModel (state: GameState) dispatch x =
    let cellContent = state.Field.[x]
    { Dispatch = dispatch
      Number = x
      Clickable =
          (cellContent = GameCell.Empty)
          && (isPlayerTurn state)
      Content = cellContent }

let private fieldDiv ((_, state): string * GameState) dispatch =
    Html.div
        [ prop.className "card-content d-flex flex-wrap px-0 py-0 justify-content-around align-items-center fullheight"
          prop.children [ for i in 0 .. 8 -> cellArgsOfModel state dispatch i |> cellComponent ] ]

let private roomIdDiv ((roomId, _): string * GameState) =
    Bulma.card
        [ prop.style
            [ style.position.absolute
              style.bottom (length.em -7)
              style.width (length.percent 100) ]
          prop.children
              [ Bulma.cardContent
                  [ prop.className "room-id-field"
                    prop.children [ Html.p roomId ] ] ] ]

let private gameProgressDiv ((_, state): string * GameState) =
    Bulma.title.h1
        [ prop.style
            [ style.position.absolute
              style.top (length.em -3)
              style.width (length.percent 100)
              style.textAlign.center ]
          prop.text (progressMessage state.Progress) ]

let private exitButton dispatch =
    Bulma.delete
        [ delete.isLarge
          prop.style
              [ style.position.absolute
                style.top (length.px 10)
                style.right (length.px 10) ]
          prop.onClick (fun _ -> UserMessage.LeaveRoom |> Msg.UserMsg |> dispatch )
        ]

let renderRoom (model: string * GameState) dispatch =
    Html.div
        [ prop.className "fullheight d-flex justify-content-center align-items-center"
          prop.children
              [ exitButton dispatch
                Bulma.card
                    [ prop.children
                        [ gameProgressDiv model
                          roomIdDiv model
                          fieldDiv model dispatch ]
                      prop.style
                          [ style.width (length.em 30)
                            style.height (length.em 30) ] ] ] ]
