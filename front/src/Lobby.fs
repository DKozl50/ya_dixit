module Lobby

open Feliz
open Feliz.Bulma
open Model
open Util

type private RefT = IRefValue<option<Browser.Types.HTMLInputElement>>

let private setName name =
    globalDispatch
    ^ Msg.InternalMsg
    ^ InternalMessage.UpdateStorage { Name = Some name; Avi = None }

let private sendJoinMessage id =
    globalDispatch
    ^ Msg.UserMsg
    ^ UserMessage.JoinRoom id

let private lobbyButtonControl (refName: RefT) (refID: RefT) =
    Bulma.button.button [ color.isPrimary
                          prop.text "Погнали"
                          prop.onClick (fun _ ->
                              let name = refName.current.Value.value
                              let id = refID.current.Value.value
                              setName name
                              sendJoinMessage id) ]
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

let private lobbyInputControl (refName: RefT) (refID: RefT) =
    Bulma.field.div [ field.hasAddons
                      spacing.mx4
                      spacing.my4
                      prop.style [ style.width (length.em 33) ]
                      prop.children [ lobbyInputIdControl refID
                                      lobbyButtonControl refName refID ] ]


let private lobbyInputComponent =
    React.functionComponent (fun () ->
        let refName = React.useInputRef ()
        let refID = React.useInputRef ()
        [ lobbyInputNameControl refName
          lobbyInputControl refName refID ])

let private lobbyTitle =
    Bulma.title.h1 [ prop.text "Imaginarium v2.0"
                     prop.style [ style.textAlign.center ]
                     spacing.my5
                     title.is3 ]

let renderLobby =
    Bulma.card
        [ Bulma.cardContent [ spacing.px0
                              spacing.py0
                              prop.children [ lobbyTitle
                                              lobbyInputComponent () ] ] ]
