module RoomElements

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model
open Util

type CardArgs =
    { Info: CardInfo
      Chosen: bool
      Correct: bool
      Selectable: bool }

let private blob (p: Player) =
    Html.figure [ prop.className "image"
                  ++ spacing.mx1
                  ++ spacing.my1
                  prop.children
                      [ Html.img [ image.isRounded
                                   prop.src ^ aviSrc p.Avi ] ] ]

let private owner (p: Player) =
    Html.div [ prop.className "author"
               ++ spacing.px1
               ++ spacing.py1
               prop.children [ blob p ] ]

let private voters (p: Player list) =
    Html.div [ prop.className "voters d-flex px-1 py-1 flex-wrap"
               prop.children (p |> List.map blob) ]

let private cardContent (id: CardID) =
    Bulma.cardContent [ Html.img [ prop.src ^ imgSrc id ] ]

let private selectCardMsg id =
    globalDispatch
    ^ Msg.UserMsg
    ^ UserMessage.SelectCard id

let card (a: CardArgs) =
    Bulma.card [ prop.classes [ "game-card"
                                if a.Chosen then "chosen"
                                if a.Correct then "correct" ]
                 spacing.mx3
                 prop.children [ cardContent a.Info.ID
                                 if a.Info.Owner.IsSome then
                                     owner a.Info.Owner.Value
                                     voters a.Info.Voters ]
                 if a.Selectable
                 then prop.onClick (fun _ -> selectCardMsg a.Info.ID) ]

let player (p: Player) =
    Html.div [ prop.className "user d-flex align-items-center"
               prop.children [ Bulma.image [ image.is64x64 ++ spacing.mx3 ++ spacing.my3
                                             prop.children
                                                 [ Html.img [ prop.className "active-user" ++ image.isRounded
                                                              prop.src ^ aviSrc p.Avi ] ] ]
                               Bulma.title.h1 [ prop.className "username"
                                                ++ title.is6
                                                ++ spacing.ml3
                                                ++ spacing.mr5
                                                prop.text p.Name ]
                               Bulma.title.h1 [ prop.className "align-self-right" ++ title.is6
                                                prop.text p.Score ] ] ]

let private sendEndTurnMsg () =
    globalDispatch ^ Msg.UserMsg ^ UserMessage.EndTurn

let turnButton (clickable: bool) =
    Html.a [ prop.classes [ "end-turn-btn"
                            if clickable then "green" else "inactive" ]
             prop.text "Закончить ход"
             if clickable
             then prop.onClick (fun _ -> sendEndTurnMsg ()) ]

let hand (cards: ReactElement list) =
    Bulma.card [ prop.className "hand"
                 prop.children
                     [ Bulma.cardContent [ spacing.px3
                                           prop.children
                                               [ Html.div [ prop.className
                                                                "d-flex justify-content-between align-items-center"
                                                            prop.children cards ] ] ] ] ]




let playerList (players: ReactElement list) =
    Bulma.card [ prop.className "player-list"
                 prop.children
                     [ Bulma.cardContent [ prop.className "d-flex flex-column"
                                           ++ spacing.py3
                                           ++ spacing.px3
                                           prop.children players ] ] ]



let private tellStory (story: RefT) =
    globalDispatch
    ^ Msg.UserMsg
    ^ UserMessage.TellStory story.current.Value.value


let private storyInputField (clickable: bool) (story: RefT) =
    Bulma.field.div [ field.hasAddons
                      prop.children [ Bulma.control.div [ control.isExpanded
                                                          prop.children
                                                              [ Bulma.input.text [ prop.placeholder "Ваша история тут"
                                                                                   prop.ref story ] ] ]
                                      Bulma.control.div
                                          [ Bulma.button.button [ color.isSuccess
                                                                  prop.text "Готово"
                                                                  if clickable then prop.onClick (fun _ ->
                                                                                        tellStory story) ] ] ] ]

let storyInputComponent =
    React.functionComponent (fun (clickable: bool) ->
        let ref = React.useInputRef ()
        storyInputField clickable ref)

type TimerArgs = { Phase: GamePhase; Player: Player }

let private timerComponent' (p: Player) progress =
    let p' = max progress 360.
    let o = -(188.49 / 360.) * p' + 188.49
    Bulma.levelLeft
        [ Html.figure [ prop.className "image" ++ image.is64x64
                        prop.children [ Html.svg [ prop.style [ style.width (length.px 64)
                                                                style.height (length.px 64)
                                                                style.position.absolute
                                                                style.top 0
                                                                style.transform.rotate -90 ]
                                                   prop.children
                                                       [ Html.circle [ prop.cx 32
                                                                       prop.cy 32
                                                                       prop.r 30
                                                                       prop.custom ("fill", "transparent")
                                                                       prop.strokeWidth 4
                                                                       prop.stroke "#33EE11"
                                                                       prop.custom ("strokeDasharray", 188.49)
                                                                       prop.custom ("strokeDashoffset", o) ] ] ]
                                        Html.img [ image.isRounded
                                                   prop.src ^ aviSrc p.Avi ] ] ] ]

