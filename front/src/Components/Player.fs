module Components.Player

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private playerAviPlaceholder =
    "https://api.adorable.io/avatars/128/SphericalPotatoInVacuum.png"



let private playerComponent' (p: Player) =
    Html.div [ prop.className "user d-flex align-items-center"
               prop.children [ Bulma.image [ image.is64x64 ++ spacing.mx3 ++ spacing.my3
                                             prop.children
                                                 [ Html.img [ prop.className "active-user" ++ image.isRounded
                                                              prop.src playerAviPlaceholder ] ] ]
                               Bulma.title.h1 [ prop.className "username"
                                                ++ title.is6
                                                ++ spacing.ml3
                                                ++ spacing.mr5
                                                prop.text p.Name ]
                               Bulma.title.h1 [ prop.className "align-self-right" ++ title.is6
                                                prop.text p.Score ] ] ]

let playerComponent = React.functionComponent playerComponent'
