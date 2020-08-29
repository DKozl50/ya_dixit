module Components.Card

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private imgSrcByID (id: CardID) = "/img/" + id + ".jpg"

let private playerAviPlaceholder =
    "https://api.adorable.io/avatars/128/SphericalPotatoInVacuum.png"

type CardArgs =
    { ID: CardID
      Chosen: bool
      Correct: bool
      Selectable: bool
      OptionalInfo: CardOptionalInfo option
      Dispatch: Msg -> unit }

let private blob (_: Player) =
    Html.figure [ prop.className "image"
                  ++ spacing.mx1
                  ++ spacing.my1
                  prop.children
                      [ Html.img [ image.isRounded
                                   prop.src playerAviPlaceholder ] ] ]

let private author (p: Player) =
    Html.div [ prop.className "author"
               ++ spacing.px1
               ++ spacing.py1
               prop.children [ blob p ] ]

let private voters (p: Player list) =
    Html.div [ prop.className "voters d-flex px-1 py-1 flex-wrap"
               prop.children (p |> List.map blob) ]

let private cardContent (id: CardID) =
    Bulma.cardContent [ Html.img [ prop.src (imgSrcByID id) ] ]

let private cardComponent' (a: CardArgs) =
    Bulma.card [ prop.classes [ "game-card"
                                if a.Chosen then "chosen"
                                if a.Correct then "correct" ]
                 spacing.mx3
                 prop.children [ cardContent a.ID
                                 if a.OptionalInfo.IsSome then
                                     author a.OptionalInfo.Value.Owner
                                     voters a.OptionalInfo.Value.Voters ]
                 if a.Selectable
                 then prop.onClick (fun _ -> a.Dispatch(Msg.UserMsg(UserMessage.SelectCard a.ID))) ]

let cardComponent = React.functionComponent cardComponent'
