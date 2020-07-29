module Model

[<RequireQualifiedAccess>]
type PlayerSide =
    | Cross
    | Nought

[<RequireQualifiedAccess>]
type GameCell =
    | Empty
    | Cross
    | Nought

[<RequireQualifiedAccess>]
type GameProgress =
    | Waiting
    | CrossTurn
    | NoughtTurn
    | CrossWin
    | NoughtWin
    | Draw

type GameState =
    { Progress: GameProgress
      Field: GameCell list // Exactly 9 elements
      Side: PlayerSide }

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
    | MakeMove of cell: int

[<RequireQualifiedAccess>]
type ServerMessage =
    | FailConnect
    | RoomConnect of id: string * state: GameState
    | RoomUpdate of newState: GameState

[<RequireQualifiedAccess>]
type Msg =
    | UserMsg of UserMessage
    | ServerMsg of ServerMessage
