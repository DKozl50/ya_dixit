module Model

[<RequireQualifiedAccess>]
type PlayerRole =
    | Storyteller
    | Listener
    | None

type Player =
    { Name: string
      Role: PlayerRole
      Score: int
      MadeMove: bool }

[<RequireQualifiedAccess>]
type GamePhase =
    | Waiting
    | Storytelling
    | Matching
    | Guessing
    | Interlude
    | Victory of Player

type Hand = { Cards: int list; SelectedCard: int }

type Table =
    { Cards: (int * Player option) list
      Story: string }

type GameState =
    { Players: Player list // the client player object is always on top
      Hand: Hand
      Table: Table }

[<RequireQualifiedAccess>]
type ModelState =
    | Lobby
    | Connecting
    | Room of id: string * state: GameState

[<RequireQualifiedAccess>]
type UserMessage =
    | CreateRoom
    | JoinRoom of id: string
    | LeaveRoom
    | TellStory of cardID: int * story: string
    | DealCard of cardID: int
    | GuessCard of cardID: int

[<RequireQualifiedAccess>]
type ServerMessage =
    | FailConnect
    | RoomConnect of id: string * state: GameState
    | RoomUpdate of newState: GameState

[<RequireQualifiedAccess>]
type Msg =
    | UserMsg of UserMessage
    | ServerMsg of ServerMessage
