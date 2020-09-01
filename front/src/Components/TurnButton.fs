module Components.TurnButton

open Feliz
open Model

type TurnButtonArgs =
    { Highlighted: bool
      Dispatch: Msg -> unit }

let private turnButtonComponent' (a: TurnButtonArgs) =
    Html.a [ prop.classes [ "end-turn-btn"
                            if a.Highlighted then "green" else "inactive" ]
             prop.text "Закончить ход"
             if a.Highlighted
             then prop.onClick (fun _ -> UserMessage.EndTurn |> Msg.UserMsg |> a.Dispatch) ]

let turnButtonComponent =
    React.functionComponent turnButtonComponent'
