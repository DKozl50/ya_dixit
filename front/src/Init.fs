module Init

open Elmish
open Model

let _room = {
    Field = [ for i in 0..8 -> GameCell.Empty ]
    Progress = GameProgress.CrossTurn
    Side = PlayerSide.Cross
}

let initModel () = ModelState.Room("вставьте id", _room), Cmd.none