let private hasTimer =
    function
    | GamePhase.Waiting
    | GamePhase.Victory _ -> false
    | _ -> true

let timerComponent =
    React.functionComponent (fun (a: TimerArgs) ->
        let (progress, setProgress) = React.useState (0.)

        let subscribeToInterval () =
            let subId =
                Fable.Core.JS.setInterval (fun _ -> if hasTimer a.Phase then setProgress (progress + 1.)) 250

            { new System.IDisposable with
                member _.Dispose() = Fable.Core.JS.clearInterval (subId) }

        React.useEffect (subscribeToInterval, [| box a.Phase |])
        timerComponent' a.Player progress)

type StoryArgs =
    { Player: Player
      Story: string option }

let private msgOfStoryO =
    function
    | None -> "Is making up a story"
    | Some s -> sprintf "Tells a story: %s" s

let story (a: StoryArgs) =
    Bulma.levelItem [ spacing.ml5
                      prop.children
                          [ Bulma.container [ Bulma.title.h3 [ title.is3
                                                               prop.text (a.Player.Name) ]
                                              Html.p (msgOfStoryO a.Story) ] ] ]

type HeadBarArgs =
    { Phase: GamePhase
      Storyteller: Player
      ActiveInput: bool
      ActiveButton: bool
      Story: string option }


let headBar (a: HeadBarArgs) =
    Bulma.card [ prop.className "top"
                 prop.children
                     [ Bulma.cardContent [ Bulma.level [ timerComponent
                                                             { Phase = a.Phase
                                                               Player = a.Storyteller }
                                                         story
                                                             { Story = a.Story
                                                               Player = a.Storyteller }
                                                         Bulma.levelRight [] ]
                                           if a.ActiveInput then storyInputComponent a.ActiveButton ] ] ]


let private exit () =
    globalDispatch
    ^ Msg.UserMsg
    ^ UserMessage.LeaveRoom

let exitButton =
    Bulma.delete [ delete.isLarge
                   prop.style [ style.position.absolute
                                style.top (length.px 10)
                                style.right (length.px 10) ]
                   prop.onClick (fun _ -> exit ()) ]

type TableArgs = { Cards: ReactElement list }

let tableComponent =
    React.functionComponent (fun (a: TableArgs) -> a.Cards)

let settingsHeader setIsOpen =
    Bulma.modalCardHead [ Bulma.modalCardTitle "Настройки пользователя"
                          Bulma.delete [ prop.ariaLabel "close"
                                         prop.onClick
                                         ^ fun _ -> setIsOpen false ] ]

let settignsFooter =
    Bulma.modalCardFoot [ Bulma.button.button [ color.isSuccess
                                                prop.text "ОК" ]
                          Bulma.button.button "Отмена" ]


let aviUploadField =
    Bulma.field.div [ Bulma.label "Загрузите файл авы"
                      Bulma.file [ file.hasName ++ file.isFullWidth
                                   prop.children
                                       [ Bulma.fileLabel.label [ Bulma.fileInput [ prop.name "resume" ]
                                                                 Bulma.fileCta [ Bulma.fileIcon
                                                                                     [ Html.i
                                                                                         [ prop.className
                                                                                             "fas fa-upload" ] ]
                                                                                 Bulma.fileLabel.label "тык" ]
                                                                 Bulma.fileName "здесь короче название файла" ] ] ] ]

let nicknameChangeField =
    Bulma.field.div [ Bulma.label "Выберите себе ник"
                      Bulma.control.div [ Bulma.input.text [ prop.placeholder "Здесь ваш оригинальный ник" ] ] ]

let previewField p =
    Bulma.field.div [ Bulma.label "Предпросмотр"
                      player p ]

let settingsBody p =
    Bulma.modalCardBody [ aviUploadField
                          nicknameChangeField
                          previewField p ]

let private applyUpdatedInfo (p: Player) (c: ClientData) =
    { p with
          Name = Option.defaultValue p.Name c.Name
          Avi = Option.defaultValue p.Avi c.Avi }

let settings p updatedInfo setUpdatedInfo setIsOpen =
    Bulma.modal [ modal.isActive
                  prop.children [ Bulma.modalBackground []
                                  Bulma.modalCard [ settingsHeader setIsOpen
                                                    settingsBody ^ applyUpdatedInfo p updatedInfo
                                                    settignsFooter ] ] ]

let settingsButton setIsOpen =
    Bulma.card [ prop.className "settings-button"
                 prop.onClick
                 ^ fun _ -> setIsOpen true
                 prop.children
                     [ Bulma.cardContent [ prop.className "fullheight"
                                           prop.children
                                               [ Bulma.icon [ icon.isMedium
                                                              prop.children
                                                                  [ Html.i [ prop.className "fas fa-cog fa-2x" ] ] ] ] ] ] ]

let private settingsComponent' p =
    let updatedInfo, setUpdatedInfo =
        React.useState { Name = None; Avi = None }

    let isOpen, setIsOpen = React.useState false
    [ settingsButton setIsOpen
      if isOpen
      then settings p updatedInfo setUpdatedInfo setIsOpen ]

let settingsComponent =
    React.functionComponent settingsComponent'
