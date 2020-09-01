module GameLogic

open Model
open RoomElements

type RoomState with
    member this.SelectedCard = this.Hand.SelectedCard
    member this.MoveAvailable = this.Client.MoveAvailable
    member this.HasSelectedCard = this.SelectedCard.IsSome

    member this.DealtCard =
        this.Table.Cards
        |> List.tryFind (fun x -> x.Owner = Some this.Client)
        |> Option.map (fun x -> x.ID)

    member this.CorrectCard =
        this.Table.Cards
        |> List.tryFind (fun x ->
            x.Owner.IsSome
            && x.Owner.Value.Role = PlayerRole.Storyteller)
        |> Option.map (fun x -> x.ID)

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

    member this.EndTurnReady =
        this.MoveAvailable && this.HasSelectedCard

    member this.Storyteller =
        if this.IsStoryteller then
            this.Client
        else
            List.tryFind (fun p -> p.Role = PlayerRole.Storyteller) this.Opponents
            |> Option.defaultValue this.Client

    member this.CardArgs_Hand(i: CardInfo) =
        { Info = i
          Chosen = this.SelectedCard |> Option.contains i.ID
          Correct = this.CorrectCard |> Option.contains i.ID
          Selectable = this.HandSelectable }

    member this.CardArgs_Table(i: CardInfo) =
        { Info = i
          Chosen = this.SelectedCard |> Option.contains i.ID
          Correct = this.CorrectCard |> Option.contains i.ID
          Selectable =
              this.TableSelectable
              && not (this.DealtCard |> Option.contains i.ID) }

    member this.TurnBtnClickable = this.EndTurnReady && this.IsListener

    member this.HandArgs =
        this.Hand.Cards
        |> List.map this.CardArgs_Hand
        |> List.map card

    member this.TableArgs =
        { Cards =
              this.Hand.Cards
              |> List.map this.CardArgs_Hand
              |> List.map card }

    member this.PlayerListArgs =
        this.Client :: this.Opponents |> List.map player

    member this.HeadBarArgs =
        { Phase = this.Phase
          Storyteller = this.Storyteller
          ActiveInput =
              this.IsStoryteller
              && this.Phase = GamePhase.Storytelling
          ActiveButton = this.EndTurnReady
          Story = this.Table.Story }
