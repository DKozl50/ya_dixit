module Render.Room

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private imgSrcByID (id: CardID) = "/img/" + id + ".jpg"

// Unfortunately, Fable.React.FunctionComponent requires a single record argument
// Expect lots of boilerplate for that reason

type private TotalState =
    { ID: string
      State: GameState
      Dispatch: Msg -> unit }

    member this.Client = this.State.Client
    member this.Hand = this.State.Hand
    member this.Phase = this.State.Phase
    member this.Opponents = this.State.Opponents
    member this.Table = this.State.Table
    member this.MoveAvailable = this.Client.MoveAvailable
    member this.CardSelected = this.Hand.SelectedCard.IsSome

    member this.IsStoryteller =
        this.Client.Role = PlayerRole.Storyteller

    member this.IsListener = this.Client.Role = PlayerRole.Listener

    member this.HandSelectable =
        this.MoveAvailable
        && ((this.IsStoryteller
             && this.Phase = GamePhase.Storytelling)
            || (this.IsListener && this.Phase = GamePhase.Matching))

    member this.TableSelectable =
        this.MoveAvailable
        && this.IsListener
        && this.Phase = GamePhase.Guessing

    member this.EndTurnClickable = this.MoveAvailable && this.CardSelected

    member this.Storyteller =
        if this.IsStoryteller then
            this.Client
        else
            List.tryFind (fun p -> p.Role = PlayerRole.Storyteller) this.Opponents
            |> Option.defaultValue this.Client

type private CardArgs =
    { ID: CardID
      Highlighted: bool
      Selectable: bool
      Dispatch: Msg -> unit }
    static member OfState'Hand (t: TotalState) (id: CardID) =
        { ID = id
          Highlighted = t.Hand.SelectedCard |> Option.contains id
          Selectable = t.HandSelectable
          Dispatch = t.Dispatch }

    static member OfState'Table (t: TotalState) (id: CardID) =
        { ID = id
          Highlighted = t.Hand.SelectedCard |> Option.contains id
          Selectable = t.TableSelectable
          Dispatch = t.Dispatch }

let private cardComponent' (a: CardArgs) =
    Bulma.card [ prop.classes [ "game-card"
                                if a.Highlighted then "chosen" ]
                 spacing.mx3
                 prop.children [ Html.img [ prop.src (imgSrcByID a.ID) ] ]
                 if a.Selectable
                 then prop.onClick (fun _ -> a.Dispatch(Msg.UserMsg(UserMessage.SelectCard a.ID))) ]

let private cardComponent = React.functionComponent cardComponent'

let private playerSvg (moveAvailable: bool) =
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

let private playerAviPlaceholder =
    "https://bulma.io/images/placeholders/128x128.png"

let private playerCompoment' (p: Player) =
    Html.figure [ prop.className "image"
                  ++ spacing.my3
                  ++ image.is64x64
                  prop.children [ playerSvg p.MoveAvailable
                                  Html.img [ image.isRounded
                                             prop.src playerAviPlaceholder ] ] ]

let private playerCompoment = React.functionComponent playerCompoment'

type private TurnButtonArgs =
    { Highlighted: bool
      Dispatch: Msg -> unit }
    static member OfState(t: TotalState) =
        { Highlighted = t.EndTurnClickable && t.IsListener
          Dispatch = t.Dispatch }

let private turnButtonComponent' (a: TurnButtonArgs) =
    Html.a [ prop.classes [ "end-turn-btn"
                            if a.Highlighted then "chosen" ]
             prop.text (if a.Highlighted then "Закончить ход" else "Сделайте ход")
             if a.Highlighted
             then prop.onClick (fun _ -> UserMessage.EndTurn |> Msg.UserMsg |> a.Dispatch) ]

let private turnButtonComponent =
    React.functionComponent turnButtonComponent'

