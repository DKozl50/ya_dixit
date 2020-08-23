module Components.Settings

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private settingsComponent' () =
    Bulma.card [ prop.className "settings-button"
                 prop.children
                     [ Bulma.cardContent [ prop.className "fullheight"
                                           prop.children
                                               [ Bulma.icon [ icon.isMedium
                                                              prop.children
                                                                  [ Html.i [ prop.className "fas fa-cog fa-2x" ] ] ] ] ] ] ]

let settingsComponent =
    React.functionComponent settingsComponent'
