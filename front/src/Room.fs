module Room

open Feliz
open Model
open GameLogic
open RoomElements

let private roomComponent =
    React.functionComponent (fun (s: RoomState) ->
        React.useEffectOnce (fun () -> printfn "Room id:\n%A" s.ID)
        [ headBar s.HeadBarArgs
          playerList s.PlayerListArgs
          turnButton s.TurnBtnClickable
          exitButton
          settingsComponent s.Client
          hand s.HandArgs
          tableComponent s.TableArgs ])

let renderRoom = roomComponent