type private HandArgs =
    { Cards: Fable.React.ReactElement list }
    static member OfState(t: TotalState) =
        { Cards =
              t.Hand.Cards
              |> List.map (CardArgs.OfState'Hand t)
              |> List.map cardComponent }


let private handComponent' (a: HandArgs) =
    Bulma.card [ prop.className "hand"
                 prop.children
                     [ Bulma.cardContent [ spacing.px3
                                           prop.children
                                               [ Html.div [ prop.className
                                                                "d-flex justify-content-between align-items-center"
                                                            prop.children a.Cards ] ] ] ] ]

let private handComponent = React.functionComponent handComponent'

let private settingsComponent' () =
    Bulma.card [ prop.className "settings"
                 prop.children
                     [ Bulma.cardContent
                         [ Bulma.icon [ icon.isLarge
                                        prop.children [ Html.i [ prop.className "fas fa-cog fa-3x" ] ] ] ] ] ]

let private settingsComponent =
    React.functionComponent settingsComponent'

type private PlayerListArgs =
    { Players: ReactElement list }
    static member OfState(t: TotalState) =
        { Players =
              (t.Client :: t.Opponents)
              |> List.map playerCompoment }

let private playerListComponent' (a: PlayerListArgs) =
    Bulma.card [ prop.className "player-list"
                 prop.children
                     [ Bulma.cardContent [ prop.className "d-flex flex-column"
                                           spacing.py3
                                           prop.children a.Players ] ] ]

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

type private StoryInputArgs =
    { Clickable: bool
      Dispatch: Msg -> unit }

let private storyInputComponent =
    React.functionComponent (fun (a: StoryInputArgs) ->
        let ref = React.useInputRef ()
        storyInputField a.Clickable a.Dispatch ref)

type private TimerArgs = { Phase: GamePhase; Player: Player }

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
    React.functionComponent (fun (a: TimerArgs) ->
        let (progress, setProgress) = React.useState (0.)

        let subscribeToInterval () =
            let subId =
                Fable.Core.JS.setInterval (fun _ -> if hasTimer a.Phase then setProgress (progress + 1.)) 250

            { new System.IDisposable with
                member this.Dispose() = Fable.Core.JS.clearInterval (subId) }

        React.useEffect (subscribeToInterval, [| box a.Phase |])
        timerComponent' progress)

type private StoryComponentArgs =
    { Player: Player
      Story: string option }

let private msgOfStoryO =
    function
    | None -> "Is making up a story"
    | Some s -> sprintf "Tells a story: %s" s

let private storyComponent' (a: StoryComponentArgs) =
    Bulma.levelItem [ spacing.ml5
                      prop.children
                          [ Bulma.container [ Bulma.title.h3 [ title.is3
                                                               prop.text (a.Player.Name) ]
                                              Html.p (msgOfStoryO a.Story) ] ] ]

let private storyComponent = React.functionComponent storyComponent'

type private HeadBarArgs =
    { Phase: GamePhase
      Storyteller: Player
      ActiveInput: bool
      ActiveButton: bool
      Story: string option
      Dispatch: Msg -> unit }
    static member OfState(t: TotalState) =
        { Phase = t.Phase
          Storyteller = t.Storyteller
          ActiveInput =
              t.IsStoryteller
              && t.Phase = GamePhase.Storytelling
          ActiveButton = t.EndTurnClickable
          Story = t.Table.Story
          Dispatch = t.Dispatch }

let private headBarComponent' (a: HeadBarArgs) =
    Bulma.card [ prop.className "top"
                 prop.children
                     [ Bulma.cardContent [ Bulma.level [ timerComponent
                                                             { Phase = a.Phase
                                                               Player = a.Storyteller }
                                                         storyComponent
                                                             { Story = a.Story
                                                               Player = a.Storyteller }
                                                         Bulma.levelRight [] ]
                                           if a.ActiveInput then
                                               storyInputComponent
                                                   { Clickable = a.ActiveButton
                                                     Dispatch = a.Dispatch } ] ] ]

let private headBarComponent =
    React.functionComponent headBarComponent'

let private exitButtonComponent =
    React.functionComponent (fun (a: {| Dispatch: Msg -> unit |}) ->
        Html.a [ prop.className "delete is-large"
                 prop.style [ style.position.absolute
                              style.top (length.px 10)
                              style.right (length.px 10) ]
                 prop.onClick (fun _ -> a.Dispatch(Msg.UserMsg(UserMessage.LeaveRoom))) ])

type private TableArgs =
    { Cards: ReactElement list }
    static member OfState(t: TotalState) =
        { Cards =
              t.Table.Cards
              |> List.map fst
              |> List.map (CardArgs.OfState'Table t)
              |> List.map cardComponent }

let private tableComponent =
    React.functionComponent (fun (a: TableArgs) -> a.Cards)

let private roomComponent =
    React.functionComponent (fun (t: TotalState) ->
        React.useEffectOnce (fun () -> printfn "Room id:\n%A" t.ID)
        [ headBarComponent (HeadBarArgs.OfState t)
          playerListComponent (PlayerListArgs.OfState t)
          turnButtonComponent (TurnButtonArgs.OfState t)
          exitButtonComponent {| Dispatch = t.Dispatch |}
          settingsComponent ()
          handComponent (HandArgs.OfState t)
          tableComponent (TableArgs.OfState t) ])

let renderRoom (id: string) (state: GameState) (dispatch: Msg -> unit) =
    roomComponent
        { State = state
          ID = id
          Dispatch = dispatch }
