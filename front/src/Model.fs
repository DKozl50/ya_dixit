module Model

[<RequireQualifiedAccess>]
type PlayerRole =
    | Storyteller
    | Listener
    | Spectator

type Player =
    { Name: string
      Role: PlayerRole
      Score: int
      MoveAvailable: bool }

[<RequireQualifiedAccess>]
type GamePhase =
    | Waiting
    | Storytelling
    | Matching
    | Guessing
    | Interlude
    | Victory of Player

type CardID = string

type CardOptionalInfo = { Owner: Player; Voters: Player list }

type Hand =
    { Cards: CardID list
      SelectedCard: CardID option }

type Table =
    { Cards: (CardID * CardOptionalInfo option) list
      Story: string option }

type GameState =
    { Client: Player
      Opponents: Player list
      Hand: Hand
      Table: Table
      Phase: GamePhase }

[<RequireQualifiedAccess>]
type ModelState =
    | Lobby
    | Connecting
    | Room of id: string * state: GameState

[<RequireQualifiedAccess>]
type UserMessage =
    | CreateRoom of nickname: string
    | JoinRoom of id: string * nickname: string
    | LeaveRoom
    | SelectCard of id: CardID
    | TellStory of story: string
    | EndTurn

[<RequireQualifiedAccess>]
type ServerMessage =
    | FailConnect
    | RoomConnect of id: string * state: GameState
    | RoomUpdate of newState: GameState

[<RequireQualifiedAccess>]
type Msg =
    | UserMsg of UserMessage
    | ServerMsg of ServerMessage
