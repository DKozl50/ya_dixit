module Components.Player

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private playerSvg (moveAvailable: bool) =
    Html.svg [ prop.style [ style.width (length.px 64)
                            style.height (length.px 64)
                            style.position.absolute
                            style.top 0 ]
               prop.children
                   [ Html.circle [ prop.cx 32
                                   prop.cy 32
                                   prop.r 30
                                   prop.custom ("fill", "transparent")
                                   prop.strokeWidth 4
                                   prop.stroke (if moveAvailable then "#33EE11" else "transparent") ] ] ]

let private playerAviPlaceholder =
    "https://bulma.io/images/placeholders/128x128.png"

let private playerCompoment' (p: Player) =
    Html.figure [ prop.className "image"
                  ++ spacing.my3
                  ++ image.is64x64
                  prop.children [ playerSvg p.MoveAvailable
                                  Html.img [ image.isRounded
                                             prop.src playerAviPlaceholder ] ] ]

let playerCompoment = React.functionComponent playerCompoment'
