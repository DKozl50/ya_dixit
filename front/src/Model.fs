module Model

[<RequireQualifiedAccess>]
type PlayerSide = Cross | Nought

[<RequireQualifiedAccess>]
type GameCell = Empty | Cross | Nought

[<RequireQualifiedAccess>]
type GameProgress = Waiting | CrossTurn | NoughtTurn | CrossWin | NoughtWin

type GameState = {
    Progress: GameProgress
    Field: GameCell list    // Exactly 9 elements
    Side: PlayerSide
}

[<RequireQualifiedAccess>]
type ModelState = 
    | Lobby
    | Connecting
    | Error of errorText: string
    | Room of id: string * state: GameState

[<RequireQualifiedAccess>]
type UserMessage =
    | CreateRoom
    | JoinRoom of id: string
    | LeaveRoom
    | MakeMove of cell: int

[<RequireQualifiedAccess>]
type ServerMessage =
    | RoomConnect of id: string * state: GameState
    | RoomUpdate of newState: GameState

[<RequireQualifiedAccess>]
type InternalMessage =
    | PseudoUpdate of updater: (GameState -> GameState)

type Msg = 
    | UserMsg of UserMessage
    | ServerMsg of ServerMessage
    | InternalMsg of InternalMessage
