module Update

open Elmish
open Model

let cellOfSide =
    function
    | PlayerSide.Cross -> GameCell.Cross
    | PlayerSide.Nought -> GameCell.Nought

let switchTurn =
    function
    | GameProgress.CrossTurn -> GameProgress.NoughtTurn
    | GameProgress.NoughtTurn -> GameProgress.CrossTurn
    | x -> x

let inline listUpdate (i: int) (x: 'T) (li: 'T list) =
    let a = List.toArray li
    a.[i] <- x
    Array.toList a

let inline konst x y = x

let makeMove (x: int) (gs: GameState) =
    let field' =
        gs.Field |> listUpdate x (cellOfSide gs.Side)

    { gs with
          Field = field'
          Progress = switchTurn gs.Progress }

let updateGameState (updater: GameState -> GameState) (state: ModelState) =
    match state with
    | ModelState.Room (id, s) -> ModelState.Room(id, updater s)
    | _ -> state

let userUpdate (msg: UserMessage) (state: ModelState) =
    Socket.sendObject msg
    match msg with
    | UserMessage.CreateRoom -> ModelState.Connecting, Cmd.none
    | UserMessage.JoinRoom id -> ModelState.Connecting, Cmd.none
    | UserMessage.LeaveRoom -> ModelState.Lobby, Cmd.none
    | UserMessage.MakeMove x -> updateGameState (makeMove x) state, Cmd.none

let serverUpdate (msg: ServerMessage) (state: ModelState) =
    match msg with
    | ServerMessage.RoomConnect (id, s) -> ModelState.Room(id, s), Cmd.none
    | ServerMessage.RoomUpdate ns -> updateGameState (konst ns) state, Cmd.none
    | ServerMessage.FailConnect -> ModelState.Lobby, Cmd.none

let update (msg: Msg) (state: ModelState) =
    match msg with
    | Msg.UserMsg msg -> userUpdate msg state
    | Msg.ServerMsg msg -> serverUpdate msg state
