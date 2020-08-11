module Render.Room

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

type private CardOptions =
    { ID: CardID
      Highlighted: bool
      Selectable: bool
      Dispatch: Msg -> unit }

let private imgSrcByID (id: CardID) = "/img/" + id + ".jpg"

let private cardComponent' (o: CardOptions) =
    Bulma.card [ prop.classes [ "game-card"
                                if o.Highlighted then "chosen" ]
                 spacing.mx3
                 prop.children [ Html.img [ prop.src (imgSrcByID o.ID) ] ]
                 if o.Selectable
                 then prop.onClick (fun _ -> o.Dispatch(Msg.UserMsg(UserMessage.SelectCard o.ID))) ]

let private cardComponent = React.functionComponent cardComponent'

let playerSvg (moveAvailable: bool) =
    Html.svg [ prop.style [ style.width (length.px 64)
                            style.height (length.px 64)
                            style.position.absolute
                            style.top 0 ]
               prop.children
                   [ Html.circle [ prop.cx 32
                                   prop.cy 32
                                   prop.r 30
                                   prop.custom ("fill", "transparent")
                                   prop.strokeWidth 4
                                   prop.stroke (if moveAvailable then "#33EE11" else "transparent") ] ] ]

let playerAviPlaceholder =
    "https://bulma.io/images/placeholders/128x128.png"

let private playerCompoment' (p: Player) =
    Html.figure [ prop.className "image"
                  ++ spacing.my3
                  ++ image.is64x64
                  prop.children [ playerSvg p.MoveAvailable
                                  Html.img [ image.isRounded
                                             prop.src playerAviPlaceholder ] ] ]

let private playerCompoment = React.functionComponent playerCompoment'

type private TurnButtonOptions =
    { Highlighted: bool
      Dispatch: Msg -> unit }

let private turnButtonComponent' (o: TurnButtonOptions) =
    Html.a [ prop.classes [ "end-turn-btn"
                            if o.Highlighted then "chosen" ]
             prop.text "Закончить ход"
             if o.Highlighted
             then prop.onClick (fun _ -> UserMessage.EndTurn |> Msg.UserMsg |> o.Dispatch) ]

let private turnButtonComponent =
    React.functionComponent turnButtonComponent'

let private handComponent' (a: {| cards: Fable.React.ReactElement list |}) =
    Bulma.card [ prop.className "hand"
                 prop.children
                     [ Bulma.cardContent [ spacing.px3
                                           prop.children
                                               [ Html.div [ prop.className
                                                                "d-flex justify-content-between align-items-center"
                                                            prop.children a.cards ] ] ] ] ]

let private handComponent = React.functionComponent handComponent'

let private settingsComponent' () =
    Bulma.card [ prop.className "settings"
                 prop.children
                     [ Bulma.cardContent
                         [ Bulma.icon [ icon.isLarge
                                        prop.children [ Html.i [ prop.className "fas fa-cog fa-3x" ] ] ] ] ] ]

let private settingsComponent =
    React.functionComponent settingsComponent'

let private playerListComponent' (a: {| players: Fable.React.ReactElement list |}) =
    Bulma.card [ prop.className "player-list"
                 prop.children
                     [ Bulma.cardContent [ prop.className "d-flex flex-column"
                                           spacing.py3
                                           prop.children a.players ] ] ]

let private playerListComponent =
    React.functionComponent playerListComponent'

type private RefT = IRefValue<option<Browser.Types.HTMLInputElement>>

let private tellStory (story: RefT) =
    UserMessage.TellStory story.current.Value.value
    |> Msg.UserMsg

let private storyInputField (clickable: bool) (dispatch: Msg -> unit) (story: RefT) =
    Bulma.field.div [ field.hasAddons
                      prop.children [ Bulma.control.div [ control.isExpanded
                                                          prop.children
                                                              [ Bulma.input.text [ prop.placeholder "Ваша история тут"
                                                                                   prop.ref story ] ] ]
                                      Bulma.control.div
                                          [ Bulma.button.button [ color.isSuccess
                                                                  prop.text "Готово"
                                                                  if clickable
                                                                  then prop.onClick (fun _ ->
                                                                           tellStory story |> dispatch) ] ] ] ]

type private StoryInputOptions =
    { Clickable: bool
      Dispatch: Msg -> unit }

let private storyInputComponent =
    React.functionComponent (fun (o: StoryInputOptions) ->
        let ref = React.useInputRef ()
        storyInputField o.Clickable o.Dispatch ref)

type private TimerOptions = { Phase: GamePhase; Player: Player }

let private timerComponent' progress =
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
                                                   prop.src playerAviPlaceholder ] ] ] ]

let private hasTimer =
    function
    | GamePhase.Waiting -> false
    | GamePhase.Victory _ -> false
    | _ -> true

