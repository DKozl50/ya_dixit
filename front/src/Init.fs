module Init

open Elmish

let initModel () = Unchecked.defaultof<Model.Model>, Cmd.none
