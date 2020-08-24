module Update

open Elmish
open Model

let private makeMove (state: GameState) =
    { state with
          Client =
              { state.Client with
                    MoveAvailable = false } }

let private selectCard (id: CardID option) (state: GameState) =
    { state with
          Hand = { state.Hand with SelectedCard = id } }

let private mapGameState (f: GameState -> GameState) (state: ModelState) =
    match state with
    | ModelState.Room (id, s) -> ModelState.Room(id, f s)
    | _ -> state

let private userUpdate (msg: UserMessage) (state: ModelState) =
    let state' =
        match msg with
        | UserMessage.CreateRoom _ -> ModelState.Connecting
        | UserMessage.JoinRoom _ -> ModelState.Connecting
        | UserMessage.LeaveRoom -> ModelState.Lobby
        | UserMessage.SelectCard id -> mapGameState (selectCard (Some id)) state
        | _ -> mapGameState makeMove state

    state', Socket.sendObjectCmd msg

let private serverUpdate (msg: ServerMessage) (state: ModelState) =
    match msg with
    | ServerMessage.RoomConnect (id, s) -> ModelState.Room(id, s), Cmd.none
    | ServerMessage.RoomUpdate ns -> mapGameState (fun _ -> ns) state, Cmd.none
    | ServerMessage.FailConnect -> ModelState.Lobby, Cmd.none

let update (msg: Msg) (state: ModelState) =
    match msg with
    | Msg.UserMsg msg -> userUpdate msg state
    | Msg.ServerMsg msg -> serverUpdate msg state