let private timerComponent =
    React.functionComponent (fun (o: TimerOptions) ->
        let (progress, setProgress) = React.useState (0.)

        let subscribeToInterval () =
            let subId =
                Fable.Core.JS.setInterval (fun _ -> if hasTimer o.Phase then setProgress (progress + 1.)) 250

            { new System.IDisposable with
                member this.Dispose() = Fable.Core.JS.clearInterval (subId) }

        React.useEffect (subscribeToInterval, [| box o.Phase |])
        timerComponent' progress)

type private StoryComponentOptions =
    { Player: Player
      Story: string option }

let private msgOfStoryO =
    function
    | None -> "Is making up a story"
    | Some s -> sprintf "Tells a story: %s" s

let private storyComponent' (o: StoryComponentOptions) =
    Bulma.levelItem [ spacing.ml5
                      prop.children
                          [ Bulma.container [ Bulma.title.h3 [ title.is3
                                                               prop.text (o.Player.Name) ]
                                              Html.p (msgOfStoryO o.Story) ] ] ]

let private storyComponent = React.functionComponent storyComponent'

type private HeadBarOptions =
    { Phase: GamePhase
      Storyteller: Player
      ActiveInput: bool
      ActiveButton: bool
      Story: string option
      Dispatch: Msg -> unit }

let private headBarComponent' (o: HeadBarOptions) =
    Bulma.card [ prop.className "top"
                 prop.children
                     [ Bulma.cardContent [ Bulma.level [ timerComponent
                                                             { Phase = o.Phase
                                                               Player = o.Storyteller }
                                                         storyComponent
                                                             { Story = o.Story
                                                               Player = o.Storyteller }
                                                         Bulma.levelRight [] ]
                                           if o.ActiveInput then
                                               storyInputComponent
                                                   { Clickable = o.ActiveButton
                                                     Dispatch = o.Dispatch } ] ] ]

let private headBarComponent =
    React.functionComponent headBarComponent'

let private exitButtonComponent =
    React.functionComponent (fun (a: {| Dispatch: Msg -> unit |}) ->
        Html.a [ prop.className "delete is-large"
                 prop.style [ style.position.absolute
                              style.top (length.px 10)
                              style.right (length.px 10) ]
                 prop.onClick (fun _ -> a.Dispatch(Msg.UserMsg(UserMessage.LeaveRoom))) ])

let tableComponent =
    React.functionComponent (fun (a: {| cards: Fable.React.ReactElement list |}) -> a.cards)

type private TotalState =
    { ID: string
      State: GameState
      Dispatch: Msg -> unit }

let private roomComponent =
    React.functionComponent (fun (s: TotalState) ->
        React.useEffectOnce (fun () -> printfn "%A" s.ID)
        let moveA = s.State.Client.MoveAvailable
        let cardSelected = s.State.Hand.SelectedCard.IsNone

        let isStoryteller =
            s.State.Client.Role = PlayerRole.Storyteller

        let isListener =
            s.State.Client.Role = PlayerRole.Listener

        let phase = s.State.Phase

        let handSelectable =
            moveA
            && ((isStoryteller && phase = GamePhase.Storytelling)
                || (isListener && phase = GamePhase.Matching))

        let tableSelectable =
            moveA && isListener && phase = GamePhase.Guessing

        let btnClickable = moveA && cardSelected

        let storyteller =
            if isStoryteller then
                s.State.Client
            else
                List.tryFind (fun p -> p.Role = PlayerRole.Storyteller) s.State.Opponents
                |> Option.defaultValue s.State.Client

        let handMap id =
            { ID = id
              Highlighted = Option.exists ((=) id) s.State.Hand.SelectedCard
              Selectable = handSelectable
              Dispatch = s.Dispatch }

        let tableMap id =
            { ID = id
              Highlighted = Option.exists ((=) id) s.State.Hand.SelectedCard
              Selectable = tableSelectable
              Dispatch = s.Dispatch }

        [ headBarComponent
            { Phase = phase
              Storyteller = storyteller
              ActiveInput = isStoryteller && phase = GamePhase.Storytelling
              ActiveButton = btnClickable
              Story = s.State.Table.Story
              Dispatch = s.Dispatch }
          playerListComponent {| players = s.State.Opponents |> List.map playerCompoment |}
          turnButtonComponent
              { Highlighted = btnClickable && isListener
                Dispatch = s.Dispatch }
          exitButtonComponent {| Dispatch = s.Dispatch |}
          settingsComponent ()
          handComponent
              {| cards =
                     s.State.Hand.Cards
                     |> List.map handMap
                     |> List.map cardComponent |}
          tableComponent
              {| cards =
                     s.State.Table.Cards
                     |> List.map fst
                     |> List.map tableMap
                     |> List.map cardComponent |} ])

let renderRoom (id: string, state: GameState) (dispatch: Msg -> unit) =
    roomComponent
        { State = state
          ID = id
          Dispatch = dispatch }
