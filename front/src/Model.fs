module Model

[<RequireQualifiedAccess>]
type PlayerSide = Cross | Nought

[<RequireQualifiedAccess>]
type GameCell = Empty | Cross | Nought

[<RequireQualifiedAccess>]
type GameState = Waiting | CrossTurn | NoughtTurn | CrossWin | NoughtWin

type Game = {
    State: GameState
    Field: GameCell list
    Side: PlayerSide
}

type Model = 
    | Lobby
    | Connecting
    | Error of errorText: string
    | Room of id: string * game: Game

type UserMessage =
    | CreateRoom
    | JoinRoom of id: string
    | LeaveRoom
    | MakeMove of cell: int

type ServerMessage =
    | RoomConnect of id: string * game: Game
    | RoomUpdate of game: Game

type InternalMessage =
    | PseudoUpdate of game: Game

type Msg = 
    | UserMsg of UserMessage
    | ServerMsg of ServerMessage
    | InternalMsg of InternalMessage
