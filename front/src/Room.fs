module Render.Room

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

open Components.Card
open Components.Player
open Components.TurnButton
open Components.Hand
open Components.Settings
open Components.PlayerList
open Components.HeadBar
open Components.ExitButton
open Components.Table

type TotalState =
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

    member this.DealtCard =
        this.Table.Cards
        |> List.tryFind (function
            | _, Some x when x.Owner = this.Client -> true
            | _ -> false)
        |> Option.map fst

    member this.CorrectCard =
        this.Table.Cards
        |> List.tryFind (function
            | _, Some x when x.Owner.Role = PlayerRole.Storyteller -> true
            | _ -> false)
        |> Option.map fst

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

type CardArgs with
    static member OfState'Hand (t: TotalState) (id: CardID) =
        { ID = id
          Chosen = t.Hand.SelectedCard |> Option.contains id
          Correct = false
          Selectable = t.HandSelectable
          Dispatch = t.Dispatch
          OptionalInfo = None }

    static member OfState'Table (t: TotalState) (id: CardID) =
        { ID = id
          Chosen = t.Hand.SelectedCard |> Option.contains id
          Correct = t.CorrectCard |> Option.contains id
          Selectable =
              t.TableSelectable
              && not (Option.contains id t.DealtCard)
          Dispatch = t.Dispatch
          OptionalInfo =
              t.Table.Cards
              |> List.tryFind (fst >> ((=) id))
              |> Option.bind snd }

type TurnButtonArgs with
    static member OfState(t: TotalState) =
        { Highlighted = t.EndTurnClickable && t.IsListener
          Dispatch = t.Dispatch }

type HandArgs with
    static member OfState(t: TotalState): HandArgs =
        { Cards =
              t.Hand.Cards
              |> List.map (CardArgs.OfState'Hand t)
              |> List.map cardComponent }

type PlayerListArgs with
    static member OfState(t: TotalState) =
        { Players =
              (t.Client :: t.Opponents)
              |> List.map playerCompoment }


type HeadBarArgs with
    static member OfState(t: TotalState) =
        { Phase = t.Phase
          Storyteller = t.Storyteller
          ActiveInput =
              t.IsStoryteller
              && t.Phase = GamePhase.Storytelling
          ActiveButton = t.EndTurnClickable
          Story = t.Table.Story
          Dispatch = t.Dispatch }

type TableArgs with
    static member OfState(t: TotalState): TableArgs =
        { Cards =
              t.Table.Cards
              |> List.map fst
              |> List.map (CardArgs.OfState'Table t)
              |> List.map cardComponent }

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
