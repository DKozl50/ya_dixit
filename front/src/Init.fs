module Init

open Elmish
open Model

let initModel () = ModelState.Lobby, Cmd.none
