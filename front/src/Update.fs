module Update

open Elmish
open Model

let cellOfSide = function
    | PlayerSide.Cross -> GameCell.Cross
    | PlayerSide.Nought -> GameCell.Nought

let inline listUpdate (i: int) (x: 'T) (li: 'T list) = 
    let a = List.toArray li
    a.[i] <- x
    Array.toList a

let inline konst x y = x

let gameMoveUpdater (x: int) (gs: GameState) =
    let field' = gs.Field |> listUpdate x (cellOfSide gs.Side)
    { gs with Field = field'}

let updateGameState (state: ModelState) (updater: GameState -> GameState) =
    match state with
    | ModelState.Room(id, s) -> ModelState.Room(id, updater s)
    | _ -> state

let internalUpdate (msg: InternalMessage) (state: ModelState) =
    match msg with
    | InternalMessage.PseudoUpdate u -> updateGameState state u, Cmd.none

let userUpdate (msg: UserMessage) (state: ModelState) =
    match msg with
    | UserMessage.CreateRoom -> Socket.sendJson ""; ModelState.Connecting, Cmd.none
    | UserMessage.JoinRoom id -> Socket.sendJson ""; ModelState.Connecting, Cmd.none
    | UserMessage.LeaveRoom -> Socket.sendJson ""; ModelState.Lobby, Cmd.none
    | UserMessage.MakeMove x -> Socket.sendJson ""; state, Cmd.ofMsg (gameMoveUpdater x |> InternalMessage.PseudoUpdate)

let serverUpdate (msg: ServerMessage) (state: ModelState) = 
    match msg with
    | ServerMessage.RoomConnect(id, s) -> ModelState.Room(id, s), Cmd.none
    | ServerMessage.RoomUpdate ns -> updateGameState state (konst ns), Cmd.none

let update (msg: Msg) (state: ModelState) = 
    match msg with
    | InternalMsg msg -> internalUpdate msg state
    | UserMsg msg -> userUpdate msg state
    | ServerMsg msg -> serverUpdate msg state