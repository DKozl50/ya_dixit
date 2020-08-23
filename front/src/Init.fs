module Init

open Elmish
open Model

let examplePlayer = {
    Name = "Саша <3"
    Role = PlayerRole.Listener
    Score = 0
    MoveAvailable = false
}

let exampleOptionalCardInfo = {
    Owner = examplePlayer
    Voters = [ examplePlayer ; examplePlayer ]
}

let exampleHand = {
    Cards = [ "linal"; "anal"; "karnaval"]
    SelectedCard = Some "linal"
}

let exampleTable = {
    Cards = [ "nol", None; "odin", Some exampleOptionalCardInfo ]
    Story = Some "kollokvium"
}

let exampleGameState = {
    Client = examplePlayer
    Opponents = []
    Hand = exampleHand
    Table = exampleTable
    Phase = GamePhase.Victory
}

let initModel () = ModelState.Room("id", exampleGameState) , Cmd.none
