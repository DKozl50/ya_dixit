module Model

[<RequireQualifiedAccess>]
type PlayerRole =
    | Storyteller
    | Listener

type Player =
    { Name: string
      Avi: string
      Role: PlayerRole
      Score: int
      MoveAvailable: bool }

type CardID = string

type GameID = string

type CardInfo =
    { ID: CardID
      Owner: Player option
      Voters: Player list }

type Hand =
    { Cards: CardInfo list
      SelectedCard: CardID option }

type Table =
    { Cards: CardInfo list
      Story: string option }

[<RequireQualifiedAccess>]
type GamePhase =
    | Waiting
    | Storytelling
    | Matching
    | Guessing
    | Interlude
    | Victory

type RoomState =
    { Client: Player
      Opponents: Player list
      Hand: Hand
      Table: Table
      Phase: GamePhase
      ID: GameID }

[<RequireQualifiedAccess>]
type Page =
    | Lobby
    | Connecting
    | GameRoom of RoomState

type ClientData =
    { Name: string option
      Avi: string option }

type ModelState = { Page: Page; Storage: ClientData }

[<RequireQualifiedAccess>]
type UserMessage =
    | UpdateInfo of ClientData
    | JoinRoom of GameID
    | LeaveRoom
    | SelectCard of CardID
    | TellStory of string
    | EndTurn

[<RequireQualifiedAccess>]
type ServerMessage =
    | FailConnect
    | RoomUpdate of RoomState
    | AviUpload of string

[<RequireQualifiedAccess>]
type InternalMessage = UpdateStorage of ClientData

[<RequireQualifiedAccess>]
type Msg =
    | UserMsg of UserMessage
    | ServerMsg of ServerMessage
    | InternalMsg of InternalMessage
