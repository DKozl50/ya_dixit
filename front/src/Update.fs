module Update

open Elmish
open Model

let updateGameState (newState: GameState) (state: ModelState) =
    match state with
    | ModelState.Room (id, s) -> ModelState.Room(id, newState)
    | _ -> state

let userUpdate (msg: UserMessage) (state: ModelState) =
    Socket.sendObject msg
    match msg with
    | UserMessage.CreateRoom -> ModelState.Connecting, Cmd.none
    | UserMessage.JoinRoom id -> ModelState.Connecting, Cmd.none
    | UserMessage.LeaveRoom -> ModelState.Lobby, Cmd.none
    | _ -> state, Cmd.none

let serverUpdate (msg: ServerMessage) (state: ModelState) =
    match msg with
    | ServerMessage.RoomConnect (id, s) -> ModelState.Room(id, s), Cmd.none
    | ServerMessage.RoomUpdate ns -> updateGameState ns state, Cmd.none
    | ServerMessage.FailConnect -> ModelState.Lobby, Cmd.none

let update (msg: Msg) (state: ModelState) =
    match msg with
    | Msg.UserMsg msg -> userUpdate msg state
    | Msg.ServerMsg msg -> serverUpdate msg state
