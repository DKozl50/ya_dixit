module Render

open Feliz

let render (state: Model.ModelState) (dispatch: Model.Msg -> unit) =
    Html.div [ prop.text "Noughts and crosses" ]
