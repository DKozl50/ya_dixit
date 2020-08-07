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
    | _ ->
        Printf.eprintfn "Warning: incorrect message recieved"
        state

let private userUpdate (msg: UserMessage) (state: ModelState) =
    Socket.sendObject msg
    match msg with
    | UserMessage.CreateRoom _ -> ModelState.Connecting, Cmd.none
    | UserMessage.JoinRoom _ -> ModelState.Connecting, Cmd.none
    | UserMessage.LeaveRoom -> ModelState.Lobby, Cmd.none
    | UserMessage.SelectCard id -> mapGameState (selectCard (Some id)) state, Cmd.none
    | _ -> mapGameState makeMove state, Cmd.none

let private serverUpdate (msg: ServerMessage) (state: ModelState) =
    match msg with
    | ServerMessage.RoomConnect (id, s) -> ModelState.Room(id, s), Cmd.none
    | ServerMessage.RoomUpdate ns -> mapGameState (fun _ -> ns) state, Cmd.none
    | ServerMessage.FailConnect -> ModelState.Lobby, Cmd.none

let update (msg: Msg) (state: ModelState) =
    match msg with
    | Msg.UserMsg msg -> userUpdate msg state
    | Msg.ServerMsg msg -> serverUpdate msg state
