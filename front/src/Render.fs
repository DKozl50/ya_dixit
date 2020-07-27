module Render

open Feliz

let render (state: Model.Model) (dispatch: Model.Msg -> unit) =
    Html.div [
        prop.text "Noughts and crosses"
    ]
