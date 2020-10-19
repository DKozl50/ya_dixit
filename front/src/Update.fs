module Update

open Elmish
open Model
open Util

let private makeMove (state: RoomState) =
    { state with
          Client =
              { state.Client with
                    MoveAvailable = false } }

let private selectCard (id: CardID option) (state: RoomState) =
    { state with
          Hand = { state.Hand with SelectedCard = id } }

let private mapRoomState (f: RoomState -> RoomState) (state: ModelState) =
    let page' =
        match state.Page with
        | Page.GameRoom s -> Page.GameRoom ^ f s
        | other -> other

    { state with Page = page' }

let private userUpdate (msg: UserMessage) (state: ModelState) =
    let state' =
        match msg with
        | UserMessage.JoinRoom _ -> { state with Page = Page.Connecting }
        | UserMessage.LeaveRoom -> { state with Page = Page.Lobby }
        | UserMessage.SelectCard id -> mapRoomState (selectCard ^ Some id) state
        | UserMessage.TellStory _
        | UserMessage.EndTurn -> mapRoomState makeMove state
        | UserMessage.UpdateInfo _ -> state

    state', Socket.sendObjectCmd msg

let private serverUpdate (msg: ServerMessage) (state: ModelState) =
    match msg with
    | ServerMessage.RoomUpdate s -> { state with Page = Page.GameRoom s }, Cmd.none
    | ServerMessage.FailConnect -> { state with Page = Page.Lobby }, Cmd.none
    | ServerMessage.AviUpload s ->
        state,
        Cmd.ofMsg
        ^ Msg.InternalMsg
        ^ InternalMessage.UpdateStorage { Name = None; Avi = Some s }

let private internalUpdate (msg: InternalMessage) (state: ModelState) =
    match msg with
    | InternalMessage.UpdateStorage s ->
        { state with Storage = s },
        Cmd.batch [ Storage.updateStorageCmd s
                    Cmd.ofMsg ^ Msg.UserMsg ^ UserMessage.UpdateInfo s ]

let update (msg: Msg) (state: ModelState) =
    let state', cmd =
        match msg with
        | Msg.UserMsg msg -> userUpdate msg state
        | Msg.ServerMsg msg -> serverUpdate msg state
        | Msg.InternalMsg msg -> internalUpdate msg state

    let cmd' =
        Cmd.batch [ cmd
                    Url.cmdUpdateURL state'.Page ]

    state', cmd'
