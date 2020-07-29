module Render.Lobby

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

type private RefT = IRefValue<option<Browser.Types.HTMLInputElement>>

let private sendJoinMessage dispatch =
    function
    | "" ->
        dispatch (Msg.UserMsg UserMessage.CreateRoom)
        printfn "%A" ""
    | id ->
        dispatch (Msg.UserMsg(UserMessage.JoinRoom id))
        printfn "%A" id

let private lobbyButtonControl (ref': RefT) dispatch =
    Bulma.button.button
        [ color.isPrimary
          prop.text "Погнали"
          prop.onClick (fun _ ->
              match ref'.current with
              | Some v -> v.value |> sendJoinMessage dispatch
              | None -> ()) ]
    |> Bulma.control.div

let private lobbyInputControl (ref': RefT) =
    Bulma.control.div
        [ control.isExpanded
          prop.children
              [ Bulma.input.text
                  [ prop.placeholder "ID комнаты (оставьте пустым для создания своей)"
                    prop.ref ref' ] ] ]

let private lobbyInputCompoment =
    React.functionComponent (fun (wrap: {| dispatch: Elmish.Dispatch<Msg> |}) ->
        let inputRef = React.useInputRef ()
        Bulma.field.div
            [ field.hasAddons
              spacing.mx4
              spacing.my4
              prop.style [ style.width (length.em 33) ]
              prop.children
                  [ lobbyInputControl inputRef
                    lobbyButtonControl inputRef wrap.dispatch ] ])

let private lobbyTitle =
    Bulma.title.h1
        [ prop.text "Крестики-Нолики"
          prop.style [ style.textAlign.center ]
          spacing.my5
          title.is3 ]

let renderLobby dispatch =
    Bulma.card
        [ Bulma.cardContent
            [ spacing.px0
              spacing.py0
              prop.children
                  [ lobbyTitle
                    lobbyInputCompoment {| dispatch = dispatch |} ] ] ]
