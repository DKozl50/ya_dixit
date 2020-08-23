module Components.Card

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private imgSrcByID (id: CardID) = "/img/" + id + ".jpg"

type CardArgs =
    { ID: CardID
      Highlighted: bool
      Selectable: bool
      Dispatch: Msg -> unit }
    

let private cardComponent' (a: CardArgs) =
    Bulma.card [ prop.classes [ "game-card"
                                if a.Highlighted then "chosen" ]
                 spacing.mx3
                 prop.children [ Html.img [ prop.src (imgSrcByID a.ID) ] ]
                 if a.Selectable
                 then prop.onClick (fun _ -> a.Dispatch(Msg.UserMsg(UserMessage.SelectCard a.ID))) ]

let cardComponent = React.functionComponent cardComponent'
