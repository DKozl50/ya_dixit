module Render.Lobby

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

type private RefT = IRefValue<option<Browser.Types.HTMLInputElement>>

let private sendJoinMessage dispatch name =
    function
    | "" ->
        UserMessage.CreateRoom name
        |> Msg.UserMsg
        |> dispatch
    | id ->
        UserMessage.JoinRoom(id, name)
        |> Msg.UserMsg
        |> dispatch

let private lobbyButtonControl dispatch (refName: RefT) (refID: RefT) =
    Bulma.button.button [ color.isPrimary
                          prop.text "Погнали"
                          prop.onClick (fun _ ->
                              let name = refName.current.Value.value
                              let id = refID.current.Value.value
                              sendJoinMessage dispatch name id) ]
    |> Bulma.control.div

let private lobbyInputIdControl (ref': RefT) =
    Bulma.control.div [ control.isExpanded
                        prop.children
                            [ Bulma.input.text [ prop.placeholder "ID комнаты (оставьте пустым для создания своей)"
                                                 prop.ref ref' ] ] ]

let private lobbyInputNameControl (ref': RefT) =
    Bulma.field.div [ spacing.mx4
                      spacing.my4
                      prop.style [ style.width (length.em 33) ]
                      prop.children
                          [ Bulma.control.div [ control.isExpanded
                                                prop.children
                                                    [ Bulma.input.text [ prop.placeholder "Введите свой никнейм"
                                                                         prop.ref ref' ] ] ] ] ]

let private lobbyInputControl dispatch (refName: RefT) (refID: RefT) =
    Bulma.field.div [ field.hasAddons
                      spacing.mx4
                      spacing.my4
                      prop.style [ style.width (length.em 33) ]
                      prop.children [ lobbyInputIdControl refID
                                      lobbyButtonControl dispatch refName refID ] ]


let private lobbyInputCompoment =
    React.functionComponent (fun (wrap: {| dispatch: Elmish.Dispatch<Msg> |}) ->
        let refName = React.useInputRef ()
        let refID = React.useInputRef ()
        let dispatch = wrap.dispatch
        [ lobbyInputNameControl refName
          lobbyInputControl dispatch refName refID ])

let private lobbyTitle =
    Bulma.title.h1 [ prop.text "Imaginarium"
                     prop.style [ style.textAlign.center ]
                     spacing.my5
                     title.is3 ]

let renderLobby dispatch =
    Bulma.card
        [ Bulma.cardContent [ spacing.px0
                              spacing.py0
                              prop.children [ lobbyTitle
                                              lobbyInputCompoment {| dispatch = dispatch |} ] ] ]
