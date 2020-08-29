module Components.Hand

open Feliz
open Feliz.Bulma

type HandArgs =
    { Cards: Fable.React.ReactElement list }
    

let private handComponent' (a: HandArgs) =
    Bulma.card [ prop.className "hand"
                 prop.children
                     [ Bulma.cardContent [ spacing.px3
                                           prop.children
                                               [ Html.div [ prop.className
                                                                "d-flex justify-content-between align-items-center"
                                                            prop.children a.Cards ] ] ] ] ]

let handComponent = React.functionComponent handComponent'
